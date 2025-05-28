import numpy as np
from scipy.optimize import minimize

# Inputs
royalties = np.array([0.925, 0.8, 0.7, 0.6, 0.55])
n = len(royalties)

# Global price bounds
p_min, p_max = 8.99, 50

# Constraint and penalty settings
delta = 0.05      # Minimum normalized price gap between x[i+1] and x[i]
epsilon = 0.25    # Minimum royalty difference between formats
lambda_p = 0.05   # Price penalty weight

# Initial guess based on margin rank
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(m) for m in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# Objective function: maximize royalty - lambda_p * price penalty
def objective(x):
    p = p_min + x * (p_max - p_min)
    royalty = np.dot(royalties, p)
    price_penalty = np.sum(p)**2  # Quadratic to increase impact
    return (-royalty + lambda_p * price_penalty) / n  # Scaled for stability

# Constraint: price ordering in normalized space
constraints = []
for i in range(n - 1):
    constraints.append({'type': 'ineq', 'fun': lambda x, i=i: x[i+1] - x[i] - delta})

# Constraint: royalty ordering
for i in range(n - 1):
    constraints.append({
        'type': 'ineq',
        'fun': lambda x, i=i: royalties[i] * (p_min + x[i] * (p_max - p_min)) -
                              royalties[i+1] * (p_min + x[i+1] * (p_max - p_min)) - epsilon
    })

# Bounds: normalized x values between 0 and 1
bounds = [(0.0, 1.0)] * n

# Run optimization
result = minimize(
    objective,
    x_init,
    method='SLSQP',
    bounds=bounds,
    constraints=constraints,
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

# import pandas as pd
# import ace_tools as tools

# # Convert to DataFrame for display
# if "Optimal prices" in result_data:
#     df_result = pd.DataFrame({
#         "Format": [f"Format {i+1}" for i in range(n)],
#         "x (normalized)": result_data["Optimal normalized x"],
#         "Price": result_data["Optimal prices"],
#         "Royalty": result_data["Royalty per format"]
#     })
#     df_result.loc["Total"] = ["", "", result_data["Total price"], result_data["Total royalty"]]
# else:
#     df_result = pd.DataFrame({"Error": [result_data["Optimization failed"]]})

# tools.display_dataframe_to_user(name="SLSQP Pricing Optimization Result", dataframe=df_result)
