import numpy as np
from scipy.optimize import minimize
import pandas as pd

# === Inputs ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])  # Royalty rates per platform
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])    # 2022 market share data
market_shares = market_shares_raw / np.sum(market_shares_raw)  # Normalize to sum to 1

n = len(royalties)

# === Global Price Bounds ===
p_min, p_max = 8.99, 50

# === Constraint and Penalty Settings ===
delta = 0.05    # Minimum normalized gap in x values
epsilon = 0.2    # Minimum royalty difference between adjacent platforms
lambda_p = 0.05  # Penalty for price inflation
beta = (0, 0.1)  # Coefficients for royalty, log(market_share)

# === Initialization Strategy ===
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# === Logit Market Share Function ===
def logit_market_share(market_shares, royalties, beta):
    """
    Computes logit-adjusted market shares based on utility model:
    U_i = beta1 * r_i + beta2 * m_i
    """
    b1, b2 = beta
    utility = b1 * royalties +  b2 * market_shares
    exp_utility = np.exp(utility)  # numerical stability
    return exp_utility / np.sum(exp_utility)

# === Objective Function using Logit-Adjusted Shares ===
def objective(x):
    p = p_min + x * (p_max - p_min)
    logit_shares = logit_market_share(market_shares, royalties, beta)
    expected_royalty = np.sum( p * logit_shares)
    penalty = lambda_p * np.sum(p*np.log(p))
    return (-expected_royalty + penalty)

# === Constraints ===
constraints = []

# Constraint: normalized prices must increase by at least delta
for i in range(n - 1):
    constraints.append({
        'type': 'ineq',
        'fun': lambda x, i=i: x[i+1] - x[i] - delta
    })

# Constraint: enforce royalty-price ordering with a buffer epsilon
for i in range(n - 1):
    if royalties[i] != royalties[i+1]:
        constraints.append({
            'type': 'ineq',
            'fun': lambda x, i=i: royalties[i] * (p_min + x[i] * (p_max - p_min)) -
                                  royalties[i+1] * (p_min + x[i+1] * (p_max - p_min)) - epsilon
        })

# === Bounds for normalized variables between 0 and 1 ===
bounds = [(0.0, 1.0)] * n

# === Run Optimization ===
result = minimize(
    objective,
    x_init,
    method='SLSQP',
    bounds=bounds,
    constraints=constraints,
    options={'disp': True}
)

# === Postprocess Results ===
if result.success:
    x_opt = result.x
    p_opt = p_min + x_opt * (p_max - p_min)

    logit_shares = logit_market_share(market_shares, royalties, beta)
    royalties_opt = royalties * p_opt * logit_shares
    total_royalty = np.sum(royalties_opt)
    total_price = np.sum(p_opt)

    df_result = pd.DataFrame({
        "Format": [f"Format {i+1}" for i in range(n)],
        "x (normalized)": x_opt,
        "Price ($CAD)": p_opt,
        "Logit Share": logit_shares,
        "Royalty Earned": royalties_opt
    })
    df_result.loc["Total"] = ["", "", total_price, "", total_royalty]
    print(df_result.to_string(index=False))
else:
    print("Optimization failed:", result.message)
