import numpy as np
from scipy.optimize import minimize

# === Inputs ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])  # Royalty rates per platform
market_shares_raw = np.array([26, 26, 15, 19, 3, 29])   # 2022 market share data
market_shares = market_shares_raw / np.sum(market_shares_raw)  # Normalize to sum to 1

n = len(royalties)

# === Global Price Bounds ===
p_min, p_max = 8.99, 50

# === Constraint and Penalty Settings ===
delta = 0.05     # Minimum normalized gap in x values
epsilon = 0.25   # Minimum royalty difference between adjacent platforms
lambda_p = 0.05  # Penalty for price inflation
alpha = 0.1      # Price sensitivity coefficient for softmax

# === Sigmoid price sensitivity function ===
def sigmoid_price_sensitivity(p, L=1.0, k=0.3, p0=25):
    """
    Sigmoid demand decay function:
    Demand fraction drops from ~L to 0 around price p0 with steepness k.
    """
    return L / (1 + np.exp(k * (p - p0)))

# === Initialization Strategy ===
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# === Objective Function with Sigmoid + Softmax Market Share ===
def objective(x):
    p = p_min + x * (p_max - p_min)
    # Adjust base market shares by sigmoid price sensitivity
    adjusted_shares = market_shares * sigmoid_price_sensitivity(p, L=1.0, k=0.3, p0=25)
    # Softmax weighted shares reflecting competitive substitution
    weighted_exp = adjusted_shares * np.exp(-alpha * p)
    softmax_shares = weighted_exp / np.sum(weighted_exp)
    # Expected royalty weighted by price and platform shares
    expected_royalty = np.sum(royalties * p * softmax_shares)
    # Price penalty to discourage inflated prices
    price_penalty = np.sum(p) ** 2
    # Minimize negative profit plus penalty scaled by number of platforms
    return (-expected_royalty + lambda_p * price_penalty) / n

# === Constraints ===
constraints = []

# Constraint: normalized prices must increase by at least delta
for i in range(n - 1):
    constraints.append({
        'type': 'ineq',
        'fun': lambda x, i=i: x[i+1] - x[i] - delta
    })

# Constraint: ensure royalty * price ordering with epsilon buffer
for i in range(n - 1):
    if royalties[i] != royalties[i+1]:
        constraints.append({
            'type': 'ineq',
            'fun': lambda x, i=i: royalties[i] * (p_min + x[i] * (p_max - p_min)) -
                                  royalties[i+1] * (p_min + x[i+1] * (p_max - p_min)) - epsilon
        })

# === Bounds for normalized price variables (between 0 and 1) ===
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
result_data = None
if result.success:
    x_opt = result.x
    p_opt = p_min + x_opt * (p_max - p_min)

    # Calculate adjusted shares and final softmax shares
    adjusted_shares = market_shares * sigmoid_price_sensitivity(p_opt, L=1.0, k=0.3, p0=25)
    weighted_exp = adjusted_shares * np.exp(-alpha * p_opt)
    softmax_shares = weighted_exp / np.sum(weighted_exp)

    royalties_opt = royalties * p_opt
    total_royalty = np.sum(royalties_opt)
    total_price = np.sum(p_opt)

    result_data = {
        "Optimal normalized x": x_opt,
        "Optimal prices": p_opt,
        "Softmax shares": softmax_shares,
        "Royalty per format": royalties_opt,
        "Total royalty": total_royalty,
        "Total price": total_price
    }
else:
    result_data = {
        "Optimization failed": result.message
    }

# === Optional display with pandas if available ===
try:
    import pandas as pd

    if "Optimal prices" in result_data:
        df_result = pd.DataFrame({
            "Format": [f"Format {i+1}" for i in range(n)],
            "x (normalized)": result_data["Optimal normalized x"],
            "Price ($CAD)": result_data["Optimal prices"],
            "Softmax Share": result_data["Softmax shares"],
            "Royalty Earned": result_data["Royalty per format"]
        })
        df_result.loc["Total"] = ["", "", result_data["Total price"], "", result_data["Total royalty"]]
        print(df_result.to_string(index=False))
    else:
        print(result_data["Optimization failed"])
except ImportError:
    print("Install pandas to display table nicely.")
    print(result_data)
