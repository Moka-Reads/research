import numpy as np
from scipy.optimize import minimize

# === Define the Platform class ===
class Platform:
    def __init__(self, name, royalty, market_share):
        self.name = name
        self.royalty = royalty
        self.market_share = market_share
        self.optimal_price = None
        self.earnings = None

    def set_price_and_earnings(self, price):
        self.optimal_price = price
        self.earnings = self.royalty * price * self.market_share

# === Initialize platforms ===
platforms = [
    Platform("MoKa Reads", 0.95, 5),
    Platform("Leanpub", 0.90, 10),
    Platform("Kobo", 0.70, 20),
    Platform("Google Books", 0.70, 15),
    Platform("B&N", 0.70, 5),
    Platform("KDP eBook", 0.70, 45)
]

# === Optimization settings ===
p_min, p_max = 9.99, 50.00
p_target = 13.99

def objective(prices):
    total_revenue = 0
    variance_penalty = 0
    deviation_penalty = 0

    for i, platform in enumerate(platforms):
        price = prices[i]
        r = platform.royalty
        m = platform.market_share
        total_revenue += r * price * m

        deviation_penalty += m * (price - p_target)**2
        variance_penalty += (price - np.mean(prices))**2

    # Negative revenue to maximize it (since we minimize the objective)
    return -total_revenue + 0.5 * deviation_penalty + 0.2 * variance_penalty

# Initial guess: all prices at target
p0 = np.array([p_target] * len(platforms))
bounds = [(p_min, p_max)] * len(platforms)

# Run optimization
result = minimize(objective, p0, bounds=bounds)
optimal_prices = result.x

# Assign optimal prices and earnings
for i, platform in enumerate(platforms):
    platform.set_price_and_earnings(optimal_prices[i])

# === Print results ===
print(f"{'Platform':<12} {'Price ($)':>10} {'Royalty':>10} {'Share':>8} {'Earnings':>12}")
print("-" * 56)
for p in platforms:
    print(f"{p.name:<12} {p.optimal_price:>10.2f} {p.royalty:>10.3f} {p.market_share:>8} {p.earnings:>12.2f}")

total_earnings = sum(p.earnings for p in platforms)
print("\nTotal Projected Earnings: ${:.2f}".format(total_earnings))
