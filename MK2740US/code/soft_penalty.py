import numpy as np
from scipy.optimize import minimize
import pandas as pd

# === Inputs ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])
market_shares_raw = np.array([26, 26, 15, 19, 3, 29])
market_shares = market_shares_raw / np.sum(market_shares_raw)

n = len(royalties)

p_min, p_max = 8.99, 50

# Penalty weights for soft constraints
lambda_p = 0.005      # price inflation penalty
kappa_gap = 5000.0   # penalty weight for price gap violations
kappa_royalty = 5000.0  # penalty weight for royalty ordering violations

delta = 0.05   # min price gap in normalized x
epsilon = 0.1  # min royalty difference

beta = (-1, -1, 2.0)  # utility weights

unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

def logit_market_share(p, market_shares, royalties, beta):
    b1, b2, b3 = beta
    utility = b1 * royalties  + b3 * market_shares
    exp_utility = np.exp(utility - np.max(utility))
    return exp_utility / np.sum(exp_utility)

def penalty_price_gap(x):
    penalty = 0.0
    for i in range(n-1):
        diff = x[i+1] - x[i]
        if diff < delta:
            penalty += (delta - diff)**2
    return penalty

def penalty_royalty_order(x):
    penalty = 0.0
    for i in range(n-1):
        p_i = p_min + x[i] * (p_max - p_min)
        p_j = p_min + x[i+1] * (p_max - p_min)
        val = royalties[i] * p_i - royalties[i+1] * p_j
        if val < epsilon:
            penalty += (epsilon - val)**2
    return penalty

def objective(x):
    p = p_min + x * (p_max - p_min)
    logit_shares = logit_market_share(p, market_shares, royalties, beta)
    expected_royalty = np.sum(royalties * p * logit_shares)
    price_penalty = lambda_p * np.sum(p)**2
    gap_penalty = kappa_gap * penalty_price_gap(x)
    royalty_penalty = kappa_royalty * penalty_royalty_order(x)

    obj = (-expected_royalty + price_penalty + gap_penalty + royalty_penalty) / n
    return obj

bounds = [(0.0, 1.0)] * n

result = minimize(
    objective,
    x_init,
    method='SLSQP',
    bounds=bounds,
    options={'disp': True}
)

if result.success:
    x_opt = result.x
    p_opt = p_min + x_opt * (p_max - p_min)

    logit_shares = logit_market_share(p_opt, market_shares, royalties, beta)
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
