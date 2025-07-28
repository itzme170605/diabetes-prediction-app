import numpy as np
from scipy.integrate import odeint
from typing import Tuple, Dict, Any, Optional
from app.models.ode_model import ODEParameters
import logging

logger = logging.getLogger(__name__)

class T2DMODESolver:
    """Implements the 12-variable ODE model from the paper"""
    
    def __init__(self, params: ODEParameters):
        self.params = params
        
    def F(self, t: float, t0: float, t1: float) -> float:
        """Food intake function"""
        return 1.0 if t0 <= t <= t1 else 0.0
    
    def H(self, x: float) -> float:
        """Heaviside function"""
        return 1.0 if x > 0 else 0.0
    
    def hill_function(self, x: float, x0: float, n: int = 2) -> float:
        """Hill function for activation/inhibition"""
        return x**n / (x**n + x0**n)
    
    def system_odes(self, x: np.ndarray, t: float, 
                   meal_times: list, meal_factors: list,
                   food_factor: float, palmitic_factor: float,
                   drug_dosage: float = 0.0) -> np.ndarray:
        """
        System of ODEs for T2DM model
        Variables: [B, A, L, I, U2, U4, C, G, G*, Ta, O, P]
        """
        B, A, L, I, U2, U4, C, G, Gs, Ta, O, P = x
        D = drug_dosage  # Drug concentration
        
        # Food intake functions
        lambda_L = self.get_food_intake(t, meal_times, meal_factors, 'L', food_factor)
        lambda_G = self.get_food_intake(t, meal_times, meal_factors, 'G', food_factor)
        lambda_Gs = self.get_food_intake(t, meal_times, meal_factors, 'Gs', food_factor)
        lambda_O = self.get_food_intake(t, meal_times, meal_factors, 'O', food_factor)
        lambda_P = self.get_food_intake(t, meal_times, meal_factors, 'P', 
                                       food_factor, palmitic_factor)
        
        # GLP-1 equation with drug effect
        drug_effect_L = (1 + D / (self.params.K_D + D)) if D > 0 else 1.0
        dL = lambda_L * drug_effect_L - self.params.mu_LB * B * L - self.params.mu_LA * A * L
        
        # α-cells equation
        I_frac = max(self.params.I_hypo - I, 0) / (self.params.K_I + max(self.params.I_hypo - I, 0))
        L_inhibition = 1 / (1 + L / self.params.K_hat_L)
        dA = self.params.lambda_tilde_A * I_frac * L_inhibition - self.params.mu_A * A
        
        # β-cells equation
        L_frac = max(L - self.params.L_0, 0) / (self.params.K_L + max(L - self.params.L_0, 0))
        dB = self.params.lambda_tilde_B * L_frac - self.params.mu_B * B * (1 + self.params.xi_1 * G + self.params.xi_2 * P)
        
        # Insulin equation
        dI = self.params.lambda_IB * B - self.params.mu_I * I - self.params.mu_IG * G * I
        
        # GLUT transporters
        dU2 = self.params.lambda_U2C * C - self.params.mu_U2 * U2
        
        Ta_inhibition = 1 / (1 + self.params.eta_T_alpha * Ta)
        dU4 = self.params.lambda_U4_I * I * Ta_inhibition - self.params.mu_U4 * U4
        
        # Glucagon equation
        gamma1_effect = 1 + self.params.gamma_1 * self.H(G - self.params.xi_4) * L
        gamma2_effect = 1 + self.params.gamma_2 * self.H(self.params.xi_3 - G) * L
        dC = self.params.lambda_CA * A * gamma2_effect / gamma1_effect - self.params.mu_C * C
        
        # Glucose equations with drug effect
        drug_inhibition_G = 1 / (1 + D / self.params.K_hat_D) if D > 0 else 1.0
        U2_frac = U2 / (self.params.K_U2 + U2)
        U4_frac = U4 / (self.params.K_U4 + U4)
        
        dG = (lambda_G * drug_inhibition_G - lambda_Gs * G + 
              self.params.lambda_G_star_U2 * Gs * U2_frac - 
              self.params.lambda_GU4 * G * U4_frac)
        
        dGs = (lambda_Gs * G + self.params.lambda_GU4 * G * U4_frac - 
               self.params.lambda_G_star_U2 * Gs * U2_frac)
        
        # TNF-α equation
        O_inhibition = 1 / (1 + O / self.params.K_hat_O)
        dTa = (self.params.lambda_T_alpha + 
               self.params.lambda_T_alpha_P * P * O_inhibition - 
               self.params.mu_T_alpha * Ta)
        
        # Fatty acids
        dO = lambda_O - self.params.mu_O * O
        dP = lambda_P - self.params.mu_P * P
        
        return np.array([dB, dA, dL, dI, dU2, dU4, dC, dG, dGs, dTa, dO, dP])
    
    def get_food_intake(self, t: float, meal_times: list, meal_factors: list, 
                       substance: str, food_factor: float, 
                       palmitic_factor: float = 1.0) -> float:
        """Calculate food intake for different substances"""
        # Check if we're within 1 hour of any meal time
        t_mod = t % 24  # Convert to 24-hour cycle
        
        for i, meal_time in enumerate(meal_times):
            if abs(t_mod - meal_time) < 0.1:  # Within ~6 minutes of meal time
                factor = meal_factors[i] if i < len(meal_factors) else 0.0
                
                if substance == 'L':  # GLP-1
                    return self.params.gamma_L * factor * food_factor * self.F(t_mod, meal_time, meal_time + 1)
                elif substance == 'G':  # Glucose
                    return self.params.gamma_G * factor * food_factor * self.F(t_mod, meal_time, meal_time + 1)
                elif substance == 'Gs':  # Glucose elimination
                    return self.params.gamma_G_star * self.F(t_mod, meal_time + 1, meal_time + 3)
                elif substance == 'O':  # Oleic acid
                    return self.params.gamma_O * factor * food_factor * self.F(t_mod, meal_time, meal_time + 1)
                elif substance == 'P':  # Palmitic acid
                    base_rate = self.params.gamma_P
                    obesity_rate = self.params.gamma_P_hat * (palmitic_factor - 1.0)
                    return (base_rate + obesity_rate) * factor * food_factor * self.F(t_mod, meal_time, meal_time + 1)
        
        return 0.0
    
    def get_initial_conditions(self, patient_data: Dict[str, Any]) -> np.ndarray:
        """Set initial conditions based on patient data"""
        # Default healthy initial conditions
        B_0 = 13e-3     # β-cells
        A_0 = 5e-3      # α-cells
        L_0 = 4.5e-15   # GLP-1
        I_0 = 0.97e-13  # Insulin
        U2_0 = 9e-6     # GLUT-2
        U4_0 = 2.6e-6   # GLUT-4
        C_0 = 4.964e-16 # Glucagon
        G_0 = 0.95e-3   # Glucose (normal)
        Gs_0 = 0.9e-3   # Stored glucose
        Ta_0 = 5.65e-12 # TNF-α
        O_0 = 6.78e-7   # Oleic acid
        P_0 = 1.22e-6   # Palmitic acid
        
        # Adjust based on patient condition
        if patient_data.get('diabetes_type') == 'prediabetic':
            G_0 *= 1.15
            I_0 *= 1.2
        elif patient_data.get('diabetes_type') == 'diabetic':
            G_0 *= 1.8
            I_0 *= 0.8
            B_0 *= 0.7
        
        if patient_data.get('bmi', 25) > 30:  # Obese
            P_0 *= 2.0
            O_0 *= 2.0
            Ta_0 *= 1.3
        
        return np.array([B_0, A_0, L_0, I_0, U2_0, U4_0, C_0, G_0, Gs_0, Ta_0, O_0, P_0])
    
    def solve(self, t_span: np.ndarray, initial_conditions: np.ndarray,
              meal_times: list, meal_factors: list,
              food_factor: float, palmitic_factor: float,
              drug_dosage: float = 0.0) -> np.ndarray:
        """Solve the ODE system"""
        
        solution = odeint(
            self.system_odes,
            initial_conditions,
            t_span,
            args=(meal_times, meal_factors, food_factor, palmitic_factor, drug_dosage),
            mxstep=50000
        )
        
        return solution