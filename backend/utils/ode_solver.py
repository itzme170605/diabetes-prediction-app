import numpy as np
from scipy.integrate import odeint, solve_ivp
from models.diabetes_model import PatientData, SimulationResult, HealthMetrics
import math
import warnings

class DiabetesODESolver:
    def __init__(self, patient_data: PatientData):
        self.patient_data = patient_data
        # Calculate derived values
        self.patient_data.calculate_derived_values()
        self.params = self._calculate_parameters()
        
    def _calculate_parameters(self):
        """Calculate model parameters based on patient data with enhanced personalization"""
        # Base parameters from the diabetes model paper
        params = {
            # Half-saturation constants (g/cm³)
            'K_L': 1.7e-14,      # GLP-1
            'K_U2': 9.45e-6,     # GLUT-2
            'K_U4': 2.78e-6,     # GLUT-4
            'K_I': 2e-13,        # Insulin
            
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
            
            # Switch parameters
            'gamma_1': 1e-14,     # Glucagon blocking
            'gamma_2': 1.2e-14,   # Glucagon inducing
            'xi_1': 1e12,         # β-cell deactivation by glucose
            'xi_2': 1e12,         # β-cell deactivation by palmitic
            'xi_3': 1e-2,         # Glucose switch level (inhibition)
            'xi_4': 1e-4,         # Glucose switch level (activation)
            'eta_T_alpha': 1e10,  # TNF-α inhibition of GLUT-4
            'I_hypo': 8e-14,      # Hypoglycemia insulin level
            'L_0': 1.7e-14,       # GLP-1 threshold
            'K_hat_L': 1.7e-14,   # GLP-1 inhibitory saturation
            'K_hat_O': 1.36e-6,   # Oleic acid inhibitory saturation
        }
        
        # Patient-specific adjustments
        self._adjust_for_obesity(params)
        self._adjust_for_age(params)
        self._adjust_for_diabetes_status(params)
        self._adjust_for_gender(params)
        self._adjust_for_activity_level(params)
        self._adjust_for_medications(params)
        
        return params
    
    def _adjust_for_obesity(self, params):
        """Adjust parameters based on BMI and obesity level"""
        bmi = self.patient_data.bmi
        
        if bmi >= 35:  # Severely obese
            params['obesity_factor'] = 6.0
            params['gamma_P_hat'] *= 2.5
            params['lambda_T_alpha_P'] *= 2.0
            params['eta_T_alpha'] *= 1.5
        elif bmi >= 30:  # Obese
            params['obesity_factor'] = 4.0
            params['gamma_P_hat'] *= 2.0
            params['lambda_T_alpha_P'] *= 1.5
        elif bmi >= 25:  # Overweight
            params['obesity_factor'] = 2.0
            params['gamma_P_hat'] *= 1.3
        else:  # Normal/underweight
            params['obesity_factor'] = 1.0
    
    def _adjust_for_age(self, params):
        """Adjust parameters based on age"""
        age = self.patient_data.age
        
        # β-cell function decreases with age
        if age >= 65:
            age_factor = 0.6
        elif age >= 45:
            age_factor = 0.8
        elif age >= 35:
            age_factor = 0.9
        else:
            age_factor = 1.0
        
        params['lambda_tilde_B'] *= age_factor
        params['lambda_IB'] *= age_factor
        
        # Insulin sensitivity decreases with age
        if age >= 50:
            params['lambda_U4_I'] *= 0.85
            params['lambda_GU4'] *= 0.9
    
    def _adjust_for_diabetes_status(self, params):
        """Adjust parameters based on diabetes status"""
        diabetes_type = self.patient_data.diabetes_type
        
        if diabetes_type == "diabetic":
            # Reduced β-cell function
            params['lambda_tilde_B'] *= 0.4
            params['lambda_IB'] *= 0.5
            # Increased insulin resistance
            params['lambda_U4_I'] *= 0.6
            params['lambda_GU4'] *= 0.7
            # Increased inflammation
            params['lambda_T_alpha'] *= 2.0
            params['lambda_T_alpha_P'] *= 1.5
            
        elif diabetes_type == "prediabetic":
            # Moderately reduced β-cell function
            params['lambda_tilde_B'] *= 0.7
            params['lambda_IB'] *= 0.8
            # Mild insulin resistance
            params['lambda_U4_I'] *= 0.8
            params['lambda_GU4'] *= 0.85
            # Mild inflammation
            params['lambda_T_alpha'] *= 1.3
    
    def _adjust_for_gender(self, params):
        """Adjust parameters based on gender"""
        if self.patient_data.gender.lower() in ['female', 'f']:
            # Women generally have better insulin sensitivity
            params['lambda_U4_I'] *= 1.1
            params['lambda_GU4'] *= 1.05
            # Different fat metabolism
            params['gamma_P'] *= 0.9
    
    def _adjust_for_activity_level(self, params):
        """Adjust parameters based on activity level"""
        activity_level = self.patient_data.activity_level
        
        if activity_level == "active":
            # Improved insulin sensitivity
            params['lambda_U4_I'] *= 1.3
            params['lambda_GU4'] *= 1.2
            # Reduced inflammation
            params['lambda_T_alpha'] *= 0.8
            params['lambda_T_alpha_P'] *= 0.7
        elif activity_level == "moderate":
            params['lambda_U4_I'] *= 1.15
            params['lambda_GU4'] *= 1.1
            params['lambda_T_alpha'] *= 0.9
        elif activity_level == "sedentary":
            # Reduced insulin sensitivity
            params['lambda_U4_I'] *= 0.85
            params['lambda_GU4'] *= 0.9
            # Increased inflammation
            params['lambda_T_alpha'] *= 1.2
    
    def _adjust_for_medications(self, params):
        """Adjust parameters based on medications"""
        medications = [med.lower() for med in self.patient_data.medications]
        
        if any('metformin' in med for med in medications):
            # Metformin improves insulin sensitivity
            params['lambda_U4_I'] *= 1.2
            params['lambda_GU4'] *= 1.15
            params['gamma_G'] *= 0.9  # Reduced glucose production
        
        if any('insulin' in med for med in medications):
            # External insulin supplementation
            params['lambda_IB'] *= 1.5
        
        if any('glp1' in med or 'semaglutide' in med or 'ozempic' in med for med in medications):
            # GLP-1 agonists
            params['gamma_L'] *= 2.0
            params['mu_LB'] *= 0.5  # Slower degradation
    
    def F(self, t, t0, t1):
        """Food intake function"""
        return 1.0 if t0 <= t <= t1 else 0.0
    
    def H(self, x):
        """Heaviside step function"""
        return 1.0 if x > 0 else 0.0
    
    def exercise_effect(self, t, exercise_times, duration=2.0):
        """Exercise effect function"""
        for exercise_time in exercise_times:
            if exercise_time <= t <= exercise_time + duration:
                # Exercise increases glucose uptake
                return 1.5
        return 1.0
    
    def ode_system(self, t, y, food_factor=1.0, palmitic_factor=1.0, drug_dose=0.0, meal_times=None, exercise_times=None):
        """
        Enhanced ODE system with better meal timing and exercise effects
        Variables: [L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha]
        """
        if meal_times is None:
            meal_times = [0, 6, 12, 18]
        if exercise_times is None:
            exercise_times = []
        
        L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha = y
        
        # Food intake timing (meals with 1.5 hour duration)
        food_active = any(self.F(t % 24, mt, mt + 1.5) for mt in meal_times)
        
        # Exercise effects
        exercise_factor = self.exercise_effect(t, exercise_times)
        
        # Equation for GLP-1 (L)
        lambda_L = self.params['gamma_L'] * food_factor if food_active else 0
        dL_dt = lambda_L - self.params['mu_LB'] * B * L - self.params['mu_LA'] * A * L
        
        # Enhanced GLP-1 by drug (for GLP-1 agonists)
        if drug_dose > 0:
            K_D = 1e-7
            dL_dt += lambda_L * (drug_dose / (K_D + drug_dose))
        
        # Equation for β-cells (B)
        L_term = max(0, L - self.params['L_0'])
        dB_dt = (self.params['lambda_tilde_B'] * L_term / 
                (self.params['K_L'] + L_term) - 
                self.params['mu_B'] * B * (1 + self.params['xi_1'] * G + self.params['xi_2'] * P))
        
        # Equation for α-cells (A)
        I_term = max(0, self.params['I_hypo'] - I)
        dA_dt = (self.params['lambda_tilde_A'] * I_term / 
                (self.params['K_I'] + I_term) * 
                (1 / (1 + L / self.params['K_hat_L'])) - 
                self.params['mu_A'] * A)
        
        # Equation for insulin (I)
        dI_dt = self.params['lambda_IB'] * B - self.params['mu_I'] * I - self.params['mu_IG'] * G * I
        
        # Equation for GLUT-2 (U2)
        dU2_dt = self.params['lambda_U2C'] * C - self.params['mu_U2'] * U2
        
        # Equation for GLUT-4 (U4) with exercise enhancement
        dU4_dt = (self.params['lambda_U4_I'] * I * exercise_factor * 
                 (1 / (1 + self.params['eta_T_alpha'] * T_alpha)) - 
                 self.params['mu_U4'] * U4)
        
        # Equation for glucagon (C)
        G_high_term = self.H(G - self.params['xi_4'])
        G_low_term = self.H(self.params['xi_3'] - G)
        dC_dt = (self.params['lambda_CA'] * A / 
                (1 + self.params['gamma_1'] * G_high_term * L) * 
                (1 + self.params['gamma_2'] * G_low_term * L) - 
                self.params['mu_C'] * C)
        
        # Equation for blood glucose (G) with exercise effects
        lambda_G = self.params['gamma_G'] * food_factor if food_active else 0
        lambda_G_star = self.params['gamma_G_star'] if any(mt <= t % 24 <= mt + 3 for mt in meal_times) else 0
        
        # Reduce glucose intake if drug is present (SGLT2 inhibitors effect)
        if drug_dose > 0:
            K_hat_D = 1e-7
            lambda_G = lambda_G / (1 + drug_dose / K_hat_D)
        
        dG_dt = (lambda_G - lambda_G_star * G + 
                self.params['lambda_G_star_U2'] * G_star * U2 / (self.params['K_U2'] + U2) - 
                self.params['lambda_GU4'] * G * U4 * exercise_factor / (self.params['K_U4'] + U4))
        
        # Equation for stored glucose (G*)
        dG_star_dt = (lambda_G_star * G + 
                     self.params['lambda_GU4'] * G * U4 * exercise_factor / (self.params['K_U4'] + U4) - 
                     self.params['lambda_G_star_U2'] * G_star * U2 / (self.params['K_U2'] + U2))
        
        # Equation for oleic acid (O)
        lambda_O = self.params['gamma_O'] * food_factor if food_active else 0
        dO_dt = lambda_O - self.params['mu_O'] * O
        
        # Equation for palmitic acid (P)
        lambda_P = ((self.params['gamma_P'] + 
                    palmitic_factor * self.params['gamma_P_hat'] * self.params['obesity_factor']) * 
                   food_factor if food_active else 0)
        dP_dt = lambda_P - self.params['mu_P'] * P
        
        # Equation for TNF-α (T_alpha)
        dT_alpha_dt = (self.params['lambda_T_alpha'] + 
                      self.params['lambda_T_alpha_P'] * P * (1 / (1 + O / self.params['K_hat_O'])) - 
                      self.params['mu_T_alpha'] * T_alpha)
        
        return [dL_dt, dA_dt, dB_dt, dI_dt, dU2_dt, dU4_dt, dC_dt, dG_dt, dG_star_dt, dO_dt, dP_dt, dT_alpha_dt]
    
    def get_initial_conditions(self):
        """Get initial conditions based on patient data"""
        diabetes_type = self.patient_data.diabetes_type
        bmi = self.patient_data.bmi
        
        # Adjust initial conditions based on patient characteristics
        if diabetes_type == "diabetic":
            # Diabetic initial conditions
            base_conditions = [
                4.5e-15,   # L (GLP-1)
                12e-12,    # A (α-cells) - higher in diabetic
                4e-12,     # B (β-cells) - lower in diabetic  
                0.4e-13,   # I (insulin) - lower in diabetic
                8.5e-6,    # U2 (GLUT-2)
                1.2e-6,    # U4 (GLUT-4) - lower in diabetic
                18e-16,    # C (glucagon) - higher in diabetic
                1.4e-3,    # G (glucose) - higher in diabetic
                0.6e-3,    # G* (stored glucose)
                7.2e-7,    # O (oleic acid)
                2.8e-6,    # P (palmitic acid) - higher in diabetic
                10e-12     # T_alpha (TNF-α) - higher in diabetic
            ]
        elif diabetes_type == "prediabetic":
            # Prediabetic initial conditions
            base_conditions = [
                4.5e-15,   # L (GLP-1)
                9e-12,     # A (α-cells)
                6e-12,     # B (β-cells)
                0.7e-13,   # I (insulin)
                9.0e-6,    # U2 (GLUT-2)
                1.8e-6,    # U4 (GLUT-4)
                12e-16,    # C (glucagon)
                1.15e-3,   # G (glucose)
                0.45e-3,   # G* (stored glucose)
                6.9e-7,    # O (oleic acid)
                2.0e-6,    # P (palmitic acid)
                8e-12      # T_alpha (TNF-α)
            ]
        else:
            # Normal/healthy initial conditions
            base_conditions = [
                4.5e-15,   # L (GLP-1)
                6e-12,     # A (α-cells)
                10e-12,    # B (β-cells)
                1.0e-13,   # I (insulin)
                9.45e-6,   # U2 (GLUT-2)
                2.78e-6,   # U4 (GLUT-4)
                5.4e-16,   # C (glucagon)
                8.5e-4,    # G (glucose) - normal fasting
                0.3e-3,    # G* (stored glucose)
                6.78e-7,   # O (oleic acid)
                1.22e-6,   # P (palmitic acid)
                6e-12      # T_alpha (TNF-α)
            ]
        
        # Adjust for obesity
        if bmi >= 30:
            base_conditions[10] *= 2.0  # Increase palmitic acid
            base_conditions[11] *= 1.5  # Increase TNF-α
            base_conditions[5] *= 0.8   # Decrease GLUT-4
        
        return base_conditions
    
    def simulate(self, hours=24, food_factor=1.0, palmitic_factor=1.0, drug_dosage=0.0, meal_times=None, exercise_times=None):
        """Run the enhanced simulation and return results"""
        if meal_times is None:
            meal_times = [0, 6, 12, 18]
        if exercise_times is None:
            exercise_times = []
        
        # Time points with 5-minute resolution for better accuracy
        t = np.linspace(0, hours, int(hours * 12))
        
        # Initial conditions
        y0 = self.get_initial_conditions()
        
        try:
            # Solve ODE system using solve_ivp for better numerical stability
            result = solve_ivp(
                lambda t, y: self.ode_system(t, y, food_factor, palmitic_factor, drug_dosage, meal_times, exercise_times),
                [0, hours],
                y0,
                t_eval=t,
                method='RK45',
                rtol=1e-8,
                atol=1e-10
            )
            
            if not result.success:
                raise Exception(f"ODE solver failed: {result.message}")
            
            # Extract variables
            L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha = result.y
            
            # Convert to appropriate units for medical interpretation
            glucose_mg_dl = G * 180000  # Convert to mg/dL (more accurate conversion)
            insulin_pmol_l = I * 6e15   # Convert to pmol/L
            glucagon_pg_ml = C * 3.5e15 # Convert to pg/mL
            glp1_pmol_l = L * 1e15      # Convert to pmol/L
            
            # Calculate A1C estimate (using more accurate formula)
            avg_glucose_mg_dl = np.mean(glucose_mg_dl)
            a1c_estimate = (avg_glucose_mg_dl + 46.7) / 28.7
            
            # Determine diagnosis based on multiple criteria
            max_glucose = np.max(glucose_mg_dl)
            min_glucose = np.min(glucose_mg_dl)
            
            if a1c_estimate >= 6.5 or max_glucose >= 200:
                diagnosis = "Diabetic"
            elif a1c_estimate >= 5.7 or avg_glucose_mg_dl >= 100:
                diagnosis = "Prediabetic"
            else:
                diagnosis = "Normal"
            
            # Generate optimal glucose trajectory
            optimal_glucose = self._generate_optimal_glucose(t, meal_times)
            
            # Create result object
            result_obj = SimulationResult(
                time_points=t.tolist(),
                glucose=glucose_mg_dl.tolist(),
                insulin=insulin_pmol_l.tolist(),
                glucagon=glucagon_pg_ml.tolist(),
                glp1=glp1_pmol_l.tolist(),
                beta_cells=(B * 1e12).tolist(),  # Scale for visualization
                alpha_cells=(A * 1e12).tolist(),  # Scale for visualization
                optimal_glucose=optimal_glucose,
                a1c_estimate=round(a1c_estimate, 2),
                diagnosis=diagnosis,
                patient_info=self._get_patient_info(),
                simulation_summary={},
                recommendations=self._generate_recommendations(),
                risk_factors=self._identify_risk_factors()
            )
            
            # Generate summary statistics
            result_obj.generate_summary()
            
            return result_obj
            
        except Exception as e:
            print(f"ODE solver error: {e}")
            raise Exception(f"Simulation failed: {str(e)}")
    
    def _generate_optimal_glucose(self, t, meal_times):
        """Generate optimal glucose trajectory for healthy individual"""
        optimal_G = []
        for time in t:
            base_glucose = 90  # mg/dL baseline
            glucose_response = base_glucose
            
            for meal_time in meal_times:
                time_in_day = time % 24
                if time_in_day >= meal_time:
                    time_since_meal = time_in_day - meal_time
                    if time_since_meal <= 4:  # 4-hour post-meal period
                        # More realistic glucose response curve
                        peak_time = 1.0  # Peak at 1 hour
                        if time_since_meal <= peak_time:
                            # Rising phase
                            peak_response = 40 * (time_since_meal / peak_time)
                        else:
                            # Falling phase
                            peak_response = 40 * math.exp(-(time_since_meal - peak_time) / 1.5)
                        glucose_response += peak_response
            
            # Add circadian rhythm effect
            circadian_effect = 5 * math.sin(2 * math.pi * (time % 24) / 24 + math.pi)
            glucose_response += circadian_effect
            
            optimal_G.append(max(70, min(140, glucose_response)))
        
        return optimal_G
    
    def _get_patient_info(self):
        """Get formatted patient information"""
        return {
            "name": self.patient_data.name,
            "age": self.patient_data.age,
            "gender": self.patient_data.gender,
            "bmi": self.patient_data.bmi,
            "bmi_category": self.patient_data.bmi_category,
            "diabetes_type": self.patient_data.diabetes_type,
            "diabetes_risk": self.patient_data.diabetes_risk,
            "activity_level": self.patient_data.activity_level,
            "medications": self.patient_data.medications
        }
    
    def _generate_recommendations(self):
        """Generate personalized recommendations"""
        recommendations = []
        
        if self.patient_data.bmi >= 25:
            recommendations.append("Consider weight management through diet and exercise")
        
        if self.patient_data.activity_level == "sedentary":
            recommendations.append("Increase physical activity to at least 150 minutes per week")
        
        if self.patient_data.diabetes_type in ["prediabetic", "diabetic"]:
            recommendations.append("Monitor blood glucose regularly")
            recommendations.append("Follow a diabetes-appropriate diet")
        
        if self.patient_data.age >= 45 and not self.patient_data.medications:
            recommendations.append("Consider regular diabetes screening")
        
        if self.patient_data.smoking_status == "smoker":
            recommendations.append("Smoking cessation is highly recommended")
        
        return recommendations
    
    def _identify_risk_factors(self):
        """Identify patient risk factors"""
        risk_factors = []
        
        if self.patient_data.age >= 45:
            risk_factors.append("Age ≥ 45 years")
        
        if self.patient_data.bmi >= 25:
            risk_factors.append(f"BMI {self.patient_data.bmi} (overweight/obese)")
        
        if self.patient_data.family_history:
            risk_factors.append("Family history of diabetes")
        
        if self.patient_data.activity_level == "sedentary":
            risk_factors.append("Sedentary lifestyle")
        
        if self.patient_data.smoking_status == "smoker":
            risk_factors.append("Current smoker")
        
        return risk_factors