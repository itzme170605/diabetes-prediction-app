import numpy as np
from scipy.integrate import solve_ivp
from models.diabetes_model import PatientData, SimulationResult
import math
import warnings

class DiabetesODESolver:
    def __init__(self, patient_data: PatientData):
        self.patient_data = patient_data
        self.patient_data.calculate_derived_values()
        self.params = self._get_model_parameters()
        
    def _get_model_parameters(self):
        """Get model parameters from Table 2 in the paper with proper units"""
        params = {
            # Half-saturation constants (g/cm³) - From Table 2
            'K_L': 1.7e-14,           # Half-saturation of GLP-1
            'K_hat_L': 1.7e-14,       # Inhibitory-saturation by GLP-1
            'K_U2': 9.45e-6,          # Half-saturation of GLUT-2
            'K_U4': 2.78e-6,          # Half-saturation of GLUT-4
            'K_I': 2e-13,             # Half-saturation of insulin
            'K_hat_O': 1.36e-6,       # Inhibitory-saturation of P by O
            'K_D': 1e-7,              # Half-saturation of G by D (drug)
            'K_hat_D': 1e-7,          # Inhibitory-saturation of G by D
            
            # Activation rates (d⁻¹) - From Table 2
            'lambda_tilde_A': 0.35,           # Activation rate of A
            'lambda_tilde_B': 1.745e9,        # Activation rate of B
            'gamma_L': 1.98e-13,              # Baseline secretion rate of GLP-1
            'lambda_IB': 1.26e-8,             # Secretion rate of insulin by B
            'lambda_U4_I': 4.17e7,            # Secretion rate of GLUT-4 by I
            'lambda_U2C': 6.6e10,             # Secretion rate of GLUT-2 by C
            'lambda_CA': 1.65e-11,            # Secretion rate of glucagon by A
            'gamma_G': 0.017,                 # Baseline secretion rate of glucose
            'gamma_G_star': 11.1,             # Baseline rate of early glucose elimination
            'gamma_O': 1.46e-4,               # Baseline secretion rate of oleic acid
            'gamma_P': 1.83e-6,               # Baseline secretion rate of palmitic acid
            'gamma_P_hat': 5.72e-5,           # Obesity-prone secretion rate of palmitic acid
            
            # Transport rates (d⁻¹) - From Table 2
            'lambda_GU4': 1.548,              # Transportation rate of glucose by U4
            'lambda_G_star_U2': 4.644,        # Importation rate of liver-glucose by U2
            'lambda_T_alpha': 1.19e-9,        # Normal secretion rate of TNF-α
            'lambda_T_alpha_P': 3.26e-4,      # Secretion rate of TNF-α by palmitic acid
            
            # Decay/degradation rates (d⁻¹) - From Table 2
            'mu_A': 8.32,                     # Deactivation rate of A
            'mu_B': 8.32,                     # Deactivation rate of B
            'mu_LB': 251,                     # Absorption rate of GLP-1 by B
            'mu_LA': 251,                     # Absorption rate of GLP-1 by A
            'mu_I': 198.04,                   # Decay rate of insulin
            'mu_U4': 1.85,                    # Decay rate of GLUT-4
            'mu_U2': 4.62,                    # Decay rate of GLUT-2
            'mu_C': 166.22,                   # Decay rate of glucagon
            'mu_T_alpha': 199,                # Decay rate of TNF-α
            'mu_O': 13.68,                    # Degradation rate of oleic acid
            'mu_P': 12,                       # Degradation rate of palmitic acid
            'mu_D': 0.139,                    # Degradation rate of mounjaro
            'mu_IG': 6e5,                     # Baseline decay rate of I by G
            
            # Switch parameters - From Table 2
            'gamma_1': 1e-14,                 # Blocking rate of glucagon
            'gamma_2': 1.2e-14,               # Inducing rate of glucagon
            'xi_1': 1e12,                     # Deactivation rate of B by G
            'xi_2': 1e12,                     # Deactivation rate of B by P
            'xi_3': 1e-2,                     # Switch level of G for inhibition of C-secretion
            'xi_4': 1e-4,                     # Switch level of G for activation of C-secretion
            'eta_T_alpha': 1e10,              # Rate of inhibiting-effect of TNF-α on GLUT-4
            'I_hypo': 8e-14,                  # Level of I in hypoglycemia
            'L_0': 1.7e-14,                   # Threshold GLP-1 level
        }
        
        # Adjust parameters based on patient characteristics
        self._adjust_for_patient_characteristics(params)
        return params
    
    def _adjust_for_patient_characteristics(self, params):
        """Adjust parameters based on patient data following paper methodology"""
        bmi = self.patient_data.bmi
        age = self.patient_data.age
        diabetes_type = self.patient_data.diabetes_type
        activity_level = self.patient_data.activity_level
        medications = self.patient_data.medications
        
        # Obesity factor adjustment (Figure 7 methodology)
        # Paper uses eta_T_alpha multipliers: 1, 10, 100, 1000 for different obesity levels
        if bmi >= 35:  # Severely obese (Factor=4, 4γ̂P equivalent)
            self.obesity_multiplier = 1000
            params['gamma_P_hat'] *= 4.0
            self.food_adaptation_factor = 4.0
        elif bmi >= 30:  # Obese (Factor=4, 3γ̂P equivalent)
            self.obesity_multiplier = 100
            params['gamma_P_hat'] *= 3.0
            self.food_adaptation_factor = 3.0
        elif bmi >= 25:  # Overweight (Factor=3, 2γ̂P equivalent)
            self.obesity_multiplier = 10
            params['gamma_P_hat'] *= 2.0
            self.food_adaptation_factor = 2.0
        else:  # Normal (Factor=1, 0γ̂P equivalent)
            self.obesity_multiplier = 1
            self.food_adaptation_factor = 1.0
        
        # Apply obesity multiplier to eta_T_alpha (key mechanism from paper)
        params['eta_T_alpha'] *= self.obesity_multiplier
        
        # Age-related β-cell decline (more gradual as in clinical reality)
        age_factor = 1.0
        if age >= 65:
            age_factor = 0.6
        elif age >= 55:
            age_factor = 0.7
        elif age >= 45:
            age_factor = 0.8
        elif age >= 35:
            age_factor = 0.9
        
        params['lambda_tilde_B'] *= age_factor
        params['lambda_IB'] *= age_factor
        
        # Diabetes status adjustments (progressive impairment)
        if diabetes_type == "diabetic":
            # Severe β-cell dysfunction
            params['lambda_tilde_B'] *= 0.3  # More severe than paper to match clinical reality
            params['lambda_IB'] *= 0.4
            params['lambda_U4_I'] *= 0.5    # Significant insulin resistance
            # Increased inflammation
            params['lambda_T_alpha'] *= 2.0
            params['lambda_T_alpha_P'] *= 1.8
        elif diabetes_type == "prediabetic":
            # Moderate impairment
            params['lambda_tilde_B'] *= 0.7
            params['lambda_IB'] *= 0.75
            params['lambda_U4_I'] *= 0.8
            # Mild inflammation
            params['lambda_T_alpha'] *= 1.3
            params['lambda_T_alpha_P'] *= 1.2
        
        # Activity level adjustments (significant impact on insulin sensitivity)
        if activity_level == "active":
            params['lambda_U4_I'] *= 1.4    # Strong insulin sensitivity improvement
            params['lambda_GU4'] *= 1.3
            params['lambda_T_alpha'] *= 0.7  # Reduced inflammation
            params['eta_T_alpha'] *= 0.8     # Reduced TNF-α effect
        elif activity_level == "moderate":
            params['lambda_U4_I'] *= 1.2
            params['lambda_GU4'] *= 1.15
            params['lambda_T_alpha'] *= 0.85
        elif activity_level == "light":
            params['lambda_U4_I'] *= 1.05
            params['lambda_GU4'] *= 1.05
        elif activity_level == "sedentary":
            params['lambda_U4_I'] *= 0.8     # Reduced insulin sensitivity
            params['lambda_GU4'] *= 0.85
            params['lambda_T_alpha'] *= 1.3  # Increased inflammation
        
        # Medication adjustments (common diabetes medications)
        med_names = [med.lower() for med in medications]
        
        if any('metformin' in med for med in med_names):
            # Metformin: improves insulin sensitivity, reduces glucose production
            params['lambda_U4_I'] *= 1.25
            params['lambda_GU4'] *= 1.2
            params['gamma_G'] *= 0.85        # Reduced hepatic glucose production
            params['lambda_T_alpha'] *= 0.9  # Mild anti-inflammatory effect
        
        if any('insulin' in med for med in med_names):
            # External insulin supplementation
            params['lambda_IB'] *= 1.8       # Simulates external insulin
        
        if any(glp1_med in med for glp1_med in ['semaglutide', 'liraglutide', 'dulaglutide', 'glp-1'] for med in med_names):
            # GLP-1 agonists: enhance endogenous GLP-1 action
            params['gamma_L'] *= 2.5
            params['mu_LB'] *= 0.6           # Slower degradation
            params['mu_LA'] *= 0.6
        
        if any('sglt2' in med or 'empagliflozin' in med or 'canagliflozin' in med for med in med_names):
            # SGLT2 inhibitors: increase glucose excretion
            params['gamma_G'] *= 0.8         # Simulates glucose excretion
        
        # Gender-based adjustments (hormonal differences)
        if self.patient_data.gender.lower() in ['female', 'f']:
            # Women typically have better insulin sensitivity but different fat distribution
            params['lambda_U4_I'] *= 1.1
            params['gamma_P'] *= 0.9         # Different fatty acid metabolism
            # Adjust for potential hormonal effects
            if age >= 50:  # Post-menopausal considerations
                params['lambda_U4_I'] *= 0.95
                params['lambda_T_alpha'] *= 1.1
        
        # Smoking effects (strong negative impact)
        if self.patient_data.smoking_status == "smoker":
            params['lambda_U4_I'] *= 0.75    # Reduced insulin sensitivity
            params['lambda_T_alpha'] *= 1.4  # Increased inflammation
            params['eta_T_alpha'] *= 1.2     # Enhanced TNF-α effects
        elif self.patient_data.smoking_status == "former_smoker":
            params['lambda_U4_I'] *= 0.9     # Partial recovery
            params['lambda_T_alpha'] *= 1.1
    
    def F(self, t, t0, t1):
        """Food intake function - active during meal periods"""
        current_time = t % 24  # Wrap to 24-hour cycle
        return 1.0 if t0 <= current_time <= t1 else 0.0
    
    def H(self, x):
        """Heaviside step function"""
        return 1.0 if x > 0 else 0.0
    
    def ode_system(self, t, y, food_factor=1.0, palmitic_factor=1.0, drug_dose=0.0, 
                   meal_times=None, meal_factors=None):
        """
        Complete 12-variable ODE system from the paper
        Variables: [L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha]
        
        L: GLP-1 concentration
        A: α-cell density  
        B: β-cell density
        I: Insulin concentration
        U2: GLUT-2 density
        U4: GLUT-4 density
        C: Glucagon concentration
        G: Blood glucose concentration
        G_star: Liver glucose (glycogen)
        O: Oleic acid concentration
        P: Palmitic acid concentration
        T_alpha: TNF-α concentration
        """
        if meal_times is None:
            meal_times = [0, 6, 12, 18]  # Default meal times
        if meal_factors is None:
            meal_factors = [1.0, 1.0, 2.0, 0.0]  # breakfast, lunch, dinner, night snack
        
        L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha = y
        
        # Determine current meal factor and activity
        current_hour = t % 24
        current_meal_factor = 0.0
        meal_duration = 1.5  # 1.5 hour meal duration as in paper
        
        # Check active meal periods
        for i, meal_time in enumerate(meal_times):
            if meal_time <= current_hour <= meal_time + meal_duration:
                current_meal_factor = meal_factors[i] if i < len(meal_factors) else 0.0
                break
        
        # Food intake functions (λ functions from paper)
        food_active = current_meal_factor > 0
        
        lambda_L = (self.params['gamma_L'] * food_factor * current_meal_factor 
                   if food_active else 0)
        
        lambda_G = (self.params['gamma_G'] * food_factor * current_meal_factor 
                   if food_active else 0)
        
        # Early glucose elimination (first 2-3 hours after meal as in paper)
        elimination_active = any(
            meal_time + 1 <= current_hour <= meal_time + 3 
            for meal_time in meal_times
        )
        lambda_G_star = (self.params['gamma_G_star'] * G 
                        if elimination_active else 0)
        
        lambda_O = (self.params['gamma_O'] * food_factor * current_meal_factor 
                   if food_active else 0)
        
        lambda_P = ((self.params['gamma_P'] + 
                    palmitic_factor * self.params['gamma_P_hat']) * 
                   food_factor * current_meal_factor 
                   if food_active else 0)
        
        # Drug effects (Equations 4.17-4.18 from paper)
        drug_enhancement = drug_dose / (self.params['K_D'] + drug_dose) if drug_dose > 0 else 0
        glucose_drug_inhibition = (1 + drug_dose / self.params['K_hat_D']) if drug_dose > 0 else 1
        
        # Equation 2.2: GLP-1 dynamics with drug enhancement
        dL_dt = (lambda_L * (1 + drug_enhancement) - 
                self.params['mu_LB'] * B * L - 
                self.params['mu_LA'] * A * L)
        
        # Equation 2.3: β-cell dynamics
        L_term = max(0, L - self.params['L_0'])
        dB_dt = (self.params['lambda_tilde_B'] * L_term / 
                (self.params['K_L'] + L_term) - 
                self.params['mu_B'] * B * (1 + self.params['xi_1'] * G + self.params['xi_2'] * P))
        
        # Equation 2.4: α-cell dynamics  
        I_term = max(0, self.params['I_hypo'] - I)
        dA_dt = (self.params['lambda_tilde_A'] * I_term / 
                (self.params['K_I'] + I_term) * 
                (1 / (1 + L / self.params['K_hat_L'])) - 
                self.params['mu_A'] * A)
        
        # Equation 2.5: Insulin dynamics
        dI_dt = (self.params['lambda_IB'] * B - 
                self.params['mu_I'] * I - 
                self.params['mu_IG'] * G * I)
        
        # Equation 2.6: GLUT-2 dynamics
        dU2_dt = self.params['lambda_U2C'] * C - self.params['mu_U2'] * U2
        
        # Equation 2.7: GLUT-4 dynamics (key equation for insulin resistance)
        dU4_dt = (self.params['lambda_U4_I'] * I * 
                 (1 / (1 + self.params['eta_T_alpha'] * T_alpha)) - 
                 self.params['mu_U4'] * U4)
        
        # Equation 2.8: Glucagon dynamics
        G_high_term = self.H(G - self.params['xi_4'])
        G_low_term = self.H(self.params['xi_3'] - G)
        dC_dt = (self.params['lambda_CA'] * A / 
                (1 + self.params['gamma_1'] * G_high_term * L) * 
                (1 + self.params['gamma_2'] * G_low_term * L) - 
                self.params['mu_C'] * C)
        
        # Equation 2.9: Blood glucose dynamics (central equation)
        dG_dt = (lambda_G / glucose_drug_inhibition - lambda_G_star + 
                self.params['lambda_G_star_U2'] * G_star * U2 / (self.params['K_U2'] + U2) - 
                self.params['lambda_GU4'] * G * U4 / (self.params['K_U4'] + U4))
        
        # Equation 2.10: Stored glucose (glycogen) dynamics
        dG_star_dt = (lambda_G_star + 
                     self.params['lambda_GU4'] * G * U4 / (self.params['K_U4'] + U4) - 
                     self.params['lambda_G_star_U2'] * G_star * U2 / (self.params['K_U2'] + U2))
        
        # Equation 2.11: Oleic acid dynamics
        dO_dt = lambda_O - self.params['mu_O'] * O
        
        # Equation 2.11: Palmitic acid dynamics
        dP_dt = lambda_P - self.params['mu_P'] * P
        
        # Equation 2.12: TNF-α dynamics (inflammation pathway)
        dT_alpha_dt = (self.params['lambda_T_alpha'] + 
                      self.params['lambda_T_alpha_P'] * P * 
                      (1 / (1 + O / self.params['K_hat_O'])) - 
                      self.params['mu_T_alpha'] * T_alpha)
        
        return [dL_dt, dA_dt, dB_dt, dI_dt, dU2_dt, dU4_dt, dC_dt, dG_dt, dG_star_dt, dO_dt, dP_dt, dT_alpha_dt]
    
    def get_initial_conditions(self):
        """Get physiologically appropriate initial conditions"""
        diabetes_type = self.patient_data.diabetes_type
        bmi = self.patient_data.bmi
        age = self.patient_data.age
        
        # Base initial conditions following paper's Table 4 and parameter estimation section
        if diabetes_type == "diabetic":
            # Diabetic initial conditions (higher glucose, lower β-cells, higher inflammation)
            base_conditions = [
                4.5e-15,   # L (GLP-1) - fasting level
                12e-12,    # A (α-cells) - elevated in diabetes
                4e-12,     # B (β-cells) - reduced in diabetes
                0.4e-13,   # I (insulin) - reduced in diabetes
                8.5e-6,    # U2 (GLUT-2)
                1.2e-6,    # U4 (GLUT-4) - reduced due to insulin resistance
                18e-16,    # C (glucagon) - elevated in diabetes
                1.8e-3,    # G (glucose) - diabetic level from paper simulations
                0.6e-3,    # G* (stored glucose)
                7.2e-7,    # O (oleic acid)
                2.8e-6,    # P (palmitic acid) - elevated in obesity/diabetes
                10e-12     # T_alpha (TNF-α) - elevated inflammation
            ]
        elif diabetes_type == "prediabetic":
            # Prediabetic initial conditions (intermediate values)
            base_conditions = [
                4.5e-15,   # L
                9e-12,     # A - slightly elevated
                6e-12,     # B - moderately reduced
                0.7e-13,   # I - moderately reduced
                9.0e-6,    # U2
                1.8e-6,    # U4 - moderately reduced
                12e-16,    # C - moderately elevated
                1.15e-3,   # G - prediabetic level (100-125 mg/dL equivalent)
                0.45e-3,   # G*
                6.9e-7,    # O
                2.0e-6,    # P - moderately elevated
                8e-12      # T_alpha - moderately elevated
            ]
        else:  # Normal/healthy
            # Normal initial conditions from paper's healthy simulations
            base_conditions = [
                4.5e-15,   # L - normal fasting GLP-1
                6e-12,     # A - normal α-cell density
                10e-12,    # B - normal β-cell density
                1.0e-13,   # I - normal fasting insulin
                9.45e-6,   # U2 - normal GLUT-2 (K_U2 value)
                2.78e-6,   # U4 - normal GLUT-4 (K_U4 value)
                5.4e-16,   # C - normal fasting glucagon
                0.95e-3,   # G - normal fasting glucose (~95 mg/dL)
                0.3e-3,    # G* - normal liver glucose
                6.78e-7,   # O - normal oleic acid
                1.22e-6,   # P - normal palmitic acid
                6e-12      # T_alpha - normal TNF-α
            ]
        
        # Adjust for obesity (affects palmitic acid, TNF-α, and GLUT-4)
        if bmi >= 35:  # Severely obese
            base_conditions[10] *= 3.0  # Palmitic acid
            base_conditions[11] *= 2.5  # TNF-α
            base_conditions[5] *= 0.6   # GLUT-4
        elif bmi >= 30:  # Obese
            base_conditions[10] *= 2.5  # Palmitic acid
            base_conditions[11] *= 2.0  # TNF-α
            base_conditions[5] *= 0.7   # GLUT-4
        elif bmi >= 25:  # Overweight
            base_conditions[10] *= 1.8  # Palmitic acid
            base_conditions[11] *= 1.5  # TNF-α
            base_conditions[5] *= 0.85  # GLUT-4
        
        # Age-related adjustments
        if age >= 65:
            base_conditions[2] *= 0.8   # Reduced β-cells
            base_conditions[3] *= 0.9   # Reduced insulin
        elif age >= 45:
            base_conditions[2] *= 0.9   # Slightly reduced β-cells
        
        return base_conditions
    
    def simulate(self, hours=24, food_factor=1.0, palmitic_factor=1.0, drug_dosage=0.0, 
                 meal_times=None, meal_factors=None):
        """Run the enhanced diabetes simulation"""
        if meal_times is None:
            meal_times = [0, 6, 12, 18]
        if meal_factors is None:
            meal_factors = [1.0, 1.0, 2.0, 0.0]  # breakfast, lunch, dinner, night snack
        
        # High resolution time points (5-minute intervals)
        t = np.linspace(0, hours, int(hours * 12))
        
        # Get personalized initial conditions
        y0 = self.get_initial_conditions()
        
        try:
            # Solve ODE system with enhanced numerical stability
            result = solve_ivp(
                lambda t, y: self.ode_system(t, y, food_factor, palmitic_factor, 
                                           drug_dosage, meal_times, meal_factors),
                [0, hours],
                y0,
                t_eval=t,
                method='RK45',
                rtol=1e-8,
                atol=1e-10,
                max_step=0.1  # Ensure numerical stability
            )
            
            if not result.success:
                raise Exception(f"ODE solver failed: {result.message}")
            
            # Extract all 12 variables
            L, A, B, I, U2, U4, C, G, G_star, O, P, T_alpha = result.y
            
            # Convert to clinically meaningful units
            glucose_mg_dl = G * 180000      # Convert g/cm³ to mg/dL
            insulin_pmol_l = I * 6e15       # Convert g/cm³ to pmol/L
            glucagon_pg_ml = C * 3.5e15     # Convert g/cm³ to pg/mL
            glp1_pmol_l = L * 1e15          # Convert g/cm³ to pmol/L
            
            # Scale cellular densities for visualization
            beta_cells_scaled = B * 1e12
            alpha_cells_scaled = A * 1e12
            
            # Additional variables for comprehensive analysis
            glut2_density = U2 * 1e6        # Scale for visualization
            glut4_density = U4 * 1e6        # Scale for visualization
            palmitic_acid_mg_dl = P * 1e9   # Convert to more meaningful units
            oleic_acid_mg_dl = O * 1e9      # Convert to more meaningful units
            tnf_alpha_pg_ml = T_alpha * 1e12 # Convert to pg/mL
            stored_glucose_mg_dl = G_star * 180000  # Convert liver glucose
            
            # Enhanced A1C calculation using more accurate formula
            avg_glucose_mg_dl = np.mean(glucose_mg_dl)
            a1c_estimate = (avg_glucose_mg_dl + 46.7) / 28.7
            
            # Clinical diagnosis based on A1C and glucose patterns
            max_glucose = np.max(glucose_mg_dl)
            min_glucose = np.min(glucose_mg_dl)
            
            if a1c_estimate >= 6.5 or max_glucose >= 200:
                diagnosis = "Diabetic"
            elif a1c_estimate >= 5.7 or avg_glucose_mg_dl >= 100 or max_glucose >= 140:
                diagnosis = "Prediabetic"
            else:
                diagnosis = "Normal"
            
            # Generate optimal glucose trajectory for comparison
            optimal_glucose = self._generate_optimal_glucose(t, meal_times, meal_factors)
            
            # Create comprehensive result object
            result_obj = SimulationResult(
                time_points=t.tolist(),
                glucose=glucose_mg_dl.tolist(),
                insulin=insulin_pmol_l.tolist(),
                glucagon=glucagon_pg_ml.tolist(),
                glp1=glp1_pmol_l.tolist(),
                beta_cells=beta_cells_scaled.tolist(),
                alpha_cells=alpha_cells_scaled.tolist(),
                # Additional variables
                glut2=glut2_density.tolist(),
                glut4=glut4_density.tolist(),
                palmitic_acid=palmitic_acid_mg_dl.tolist(),
                oleic_acid=oleic_acid_mg_dl.tolist(),
                tnf_alpha=tnf_alpha_pg_ml.tolist(),
                stored_glucose=stored_glucose_mg_dl.tolist(),
                # Analysis data
                optimal_glucose=optimal_glucose,
                a1c_estimate=round(a1c_estimate, 2),
                diagnosis=diagnosis,
                patient_info=self._get_patient_info(),
                simulation_summary={},
                recommendations=self._generate_recommendations(glucose_mg_dl, a1c_estimate),
                risk_factors=self._identify_risk_factors()
            )
            
            # Generate comprehensive summary statistics
            result_obj.generate_summary()
            
            return result_obj
            
        except Exception as e:
            print(f"ODE solver error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Simulation failed: {str(e)}")
    
    def _generate_optimal_glucose(self, t, meal_times, meal_factors):
        """Generate optimal glucose trajectory for healthy individual"""
        optimal_G = []
        for time in t:
            base_glucose = 90  # mg/dL baseline for healthy individual
            glucose_response = base_glucose
            
            # Add meal responses
            for i, meal_time in enumerate(meal_times):
                if i >= len(meal_factors) or meal_factors[i] == 0:
                    continue  # Skip if no meal or meal factor is 0
                    
                time_in_day = time % 24
                if time_in_day >= meal_time:
                    time_since_meal = time_in_day - meal_time
                    if time_since_meal <= 4:  # 4-hour post-meal period
                        # Physiological glucose response curve
                        peak_time = 1.0  # Peak at 1 hour
                        if time_since_meal <= peak_time:
                            # Rising phase (0-1 hour)
                            peak_response = 30 * meal_factors[i] * (time_since_meal / peak_time)
                        else:
                            # Falling phase (1-4 hours)
                            peak_response = 30 * meal_factors[i] * math.exp(-(time_since_meal - peak_time) / 1.5)
                        glucose_response += peak_response
            
            # Add circadian rhythm (dawn phenomenon and evening rise)
            circadian_effect = 5 * math.sin(2 * math.pi * (time % 24) / 24 + math.pi)
            glucose_response += circadian_effect
            
            # Ensure physiological bounds
            optimal_G.append(max(70, min(140, glucose_response)))
        
        return optimal_G
    
    def _get_patient_info(self):
        """Get comprehensive patient information"""
        return {
            "name": self.patient_data.name,
            "age": self.patient_data.age,
            "gender": self.patient_data.gender,
            "bmi": self.patient_data.bmi,
            "bmi_category": self.patient_data.bmi_category,
            "diabetes_type": self.patient_data.diabetes_type,
            "diabetes_risk": self.patient_data.diabetes_risk,
            "activity_level": self.patient_data.activity_level,
            "medications": self.patient_data.medications,
            "smoking_status": self.patient_data.smoking_status,
            "family_history": self.patient_data.family_history,
            "obesity_multiplier": self.obesity_multiplier,
            "food_adaptation_factor": self.food_adaptation_factor
        }
    
    def _generate_recommendations(self, glucose_mg_dl, a1c_estimate):
        """Generate personalized clinical recommendations"""
        recommendations = []
        
        # BMI-based recommendations
        if self.patient_data.bmi >= 30:
            recommendations.append("Weight loss of 5-10% can significantly improve glucose control")
            recommendations.append("Consider structured weight management program")
        elif self.patient_data.bmi >= 25:
            recommendations.append("Moderate weight loss (3-5%) may improve insulin sensitivity")
        
        # Activity level recommendations
        if self.patient_data.activity_level == "sedentary":
            recommendations.append("Increase physical activity to at least 150 minutes of moderate exercise per week")
            recommendations.append("Consider resistance training 2-3 times per week")
        elif self.patient_data.activity_level in ["light", "moderate"]:
            recommendations.append("Consider adding high-intensity interval training for better glucose control")
        
        # Glucose pattern-based recommendations
        max_glucose = max(glucose_mg_dl)
        glucose_variability = np.std(glucose_mg_dl)
        
        if max_glucose > 180:
            recommendations.append("Post-meal glucose spikes detected - consider carbohydrate counting")
            recommendations.append("Meal timing optimization may help reduce glucose excursions")
        
        if glucose_variability > 30:
            recommendations.append("High glucose variability detected - focus on consistent meal timing")
            recommendations.append("Consider continuous glucose monitoring for better pattern recognition")
        
        # A1C-based recommendations
        if a1c_estimate >= 7.0:
            recommendations.append("A1C above target - medication optimization may be needed")
            recommendations.append("Consider diabetes education program")
        elif a1c_estimate >= 6.5:
            recommendations.append("Diabetes management requires lifestyle modifications and regular monitoring")
        elif a1c_estimate >= 5.7:
            recommendations.append("Prediabetes detected - lifestyle intervention can prevent progression")
        
        # Medication-specific recommendations
        if not self.patient_data.medications and self.patient_data.diabetes_type == "diabetic":
            recommendations.append("Consider discussing medication options with healthcare provider")
        
        # Lifestyle recommendations
        if self.patient_data.smoking_status == "smoker":
            recommendations.append("Smoking cessation is critical for diabetes management")
        
        if self.patient_data.meal_frequency < 3:
            recommendations.append("Regular meal timing (3 meals/day) can improve glucose stability")
        elif self.patient_data.meal_frequency > 6:
            recommendations.append("Consider consolidating to 3-4 regular meals for better glucose control")
        
        return recommendations
    
    def _identify_risk_factors(self):
        """Identify comprehensive risk factors"""
        risk_factors = []
        
        # Age risk
        if self.patient_data.age >= 45:
            risk_factors.append(f"Age {self.patient_data.age} years (≥45 increases diabetes risk)")
        
        # BMI risk
        if self.patient_data.bmi >= 30:
            risk_factors.append(f"Obesity (BMI {self.patient_data.bmi}) - major diabetes risk factor")
        elif self.patient_data.bmi >= 25:
            risk_factors.append(f"Overweight (BMI {self.patient_data.bmi}) - increased diabetes risk")
        
        # Family history
        if self.patient_data.family_history:
            risk_factors.append("Family history of diabetes - 2-6x increased risk")
        
        # Lifestyle factors
        if self.patient_data.activity_level == "sedentary":
            risk_factors.append("Sedentary lifestyle - increases insulin resistance")
        
        if self.patient_data.smoking_status == "smoker":
            risk_factors.append("Current smoking - 30-40% increased diabetes risk")
        elif self.patient_data.smoking_status == "former_smoker":
            risk_factors.append("Former smoker - residual increased risk")
        
        # Clinical indicators
        if self.patient_data.fasting_glucose and self.patient_data.fasting_glucose >= 100:
            risk_factors.append(f"Elevated fasting glucose ({self.patient_data.fasting_glucose} mg/dL)")
        
        if self.patient_data.a1c_level and self.patient_data.a1c_level >= 5.7:
            risk_factors.append(f"Elevated A1C ({self.patient_data.a1c_level}%)")
        
        # Metabolic factors
        if self.obesity_multiplier >= 100:
            risk_factors.append("Severe insulin resistance indicated by obesity level")
        elif self.obesity_multiplier >= 10:
            risk_factors.append("Moderate insulin resistance risk")
        
        return risk_factors