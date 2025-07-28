from dataclasses import dataclass
from typing import Optional

@dataclass
class ODEParameters:
    """Parameters for the 12-variable ODE model from the paper"""
    
    # Half-saturation constants (g/cm³)
    K_L: float = 1.7e-14
    K_hat_L: float = 1.7e-14
    K_U2: float = 9.45e-6
    K_U4: float = 2.78e-6
    K_I: float = 2e-13
    K_hat_O: float = 1.36e-6
    K_D: Optional[float] = 1e-7
    K_hat_D: Optional[float] = 1e-7
    
    # Activation rates (d⁻¹)
    lambda_tilde_A: float = 0.35
    lambda_tilde_B: float = 1.745e9
    gamma_L: float = 1.98e-13  # g/cm³ d⁻¹
    lambda_IB: float = 1.26e-8
    lambda_U4_I: float = 4.17e7
    lambda_U2C: float = 6.6e10
    lambda_CA: float = 1.65e-11
    gamma_G: float = 0.017  # g/cm³ d⁻¹
    gamma_G_star: float = 11.1
    gamma_O: float = 1.46e-4  # g/cm³ d⁻¹
    gamma_P: float = 1.83e-6  # g/cm³ d⁻¹
    gamma_P_hat: float = 5.72e-5  # g/cm³ d⁻¹ (obesity-prone)
    
    # Transport rates (d⁻¹)
    lambda_GU4: float = 1.548
    lambda_G_star_U2: float = 4.644
    lambda_T_alpha: float = 1.19e-9  # g/cm³ d⁻¹
    lambda_T_alpha_P: float = 3.26e-4
    
    # Decay/degradation rates (d⁻¹)
    mu_A: float = 8.32
    mu_B: float = 8.32
    mu_LB: float = 251  # cm³/g d⁻¹
    mu_LA: float = 251  # cm³/g d⁻¹
    mu_I: float = 198.04
    mu_U4: float = 1.85
    mu_U2: float = 4.62
    mu_C: float = 166.22
    mu_T_alpha: float = 199
    mu_O: float = 13.68
    mu_P: float = 12
    mu_D: Optional[float] = 0.139
    mu_IG: float = 6e5
    
    # Switch parameters
    gamma_1: float = 1e-14
    gamma_2: float = 1.2e-14
    xi_1: float = 1e12  # cm³/g
    xi_2: float = 1e12  # cm³/g
    xi_3: float = 1e-2  # g/cm³
    xi_4: float = 1e-4  # g/cm³
    eta_T_alpha: float = 1e10  # cm³/g
    I_hypo: float = 8e-14  # g/cm³
    L_0: float = 1.7e-14  # g/cm³
    
    # Patient-specific adjustments
    obesity_factor: float = 1.0
    age_factor: float = 1.0
    activity_factor: float = 1.0