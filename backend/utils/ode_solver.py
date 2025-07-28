import numpy as np
from scipy.integrate import odeint
from models.diabetes_model import PatientData, SimulationResult, ExtendedSimulationResult, MealSchedule
import math
from typing import Optional, Tuple

class DiabetesODESolver:
    def __init__(self, patient_data: PatientData):
        self.patient_data = patient_data
        self.params = self._calculate_parameters()
        self.eps = 0.1  # Time tolerance for meal detection
        
    def _calculate_parameters(self):
        """Calculate model parameters based on patient data"""
        # Base parameters from Table 2 in the paper (matching professor's implementation)
        params = {
            # Half-saturation constants (g/cm³)
            'K_L': 1.5e-14,      # GLP-1 (professor uses 1.5e-14)
            'K_hat_L': 1.5e-14,  # GLP-1 inhibitory saturation
            'K_U2': 9.45e-6,     # GLUT-2
            'K_U4': 2.78e-6,     # GLUT-4
            'K_I': 2e-13,        # Insulin
            'K_hat_O': 1.36e-6,  # Oleic acid inhibitory saturation
            
            # Activation rates (d⁻¹)
            'lambda_tilde_A': 0.35,      # α-cells
            'lambda_tilde_B': 1.745e9,   # β-cells
            'gamma_L': 4.95e-13,         # GLP-1 secretion (professor's tlamL)
            'lambda_IB': 12*1.05e-9,     # Insulin by β-cells (professor has factor of 12)
            'lambda_U4_I': 4.17e7,       # GLUT-4 by insulin
            'lambda_U2C': 6.6e10,        # GLUT-2 by glucagon
            'lambda_CA': 1.65e-11,       # Glucagon by α-cells
            'gamma_G': 0.21/5,           # Glucose secretion (professor's tlamG)
            'gamma_G_star': 19*0.5845,   # Glucose elimination (professor's tlamsG)
            'gamma_O': 1.83e-3/5,        # Oleic acid (professor's gamO)
            'gamma_P': 3.66e-3/800,      # Palmitic acid (professor's gamP)
            
            # Transport rates (d⁻¹)
            'lambda_GU4': 4*0.387,       # Glucose by GLUT-4 (professor's lamGU4)
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
            'mu_O': 0.57*24,      # Oleic acid (professor has daily rate)
            'mu_P': 0.5*24,       # Palmitic acid
            'mu_IG': 6e5,         # Insulin by glucose (professor's tmuIG)
            
            # Other parameters
            'gamma_1': 1e14,      # Glucagon blocking (professor's gam1)
            'gamma_2': 1.2e14,    # Glucagon inducing (professor's gam2)
            'xi_1': 1e12,         # β-cell deactivation by glucose
            'xi_2': 1e12,         # β-cell deactivation by palmitic
            'xi_3': 1e-2,         # Glucose switch level (inhibition)
            'xi_4': 1e-4,         # Glucose switch level (activation)
            'eta_T_alpha': 1e10,  # TNF-α inhibition of GLUT-4 (base value)
            'I_hypo': 0.8e-13,    # Hypoglycemia insulin level (professor's Io)
            'L_0': 0.3e-14,       # GLP-1 threshold (professor's Lo)
            
            # Initial values for reference
            'P_h': 1.22e-6,       # Healthy palmitic acid
            'O_h': 6.78e-7,       # Healthy oleic acid
            'P_o': 2.44e-6,       # Obese palmitic acid
            'O_o': 1.36e-6,       # Obese oleic acid
        }
        
        # Adjust parameters based on patient characteristics
        height_m = self.patient_data.height / 100
        bmi = self.patient_data.weight / (height_m ** 2)
        
        # Obesity factor affects palmitic acid release and eta_T_alpha
        if self.patient_data.diabetes_type == "diabetic":
            if bmi >= 30:  # Obese diabetic
                params['eta_T_alpha'] *= 1000  # Professor uses 1000x for obese+diabetic
                params['obesity_factor'] = 4.0
            else:  # Non-obese diabetic
                params['eta_T_alpha'] *= 100   # Professor uses 100x for diabetic
                params['obesity_factor'] = 2.0
        elif self.patient_data.diabetes_type == "prediabetic":
            params['eta_T_alpha'] *= 10       # Professor uses 10x for prediabetic
            params['obesity_factor'] = 1.5
        else:  # Normal
            params['eta_T_alpha'] *= 1        # Normal factor
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
    
    def Hill(self, x: float, x0: float, n: float = 2) -> float:
        """Hill function for smooth transitions"""
        return x**n / (x**n + x0**n)
    
    def myequal(self, x: float, x0: float, eps: float) -> bool:
        """Check if x is approximately equal to x0 within tolerance eps"""
        return abs(x - x0) <= eps
    
    def get_meal_times(self, t: float, meal_schedule: Optional[MealSchedule] = None) -> Tuple[float, float, float, float]:
        """Get meal-specific factors based on professor's implementation"""
        if meal_schedule:
            breakfast_time = meal_schedule.breakfast_time / 24
            lunch_time = meal_schedule.lunch_time / 24
            dinner_time = meal_schedule.dinner_time / 24
            breakfast_factor = meal_schedule.breakfast_factor
            lunch_factor = meal_schedule.lunch_factor
            dinner_factor = meal_schedule.dinner_factor
        else:
            breakfast_time = 0 / 24
            lunch_time = 6 / 24
            dinner_time = 12 / 24
            breakfast_factor = 0.4
            lunch_factor = 0.4
            dinner_factor = 0.8
        
        # Check which meal period we're in (professor's logic)
        t_mod = t % 1  # Get fractional part of day
        
        if self.myequal(t_mod, dinner_time, self.eps) and t > self.eps:
            return 0, 0, 0, dinner_factor
        elif self.myequal(t_mod, lunch_time, self.eps):
            return 0, 0, lunch_factor, 0
        elif self.myequal(t_mod, breakfast_time, self.eps):
            return breakfast_factor, 0, 0, 0
        else:
            return 0, 0, 0, 0
    
    def ode_system(self, y, t, food_factor=1.0, palmitic_factor=1.0, drug_dose=0.0, 
                   meal_schedule: Optional[MealSchedule] = None):
        """
        Complete ODE system from the paper (equations 2.2-2.12)
        Variables order (professor's): [B, A, L, I, U2, U4, C, G, G_star, T_alpha, O, P]
        """
        B, A, L, I, U2, U4, C, G, G_star, T_alpha, O, P = y
        
        # Get meal factors
        bf, lf, df, total_f = self.get_meal_times(t, meal_schedule)
        current_meal_factor = (bf + lf + df) * food_factor
        
        # Helper functions matching professor's implementation
        L_inh = 1 / (1 + L / self.params['K_hat_L'])
        L_frac = self.Hill(max(0, L - self.params['L_0']), self.params['K_L'], 1)
        I_o_frac = self.Hill(max(0, self.params['I_hypo'] - I), self.params['K_I'], 1)
        U2_frac = U2 / (self.params['K_U2'] + U2)
        U4_frac = U4 / (self.params['K_U4'] + U4)
        O_inh = 1 / (1 + O / self.params['K_hat_O'])
        T_alpha_inh = 1 / (1 + self.params['eta_T_alpha'] * T_alpha)
        
        # Lambda functions for time-dependent inputs
        def lambda_L(t):
            """GLP-1 production rate"""
            if current_meal_factor > 0:
                return self.params['gamma_L'] * current_meal_factor * (1 - self.Hill(t % (6/24), 1/24, 6))
            return 0
        
        def lambda_G(t):
            """Glucose production rate"""
            if current_meal_factor > 0:
                x0 = 0.3 + (0 if (t % 1) <= 6/24 else (0.1 if 6/24 < (t % 1) <= 12/24 else 0.3))
                return self.params['gamma_G'] * current_meal_factor * (1 - self.Hill(t % (6/24), x0/24, 4))
            return 0
        
        def lambda_G_star(t):
            """Glucose elimination rate"""
            if current_meal_factor > 0:
                return self.params['gamma_G_star'] * G * current_meal_factor * (1 - self.Hill(t % (6/24), 1/24, 4))
            return 0
        
        # Equation 2.2: GLP-1 (L)
        dL_dt = lambda_L(t) - self.params['mu_LB'] * B * L - self.params['mu_LA'] * A * L
        
        # Enhanced GLP-1 by drug (GLP-1 agonist effect)
        if drug_dose > 0:
            K_D = 1e-7
            dL_dt += lambda_L(t) * (drug_dose / (K_D + drug_dose))
        
        # Equation 2.4: α-cells (A)
        dA_dt = self.params['lambda_tilde_A'] * I_o_frac * L_inh - self.params['mu_A'] * A
        
        # Equation 2.3: β-cells (B)
        dB_dt = self.params['lambda_tilde_B'] * L_frac - self.params['mu_B'] * B * (1 + self.params['xi_1'] * G + self.params['xi_2'] * P)
        
        # Equation 2.5: Insulin (I)
        dI_dt = self.params['lambda_IB'] * B - self.params['mu_I'] * I - self.params['mu_IG'] * G * I
        
        # Equation 2.8: Glucagon (C)
        G_high = (G - self.params['xi_4']) > 0
        G_low = (self.params['xi_3'] - G) > 0
        dC_dt = (self.params['lambda_CA'] * A * (1 + self.params['gamma_2'] * G_low * L) / 
                (1 + self.params['gamma_1'] * G_high * L) - self.params['mu_C'] * C)
        
        # Equation 2.6: GLUT-2 (U2)
        dU2_dt = self.params['lambda_U2C'] * C - self.params['mu_U2'] * U2
        
        # Equation 2.7: GLUT-4 (U4)
        dU4_dt = self.params['lambda_U4_I'] * I * T_alpha_inh - self.params['mu_U4'] * U4
        
        # Equation 2.9: Blood glucose (G)
        # Adjust transport factor based on diabetes status (professor's implementation)
        transport_factor = 1.05 if self.patient_data.diabetes_type == "normal" else 1.25
        
        # Reduce glucose intake if drug is present
        if drug_dose > 0:
            K_hat_D = 1e-7
            lambda_G_drug = lambda_G(t) / (1 + drug_dose / K_hat_D)
        else:
            lambda_G_drug = lambda_G(t)
        
        dG_dt = (lambda_G_drug - lambda_G_star(t) - 
                transport_factor * self.params['lambda_GU4'] * G * U4_frac + 
                self.params['lambda_G_star_U2'] * G_star * U2_frac / 2)
        
        # Equation 2.10: Stored glucose (G*)
        # Time-dependent factor for glucose storage (professor's cst)
        cst = 1 if (t % 1) <= 6/24 else (1 if 6/24 < (t % 1) <= 12/24 else 3)
        dG_star_dt = (lambda_G_star(t) - cst * self.params['lambda_G_star_U2'] * G_star * U2_frac + 
                     self.params['lambda_GU4'] * G * U4_frac)
        
        # Equation 2.12: TNF-α (T_alpha)
        dT_alpha_dt = (self.params['lambda_T_alpha'] + 
                      1.15 * self.params['lambda_T_alpha_P'] * P * O_inh - 
                      self.params['mu_T_alpha'] * T_alpha)
        
        # Equation 2.11: Oleic acid (O) and Palmitic acid (P)
        def lambda_O(t):
            if current_meal_factor > 0:
                return self.params['gamma_O'] * current_meal_factor * self.F(t % (6/24), 0, 1/24)
            return 0
        
        def lambda_P(t):
            if current_meal_factor > 0:
                return self.params['gamma_P'] * current_meal_factor * palmitic_factor * self.params['obesity_factor'] * self.F(t % (6/24), 0, 1/24)
            return 0
        
        dO_dt = lambda_O(t) - self.params['mu_O'] * O
        dP_dt = lambda_P(t) - self.params['mu_P'] * P
        
        # Return in professor's order
        return [dB_dt, dA_dt, dL_dt, dI_dt, dU2_dt, dU4_dt, dC_dt, dG_dt, dG_star_dt, dT_alpha_dt, dO_dt, dP_dt]
    
    def get_initial_conditions(self):
        """Get initial conditions based on patient data (professor's values)"""
        # Base initial conditions
        B_0 = 13e-3   # β-cells (professor's B_0)
        A_0 = 5e-3    # α-cells
        L_0 = 4.5e-15 # GLP-1
        I_0 = 0.97e-13 # Insulin
        U2_0 = 9e-6   # GLUT-2
        U4_0 = 0.993 * 2.6e-6  # GLUT-4
        C_0 = 4.964e-16  # Glucagon
        Gs_0 = 0.9e-3    # Stored glucose
        Ta_0 = 5.65e-12  # TNF-α
        
        # Adjust glucose based on diabetes status
        if self.patient_data.diabetes_type == "diabetic":
            G_0 = 1e-3 * 1.8  # 80% higher
            P_0 = self.params['P_o']  # Obese palmitic
            O_0 = self.params['O_o']  # Obese oleic
        elif self.patient_data.diabetes_type == "prediabetic":
            G_0 = 1e-3 * 1.15  # 15% higher
            P_0 = (self.params['P_h'] + self.params['P_o']) / 2
            O_0 = (self.params['O_h'] + self.params['O_o']) / 2
        else:
            G_0 = 1e-3 * 0.95  # Normal
            P_0 = self.params['P_h']  # Healthy palmitic
            O_0 = self.params['O_h']  # Healthy oleic
        
        # Return in professor's order
        return [B_0, A_0, L_0, I_0, U2_0, U4_0, C_0, G_0, Gs_0, Ta_0, O_0, P_0]
    
    def simulate(self, hours=24, food_factor=1.0, palmitic_factor=1.0, drug_dosage=0.0,
                meal_schedule: Optional[MealSchedule] = None, 
                include_all_variables=False):
        """Run the simulation and return results"""
        # Convert hours to days for ODE solver
        days = hours / 24
        
        # Time points with high resolution (professor uses 2400 points per day)
        points_per_day = 2400
        total_points = int(days * points_per_day)
        t = np.linspace(1e-10, days, total_points)
        
        # Initial conditions
        y0 = self.get_initial_conditions()
        
        try:
            # Solve ODE system
            solution = odeint(
                self.ode_system, 
                y0, 
                t, 
                args=(food_factor, palmitic_factor, drug_dosage, meal_schedule),
                mxstep=50000  # Professor uses high mxstep
            )
            
            # Extract variables (in professor's order)
            B, A, L, I, U2, U4, C, G, G_star, T_alpha, O, P = solution.T
            
            # Convert time back to hours
            time_hours = t * 24
            
            # Convert to appropriate units (matching professor's plots)
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
            
            # Determine diagnosis based on glucose levels
            if np.mean(glucose_mg_dl) < 100:
                diagnosis = "Normal"
            elif np.mean(glucose_mg_dl) < 125:
                diagnosis = "Prediabetic"
            else:
                diagnosis = "Diabetic"
            
            # Generate optimal glucose trajectory for comparison
            optimal_glucose = self._generate_optimal_glucose(time_hours, meal_schedule)
            
            if include_all_variables:
                return ExtendedSimulationResult(
                    time_points=time_hours.tolist(),
                    glucose=glucose_mg_dl.tolist(),
                    insulin=insulin_pmol_l.tolist(),
                    glucagon=glucagon_pg_ml.tolist(),
                    glp1=glp1_pmol_l.tolist(),
                    alpha_cells=(A * 1e3).tolist(),  # Convert to 10^-3 units
                    beta_cells=(B * 1e3).tolist(),
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
                    time_points=time_hours.tolist(),
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
        
        # Convert hours to days for consistency
        t_days = t / 24
        
        for time in t_days:
            # Base glucose level (professor uses 95-100 for normal)
            base_glucose = 95  # mg/dL baseline
            
            # Add meal responses
            t_mod = time % 1
            if self.myequal(t_mod, 0, self.eps):
                base_glucose += 20  # Breakfast spike
            elif self.myequal(t_mod, 6/24, self.eps):
                base_glucose += 25  # Lunch spike
            elif self.myequal(t_mod, 12/24, self.eps):
                base_glucose += 40  # Dinner spike (larger)
            
            # Add some decay after meals
            for meal_time in [0, 6/24, 12/24]:
                if t_mod > meal_time and t_mod < meal_time + 4/24:
                    time_since_meal = (t_mod - meal_time) * 24
                    decay = np.exp(-time_since_meal / 2)
                    base_glucose += 20 * decay
            
            optimal_G.append(base_glucose)
        
        return optimal_G