import numpy as np
from scipy.optimize import minimize

# === Inputs ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])  # Used for beta tuning
market_shares = market_shares_raw / np.sum(market_shares_raw)
n = len(royalties)

p_min = 9.99
p_max = 49.99
price_target = 13.99
lambda_v = 0.1
lambda_d = 0.1

# === Smart initialization of x ===
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# === Price sensitivity based on royalty & market share
#r_norm = (max(royalties) - royalties) / (max(royalties) - min(royalties))
score = 0.5 * royalties + 0.5 * market_shares
beta_min, beta_max = 0.3, 1.5
beta = beta_min + (beta_max - beta_min) * score

# === Price and Logit Share functions
def price(x):
    return p_min + (p_max - p_min) * x

def logit_shares(x):
    p = price(x)
    v = -beta * p
    expv = np.exp(v - np.max(v))  # for numerical stability
    return expv / np.sum(expv)

# === Revenue using logit-based shares
def revenue(x):
    p = price(x)
    s = logit_shares(x)
    return np.sum(p * royalties * s)

def variance(x):
    return np.var(price(x))

def deviation(x):
    return (np.mean(price(x)) - price_target)**2

def objective(x):
    return -revenue(x) + lambda_v * variance(x) + lambda_d * deviation(x)

# === Optimization
def optimize():
    result = minimize(objective, x_init, method='SLSQP', bounds=[(0, 1)] * n)
    return result.x

x = optimize()
print("Prices:", price(x))
print("Logit Shares:", logit_shares(x))
print("Revenue:", revenue(x))
