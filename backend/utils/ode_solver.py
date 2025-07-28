import numpy as np
from scipy.integrate import odeint
from models.diabetes_model import PatientData, SimulationResult, ExtendedSimulationResult, MealSchedule
import math
from typing import Optional, Tuple

class DiabetesODESolver:
    def __init__(self, patient_data: PatientData):
        self.patient_data = patient_data
        self.params = self._calculate_parameters()
        
    def _calculate_parameters(self):
        """Calculate model parameters based on patient data"""
        # Base parameters from Table 2 in the paper
        params = {
            # Half-saturation constants (g/cm³)
            'K_L': 1.7e-14,      # GLP-1
            'K_U2': 9.45e-6,     # GLUT-2
            'K_U4': 2.78e-6,     # GLUT-4
            'K_I': 2e-13,        # Insulin
            'K_hat_L': 1.7e-14,  # GLP-1 inhibitory saturation
            'K_hat_O': 1.36e-6,  # Oleic acid inhibitory saturation
            
            # Activation rates (d⁻¹)
            'lambda_tilde_A': 0.35,      # α-cells
            'lambda_tilde_B': 1.745e9,   # β-cells
            'gamma_L': 1.98e-13,         # GLP-1 secretion
            'lambda_IB': 1.26e-8,        # Insulin by β-cells
            'lambda_U4_I': 4.17e7,       # GLUT-4 by insulin
            'lambda_U2C': 6.6e10,        # GLUT-2 by glucagon
            'lambda_CA': 1.65e-11,       # Glucagon by α-cells
            'gamma_G': 0.017,            # Glucose secretion
            'gamma_G_star': 11.1,        # Glucose elimination
            'gamma_O': 1.46e-4,          # Oleic acid
            'gamma_P': 1.83e-6,          # Palmitic acid
            'gamma_P_hat': 5.72e-5,      # Obesity palmitic acid
            
            # Transport rates (d⁻¹)
            'lambda_GU4': 1.548,         # Glucose by GLUT-4
            'lambda_G_star_U2': 4.644,   # Liver glucose by GLUT-2
            'lambda_T_alpha': 1.19e-9,   # TNF-α normal
            'lambda_T_alpha_P': 3.26e-4, # TNF-α by palmitic
            
            # Decay rates (d⁻¹)
            'mu_A': 8.32,         # α-cells
            'mu_B': 8.32,         # β-cells
            'mu_LB': 251,         # GLP-1 by β-cells
            'mu_LA': 251,         # GLP-1 by α-cells
            'mu_I': 198.04,       # Insulin
            'mu_U4': 1.85,        # GLUT-4
            'mu_U2': 4.62,        # GLUT-2
            'mu_C': 166.22,       # Glucagon
            'mu_T_alpha': 199,    # TNF-α
            'mu_O': 13.68,        # Oleic acid
            'mu_P': 12,           # Palmitic acid
            'mu_IG': 6e5,         # Insulin by glucose
            
            # Other parameters
            'gamma_1': 1e-14,     # Glucagon blocking
            'gamma_2': 1.2e-14,   # Glucagon inducing
            'xi_1': 1e12,         # β-cell deactivation by glucose
            'xi_2': 1e12,         # β-cell deactivation by palmitic
            'xi_3': 1e-2,         # Glucose switch level (inhibition)
            'xi_4': 1e-4,         # Glucose switch level (activation)
            'eta_T_alpha': 1e10,  # TNF-α inhibition of GLUT-4
            'I_hypo': 8e-14,      # Hypoglycemia insulin level
            'L_0': 1.7e-14,       # GLP-1 threshold
            
            # Drug effect parameters
            'K_D': 1e-7,          # Drug half-saturation
            'K_hat_D': 1e-7,      # Drug inhibitory saturation
        }
        
        # Adjust parameters based on patient characteristics
        height_m = self.patient_data.height / 100
        bmi = self.patient_data.weight / (height_m ** 2)
        
        # Obesity factor affects palmitic acid release
        if bmi >= 30:  # Obese
            params['obesity_factor'] = 4.0
        elif bmi >= 25:  # Overweight
            params['obesity_factor'] = 2.0
        else:  # Normal
            params['obesity_factor'] = 1.0
            
        # Age factor affects β-cell function
        age_factor = max(0.5, 1.0 - (self.patient_data.age - 20) * 0.005)
        params['lambda_tilde_B'] *= age_factor
        
        return params
    
    def F(self, t: float, t0: float, t1: float) -> float:
        """Food intake function from equation (2.1)"""
        return 1.0 if t0 <= t <= t1 else 0.0
    
    def H(self, x: float) -> float:
        """Heaviside step function"""
        return 1.0 if x > 0 else 0.0
    
    def get_meal_factor(self, t: float, meal_schedule: Optional[MealSchedule] = None) -> Tuple[float, float, float, float]:
        """Get food intake factors at time t based on meal schedule"""
        if meal_schedule is None:
            # Default: meals at 0, 6, 12, 18 hours
            meal_times = [0, 6, 12, 18]
            meal_active = any(self.F(t, mt, mt + 1) for mt in meal_times if mt <= 24)
            if meal_active:
                return 1.0, 1.0, 1.0, 1.0  # All factors = 1
            else:
                return 0.0, 0.0, 0.0, 0.0
        
        # Check each meal period
        factors = [0.0, 0.0, 0.0, 0.0]  # [general, glucose, oleic, palmitic]
        
        # Breakfast
        if self.F(t, meal_schedule.breakfast_time, meal_schedule.breakfast_time + 1):
            factor = meal_schedule.breakfast_factor
            factors = [factor] * 4
            
        # Lunch  
        elif self.F(t, meal_schedule.lunch_time, meal_schedule.lunch_time + 1):
            factor = meal_schedule.lunch_factor
            factors = [factor] * 4
            
        # Dinner
        elif self.F(t, meal_schedule.dinner_time, meal_schedule.dinner_time + 1):
            factor = meal_schedule.dinner_factor
            factors = [factor] * 4
            
        return tuple(factors)
    
    def ode_system(self, y, t, food_factor=1.0, palmitic_factor=1.0, drug_dose=0.0, 
                   meal_schedule: Optional[MealSchedule] = None):
        """
        Complete ODE system from the paper (equations 2.2-2.12)
        Variables: [L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha]
        """
        L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha = y
        
        # Get meal-specific factors
        meal_f, glucose_f, oleic_f, palmitic_f = self.get_meal_factor(t, meal_schedule)
        
        # Apply global food factor
        meal_f *= food_factor
        glucose_f *= food_factor
        oleic_f *= food_factor
        palmitic_f *= food_factor
        
        # Equation 2.2: GLP-1 (L)
        lambda_L = self.params['gamma_L'] * meal_f
        dL_dt = lambda_L - self.params['mu_LB'] * B * L - self.params['mu_LA'] * A * L
        
        # Enhanced GLP-1 by drug (GLP-1 agonist effect)
        if drug_dose > 0:
            dL_dt += lambda_L * (drug_dose / (self.params['K_D'] + drug_dose))
        
        # Equation 2.3: β-cells (B)
        L_term = max(0, L - self.params['L_0'])
        dB_dt = (self.params['lambda_tilde_B'] * L_term / 
                (self.params['K_L'] + L_term) - 
                self.params['mu_B'] * B * (1 + self.params['xi_1'] * G + self.params['xi_2'] * P))
        
        # Equation 2.4: α-cells (A)
        I_term = max(0, self.params['I_hypo'] - I)
        dA_dt = (self.params['lambda_tilde_A'] * I_term / 
                (self.params['K_I'] + I_term) * 
                (1 / (1 + L / self.params['K_hat_L'])) - 
                self.params['mu_A'] * A)
        
        # Equation 2.5: Insulin (I)
        dI_dt = self.params['lambda_IB'] * B - self.params['mu_I'] * I - self.params['mu_IG'] * G * I
        
        # Equation 2.6: GLUT-2 (U2)
        dU2_dt = self.params['lambda_U2C'] * C - self.params['mu_U2'] * U2
        
        # Equation 2.7: GLUT-4 (U4)
        dU4_dt = (self.params['lambda_U4_I'] * I * 
                 (1 / (1 + self.params['eta_T_alpha'] * T_alpha)) - 
                 self.params['mu_U4'] * U4)
        
        # Equation 2.8: Glucagon (C)
        G_high_term = self.H(G - self.params['xi_4'])
        G_low_term = self.H(self.params['xi_3'] - G)
        dC_dt = (self.params['lambda_CA'] * A / 
                ((1 + self.params['gamma_1'] * G_high_term * L) * 
                 (1 + self.params['gamma_2'] * G_low_term * L)) - 
                self.params['mu_C'] * C)
        
        # Equation 2.9: Blood glucose (G)
        lambda_G = self.params['gamma_G'] * glucose_f
        
        # Glucose elimination in first 2 hours after meal
        lambda_G_star = 0
        for meal_time in [0, 6, 12, 18]:
            if meal_time + 1 <= t <= meal_time + 3:
                lambda_G_star = self.params['gamma_G_star']
                break
        
        # Reduce glucose intake if drug is present
        if drug_dose > 0:
            lambda_G = lambda_G / (1 + drug_dose / self.params['K_hat_D'])
        
        dG_dt = (lambda_G - lambda_G_star * G + 
                self.params['lambda_G_star_U2'] * G_star * U2 / (self.params['K_U2'] + U2) - 
                self.params['lambda_GU4'] * G * U4 / (self.params['K_U4'] + U4))
        
        # Equation 2.10: Stored glucose (G*)
        dG_star_dt = (lambda_G_star * G + 
                     self.params['lambda_GU4'] * G * U4 / (self.params['K_U4'] + U4) - 
                     self.params['lambda_G_star_U2'] * G_star * U2 / (self.params['K_U2'] + U2))
        
        # Equation 2.11: Oleic acid (O)
        lambda_O = self.params['gamma_O'] * oleic_f
        dO_dt = lambda_O - self.params['mu_O'] * O
        
        # Equation 2.11: Palmitic acid (P)
        lambda_P = ((self.params['gamma_P'] + 
                    palmitic_factor * self.params['gamma_P_hat'] * self.params['obesity_factor']) * 
                   palmitic_f)
        dP_dt = lambda_P - self.params['mu_P'] * P
        
        # Equation 2.12: TNF-α (T_alpha)
        dT_alpha_dt = (self.params['lambda_T_alpha'] + 
                      self.params['lambda_T_alpha_P'] * P * (1 / (1 + O / self.params['K_hat_O'])) - 
                      self.params['mu_T_alpha'] * T_alpha)
        
        return [dL_dt, dA_dt, dB_dt, dI_dt, dU2_dt, dU4_dt, dC_dt, dG_dt, dG_star_dt, dO_dt, dP_dt, dT_alpha_dt]
    
    def get_initial_conditions(self):
        """Get initial conditions based on patient data"""
        if self.patient_data.diabetes_type == "diabetic":
            # Diabetic initial conditions
            return [
                4.5e-15,   # L (GLP-1)
                10e-12,    # A (α-cells) - higher in diabetic
                5e-12,     # B (β-cells) - lower in diabetic  
                0.5e-13,   # I (insulin) - lower in diabetic
                9.45e-6,   # U2 (GLUT-2)
                1.5e-6,    # U4 (GLUT-4) - lower in diabetic
                15e-16,    # C (glucagon) - higher in diabetic
                1.3e-3,    # G (glucose) - higher in diabetic
                0.5e-3,    # G* (stored glucose)
                6.78e-7,   # O (oleic acid)
                2.4e-6,    # P (palmitic acid) - higher in diabetic
                8e-12      # T_alpha (TNF-α) - higher in diabetic
            ]
        elif self.patient_data.diabetes_type == "prediabetic":
            # Prediabetic initial conditions
            return [
                4.5e-15,   # L (GLP-1)
                8e-12,     # A (α-cells)
                7e-12,     # B (β-cells)
                0.8e-13,   # I (insulin)
                9.45e-6,   # U2 (GLUT-2)
                2.0e-6,    # U4 (GLUT-4)
                10e-16,    # C (glucagon)
                1.1e-3,    # G (glucose)
                0.4e-3,    # G* (stored glucose)
                6.78e-7,   # O (oleic acid)
                1.8e-6,    # P (palmitic acid)
                7e-12      # T_alpha (TNF-α)
            ]
        else:
            # Normal/healthy initial conditions
            return [
                4.5e-15,   # L (GLP-1)
                6e-12,     # A (α-cells)
                10e-12,    # B (β-cells)
                1.0e-13,   # I (insulin)
                9.45e-6,   # U2 (GLUT-2)
                2.78e-6,   # U4 (GLUT-4)
                5.4e-16,   # C (glucagon)
                8e-4,      # G (glucose) - normal fasting
                0.3e-3,    # G* (stored glucose)
                6.78e-7,   # O (oleic acid)
                1.22e-6,   # P (palmitic acid)
                6e-12      # T_alpha (TNF-α)
            ]
    
    def simulate(self, hours=24, food_factor=1.0, palmitic_factor=1.0, drug_dosage=0.0,
                meal_schedule: Optional[MealSchedule] = None, 
                include_all_variables=False):
        """Run the simulation and return results"""
        # Time points (hours) with 10-minute resolution
        t = np.linspace(0, hours, int(hours * 6))
        
        # Initial conditions
        y0 = self.get_initial_conditions()
        
        try:
            # Solve ODE system
            solution = odeint(
                self.ode_system, 
                y0, 
                t, 
                args=(food_factor, palmitic_factor, drug_dosage, meal_schedule),
                rtol=1e-8,
                atol=1e-10
            )
            
            # Extract variables
            L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha = solution.T
            
            # Convert to appropriate units
            glucose_mg_dl = G * 1000  # Convert to mg/dL
            insulin_pmol_l = I * 1e13  # Convert to pmol/L
            glucagon_pg_ml = C * 1e16  # Convert to pg/mL
            glp1_pmol_l = L * 1e15     # Convert to pmol/L
            
            # Calculate metrics
            avg_glucose_mg_dl = np.mean(glucose_mg_dl)
            a1c_estimate = (avg_glucose_mg_dl + 46.7) / 28.7
            glucose_std = np.std(glucose_mg_dl)
            
            # Time in range (70-140 mg/dL)
            time_in_range = np.sum((glucose_mg_dl >= 70) & (glucose_mg_dl <= 140)) / len(glucose_mg_dl) * 100
            
            # Determine diagnosis based on A1C
            if a1c_estimate < 5.7:
                diagnosis = "Normal"
            elif a1c_estimate < 6.4:
                diagnosis = "Prediabetic"
            else:
                diagnosis = "Diabetic"
            
            # Generate optimal glucose trajectory for comparison
            optimal_glucose = self._generate_optimal_glucose(t, meal_schedule)
            
            if include_all_variables:
                return ExtendedSimulationResult(
                    time_points=t.tolist(),
                    glucose=glucose_mg_dl.tolist(),
                    insulin=insulin_pmol_l.tolist(),
                    glucagon=glucagon_pg_ml.tolist(),
                    glp1=glp1_pmol_l.tolist(),
                    alpha_cells=(A * 1e12).tolist(),  # Convert to reasonable units
                    beta_cells=(B * 1e12).tolist(),
                    glut2=(U2 * 1e6).tolist(),
                    glut4=(U4 * 1e6).tolist(),
                    stored_glucose=(G_star * 1000).tolist(),  # mg/dL
                    oleic_acid=(O * 1e6).tolist(),
                    palmitic_acid=(P * 1e6).tolist(),
                    tnf_alpha=(T_alpha * 1e12).tolist(),
                    optimal_glucose=optimal_glucose,
                    a1c_estimate=round(a1c_estimate, 2),
                    diagnosis=diagnosis,
                    avg_glucose=round(avg_glucose_mg_dl, 1),
                    glucose_variability=round(glucose_std, 1),
                    time_in_range=round(time_in_range, 1)
                )
            else:
                return SimulationResult(
                    time_points=t.tolist(),
                    glucose=glucose_mg_dl.tolist(),
                    insulin=insulin_pmol_l.tolist(),
                    glucagon=glucagon_pg_ml.tolist(),
                    glp1=glp1_pmol_l.tolist(),
                    optimal_glucose=optimal_glucose,
                    a1c_estimate=round(a1c_estimate, 2),
                    diagnosis=diagnosis
                )
            
        except Exception as e:
            print(f"ODE solver error: {e}")
            raise Exception(f"Simulation failed: {str(e)}")
    
    def _generate_optimal_glucose(self, t, meal_schedule: Optional[MealSchedule] = None):
        """Generate optimal glucose trajectory for healthy individual"""
        optimal_G = []
        
        if meal_schedule:
            meal_times = [
                (meal_schedule.breakfast_time, meal_schedule.breakfast_factor),
                (meal_schedule.lunch_time, meal_schedule.lunch_factor),
                (meal_schedule.dinner_time, meal_schedule.dinner_factor)
            ]
        else:
            # Default meal times
            meal_times = [(0, 1.0), (6, 1.0), (12, 2.0), (18, 1.0)]
        
        for time in t:
            # Simulate normal glucose response to meals
            base_glucose = 85  # mg/dL baseline
            glucose_response = base_glucose
            
            for meal_time, meal_factor in meal_times:
                if time >= meal_time:
                    time_since_meal = time - meal_time
                    if time_since_meal <= 4:  # 4-hour post-meal period
                        # Gaussian-like response with peak at 1 hour
                        peak_response = 35 * meal_factor * math.exp(-0.5 * ((time_since_meal - 1) / 0.8) ** 2)
                        glucose_response += peak_response
            
            # Add some natural variation
            optimal_G.append(max(70, min(140, glucose_response)))
        
        return optimal_G