import numpy as np
from scipy.optimize import minimize

# === Inputs ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])  # Royalty rates per platform
market_shares_raw = np.array([26, 26, 15, 19, 3, 29])    # 2022 market share data
market_shares = market_shares_raw / np.sum(market_shares_raw)  # Normalize to sum to 1

n = len(royalties)

# === Global Price Bounds ===
p_min, p_max = 8.99, 50

# === Constraint and Penalty Settings ===
delta = 0.05     # Minimum normalized gap in x values
epsilon = 0.2    # Minimum royalty difference between adjacent platforms
lambda_p = 0.05  # Penalty for price inflation
alpha = 0.1      # Price sensitivity coefficient for logit model

# === Initialization Strategy ===
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# === Logit Market Share Function ===
# def logit_market_share(p, market_shares, alpha=0.1):
#     """
#     Computes logit-adjusted market shares:
#     Utility = log(market_share) - alpha * price
#     """
#     utility = np.log(market_shares + 1e-12) - alpha * p  # epsilon added to avoid log(0)
#     # beta1 = 0.0
#     # beta2 = 0.0
#     # beta3 = 0.0
#     # utility = beta1 * royalties + beta2 * np.log(p) + beta3 * np.log(market_shares)
#     exp_utility = np.exp(utility)
#     return exp_utility / np.sum(exp_utility)

def gain_loss_prob(p, ref_p, volatility, comp_discount, deal_prone,
                   gamma_gain=1.5, gamma_loss=1.5,
                   tau0_gain=0.1, tau0_loss=0.1):
    # Raw gain/loss
    gain = np.maximum(ref_p - p, 0)
    loss = np.maximum(p - ref_p, 0)

    # Probabilistic threshold
    threshold_gain = tau0_gain - 0.5 * volatility + 0.3 * deal_prone
    threshold_loss = tau0_loss + 0.5 * comp_discount - 0.3 * deal_prone

    # Probabilities using logistic CDF (sigmoid)
    prob_gain = 1 / (1 + np.exp(-(gain - threshold_gain) * 10))
    prob_loss = 1 / (1 + np.exp(-(loss - threshold_loss) * 10))

    return gain * prob_gain * gamma_gain, loss * prob_loss * gamma_loss


def logit_market_share(p, market_shares, ref_p, volatility, comp_discount, deal_prone,
                       alpha=0.1, gamma_gain=1.5, gamma_loss=1.5):
    gain_adj, loss_adj = gain_loss_prob(p, ref_p, volatility, comp_discount, deal_prone,
                                        gamma_gain, gamma_loss)
    utility = np.log(market_shares + 1e-12) - alpha * p + gain_adj - loss_adj
    exp_utility = np.exp(utility)
    return exp_utility / np.sum(exp_utility)


# === Objective Function using Logit-Adjusted Shares ===
def objective(x):
    p = p_min + x * (p_max - p_min)

    # Reference price and effects (could be dynamic if you have time series)
    volatility = np.full(n, 0.2)         # Replace with volatility proxy
    comp_discount = np.full(n, 0.3)      # Replace with average discount from others
    deal_prone = np.full(n, 0.6)         # Proxy for consumer base deal-proneness

    logit_shares = logit_market_share(p, market_shares, reference_prices,
                                      volatility, comp_discount, deal_prone,
                                      alpha=alpha)

    expected_royalty = np.sum(p * logit_shares * royalties)
    penalty = np.sum(np.log(p))**2  # Optional regularization
    return (-expected_royalty + penalty) / n

# def objective(x):
#     p = p_min + x * (p_max - p_min)
#     logit_shares = logit_market_share(p, market_shares, alpha=alpha)
#     expected_royalty = np.sum(p * logit_shares * royalties)
#     # penalty = np.sum(p)**2
#     return (-expected_royalty + np.sum(np.log(p))**2) / n

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
result_data = None
if result.success:
    x_opt = result.x
    p_opt = p_min + x_opt * (p_max - p_min)

    logit_shares = logit_market_share(p_opt, market_shares, alpha=alpha)
    royalties_opt = royalties * p_opt * logit_shares
    total_royalty = np.sum(royalties_opt)
    total_price = np.sum(p_opt)

    result_data = {
        "Optimal normalized x": x_opt,
        "Optimal prices": p_opt,
        "Logit shares": logit_shares,
        "Royalty per format": royalties_opt,
        "Total royalty": total_royalty,
        "Total price": total_price
    }
else:
    result_data = {
        "Optimization failed": result.message
    }

# === Optional Display ===
try:
    import pandas as pd

    if "Optimal prices" in result_data:
        df_result = pd.DataFrame({
            "Format": [f"Format {i+1}" for i in range(n)],
            "x (normalized)": result_data["Optimal normalized x"],
            "Price ($CAD)": result_data["Optimal prices"],
            "Logit Share": result_data["Logit shares"],
            "Royalty Earned": result_data["Royalty per format"]
        })
        df_result.loc["Total"] = ["", "", result_data["Total price"], "", result_data["Total royalty"]]
        print(df_result.to_string(index=False))
    else:
        print(result_data["Optimization failed"])
except ImportError:
    print("Install pandas to display table nicely.")
    print(result_data)
