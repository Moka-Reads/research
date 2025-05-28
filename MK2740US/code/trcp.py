import numpy as np
from scipy.optimize import minimize, NonlinearConstraint, Bounds

# Inputs
royalties = np.array([0.925, 0.8, 0.7, 0.6, 0.55])
n = len(royalties)
p_min, p_max = 8.99, 50
delta = 0.05
epsilon = 0.25
lambda_p = 0.05

# Smart initialization
rank = np.array([sorted(set(royalties), reverse=True).index(r) for r in royalties])
U = len(set(royalties))
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# Objective
def objective(x):
    p = p_min + x * (p_max - p_min)
    return (-np.dot(royalties, p) + lambda_p * np.sum(p)**2) / n

# Constraints
def price_gap(x): return x[1:] - x[:-1] - delta
def royalty_order(x):
    p = p_min + x * (p_max - p_min)
    return royalties[:-1] * p[:-1] - royalties[1:] * p[1:] - epsilon

constraints = [
    NonlinearConstraint(price_gap, 0, np.inf),
    NonlinearConstraint(royalty_order, 0, np.inf)
]

bounds = Bounds([0.0]*n, [1.0]*n)

# Solve
result = minimize(
    objective, x_init, method='trust-constr',
    bounds=bounds, constraints=constraints,
    options={'disp': True}
)

result_data = None
# Process result
if result.success:
    x_opt = result.x
    p_opt = p_min + x_opt * (p_max - p_min)
    royalties = royalties * p_opt
    total_royalty = np.sum(royalties)
    total_price = np.sum(p_opt)

    result_data = {
        "Optimal normalized x": x_opt,
        "Optimal prices": p_opt,
        "Royalty per format": royalties,
        "Total royalty": total_royalty,
        "Total price": total_price
    }
else:
    result_data = {
        "Optimization failed": result.message
    }