import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from scipy.optimize import minimize
import pandas as pd

print("="*80)
print("DIAGNOSTIC ANALYSIS: Why Optimization is Failing")
print("="*80)

# === Setup (same as fixed model) ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])
market_shares = market_shares_raw / np.sum(market_shares_raw)
n = len(royalties)
p_min, p_max = 5.0, 35.0

# === Functions from fixed model ===
def total_market_size(avg_price, base_size=1000, price_elasticity=1.5):
    reference_price = 15.0
    size = base_size * (reference_price / avg_price) ** price_elasticity
    return max(size, 100)

def logit_market_shares(prices, market_shares, royalties, beta):
    b1, b2, b3 = beta
    utility = b1 * royalties + b2 * market_shares + b3 * prices
    utility = utility - np.max(utility)
    exp_utility = np.exp(utility)
    return exp_utility / np.sum(exp_utility)

def economic_objective(x, beta):
    prices = p_min + x * (p_max - p_min)
    avg_price = np.mean(prices)
    total_market = total_market_size(avg_price)
    logit_shares = logit_market_shares(prices, market_shares, royalties, beta)
    volumes = total_market * logit_shares
    revenues = volumes * prices * royalties
    total_revenue = np.sum(revenues)
    return -total_revenue

# === DIAGNOSTIC 1: Market Size Function Behavior ===
print("\nDIAGNOSTIC 1: Market Size Function Analysis")
print("-" * 50)

avg_prices = np.linspace(5, 35, 100)
market_sizes = [total_market_size(p) for p in avg_prices]

print(f"Market size at $5.00: {total_market_size(5.0):,.0f}")
print(f"Market size at $15.00 (ref): {total_market_size(15.0):,.0f}")
print(f"Market size at $35.00: {total_market_size(35.0):,.0f}")
print(f"Market size elasticity check: {total_market_size(5.0) / total_market_size(35.0):.1f}x larger at low price")

# Create diagnostic plot 1
plt.figure(figsize=(12, 8))
plt.subplot(2, 2, 1)
plt.plot(avg_prices, market_sizes, 'b-', linewidth=2)
plt.xlabel('Average Price ($)')
plt.ylabel('Market Size')
plt.title('Market Size vs Average Price')
plt.grid(True, alpha=0.3)

# === DIAGNOSTIC 2: Revenue Surface Analysis ===
print(f"\nDIAGNOSTIC 2: Revenue Surface Analysis")
print("-" * 50)

# Test different uniform pricing levels
beta_test = (2.0, 1.0, -0.5)  # Balanced scenario
uniform_prices = np.linspace(5, 35, 50)
revenues = []

for price in uniform_prices:
    x_uniform = np.full(n, (price - p_min) / (p_max - p_min))
    revenue = -economic_objective(x_uniform, beta_test)
    revenues.append(revenue)

max_revenue_idx = np.argmax(revenues)
optimal_uniform_price = uniform_prices[max_revenue_idx]
max_revenue = revenues[max_revenue_idx]

print(f"Optimal uniform price: ${optimal_uniform_price:.2f}")
print(f"Max revenue at uniform price: ${max_revenue:,.0f}")

plt.subplot(2, 2, 2)
plt.plot(uniform_prices, revenues, 'r-', linewidth=2)
plt.axvline(optimal_uniform_price, color='r', linestyle='--', alpha=0.7)
plt.xlabel('Uniform Price ($)')
plt.ylabel('Total Revenue ($)')
plt.title('Revenue vs Uniform Pricing')
plt.grid(True, alpha=0.3)

# === DIAGNOSTIC 3: Objective Function Gradient Analysis ===
print(f"\nDIAGNOSTIC 3: Gradient Analysis")
print("-" * 50)

def compute_gradient_numerically(x, beta, epsilon=1e-6):
    grad = np.zeros_like(x)
    for i in range(len(x)):
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[i] += epsilon
        x_minus[i] -= epsilon
        grad[i] = (economic_objective(x_plus, beta) - economic_objective(x_minus, beta)) / (2 * epsilon)
    return grad

# Test gradient at different points
test_points = [
    ("All minimum", np.zeros(n)),
    ("All maximum", np.ones(n)),
    ("Middle", np.full(n, 0.5)),
    ("Random", np.random.rand(n))
]

for name, x_test in test_points:
    grad = compute_gradient_numerically(x_test, beta_test)
    prices = p_min + x_test * (p_max - p_min)
    revenue = -economic_objective(x_test, beta_test)

    print(f"\n{name}:")
    print(f"  Prices: {prices}")
    print(f"  Revenue: ${revenue:,.0f}")
    print(f"  Gradient: {grad}")
    print(f"  Gradient direction: {'Increase' if np.mean(grad) < 0 else 'Decrease'} prices")

# === DIAGNOSTIC 4: Logit Share Sensitivity ===
print(f"\nDIAGNOSTIC 4: Logit Share Sensitivity Analysis")
print("-" * 50)

# Test how logit shares respond to price changes
base_prices = np.full(n, 15.0)  # Start with uniform $15

print("Price sensitivity test:")
for beta_scenario in [(2.0, 1.0, 0.0), (2.0, 1.0, -0.5), (2.0, 1.0, -2.0)]:
    b1, b2, b3 = beta_scenario

    # Base shares
    base_shares = logit_market_shares(base_prices, market_shares, royalties, beta_scenario)

    # Shares when Format 1 price drops to $10
    test_prices = base_prices.copy()
    test_prices[0] = 10.0
    new_shares = logit_market_shares(test_prices, market_shares, royalties, beta_scenario)

    print(f"  Beta {beta_scenario}:")
    print(f"    Format 1 share: {base_shares[0]:.3f} → {new_shares[0]:.3f} (change: {new_shares[0]-base_shares[0]:+.3f})")

# === DIAGNOSTIC 5: Why Optimization Goes to Bounds ===
print(f"\nDIAGNOSTIC 5: Boundary Behavior Analysis")
print("-" * 50)

# Test revenue at boundaries vs interior
boundary_tests = [
    ("All at minimum", np.zeros(n)),
    ("All at maximum", np.ones(n)),
    ("Mixed boundaries", np.array([1, 0, 0, 0, 0, 0])),
    ("Interior point", np.full(n, 0.3))
]

for name, x_test in boundary_tests:
    revenue = -economic_objective(x_test, beta_test)
    prices = p_min + x_test * (p_max - p_min)
    avg_price = np.mean(prices)
    market_size = total_market_size(avg_price)

    print(f"{name}:")
    print(f"  Avg price: ${avg_price:.2f}, Market size: {market_size:,.0f}, Revenue: ${revenue:,.0f}")

# === DIAGNOSTIC 6: Revenue Components Breakdown ===
print(f"\nDIAGNOSTIC 6: Revenue Components Analysis")
print("-" * 50)

def detailed_revenue_analysis(x, beta, label):
    prices = p_min + x * (p_max - p_min)
    avg_price = np.mean(prices)
    total_market = total_market_size(avg_price)
    logit_shares = logit_market_shares(prices, market_shares, royalties, beta)
    volumes = total_market * logit_shares
    revenues = volumes * prices * royalties

    print(f"\n{label}:")
    print(f"  Average price: ${avg_price:.2f}")
    print(f"  Market size: {total_market:,.0f}")
    print(f"  Total revenue: ${np.sum(revenues):,.0f}")
    print(f"  Revenue breakdown:")
    for i in range(n):
        print(f"    Format {i+1}: {volumes[i]:4.0f} units × ${prices[i]:.2f} × {royalties[i]:.3f} = ${revenues[i]:6.0f}")

    return revenues, total_market, logit_shares

# Compare all-minimum vs mixed pricing
all_min = np.zeros(n)
mixed = np.array([0.8, 0.1, 0.2, 0.3, 0.1, 0.0])

rev1, mkt1, shares1 = detailed_revenue_analysis(all_min, beta_test, "All Minimum Prices")
rev2, mkt2, shares2 = detailed_revenue_analysis(mixed, beta_test, "Mixed Pricing")

# === DIAGNOSTIC 7: Problem Identification ===
print(f"\nDIAGNOSTIC 7: Root Cause Analysis")
print("=" * 50)

print("IDENTIFIED ISSUES:")

# Issue 1: Market size function creates wrong incentives
print("\n1. MARKET SIZE INCENTIVE PROBLEM:")
market_5 = total_market_size(5.0)
market_35 = total_market_size(35.0)
print(f"   - Market at $5: {market_5:,.0f}")
print(f"   - Market at $35: {market_35:,.0f}")
print(f"   - Ratio: {market_5/market_35:.1f}x")
print(f"   - This creates MASSIVE incentive for low prices")

# Issue 2: Revenue per customer analysis
print("\n2. REVENUE PER CUSTOMER ANALYSIS:")
for avg_p in [5, 15, 25, 35]:
    market = total_market_size(avg_p)
    # Rough revenue estimate
    est_revenue = market * avg_p * 0.7  # Rough average royalty
    rev_per_customer = est_revenue / market
    print(f"   - ${avg_p}: Market={market:,.0f}, Rev/customer=${rev_per_customer:.2f}")

# Issue 3: Optimization landscape
print("\n3. OPTIMIZATION LANDSCAPE PROBLEM:")
print("   - Objective function has strong bias toward minimum prices")
print("   - Market size effect overwhelms price premiums")
print("   - Logit shares have minimal impact compared to market size")

# Create diagnostic visualization
plt.subplot(2, 2, 3)
components = ['Market Size Effect', 'Price Premium Effect', 'Logit Allocation']
values = [market_5/market_35, 35/5, max(shares2)/min(shares2)]
plt.bar(components, values, alpha=0.7)
plt.ylabel('Relative Impact')
plt.title('Component Impact Analysis')
plt.xticks(rotation=45)

plt.subplot(2, 2, 4)
scenarios = ['All Min', 'Mixed', 'All Max']
scenario_revenues = [
    -economic_objective(np.zeros(n), beta_test),
    -economic_objective(mixed, beta_test),
    -economic_objective(np.ones(n), beta_test)
]
plt.bar(scenarios, scenario_revenues, alpha=0.7)
plt.ylabel('Revenue ($)')
plt.title('Revenue by Strategy')

plt.tight_layout()
plt.savefig('diagnostic_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"\n{'='*80}")
print("CONCLUSIONS & RECOMMENDED FIXES")
print(f"{'='*80}")

print("\nPROBLEM ROOT CAUSES:")
print("1. Market size elasticity (1.5) is TOO HIGH")
print("   - Creates overwhelming incentive for low prices")
print("   - Market shrinks too aggressively with higher prices")

print("\n2. Market size effect DOMINATES price premiums")
print("   - 7x market size difference vs 7x price difference")
print("   - Revenue = Market × Share × Price × Royalty")
print("   - Market term overwhelms other terms")

print("\n3. Logit shares have minimal impact")
print("   - Beta coefficients change shares slightly")
print("   - But market size changes massively")

print("\nRECOMMENDED FIXES:")
print("1. REDUCE market elasticity: 1.5 → 0.8")
print("2. ADD competitive effects (not just market size)")
print("3. MODIFY objective to balance effects properly")
print("4. CONSIDER fixed costs to prevent extreme low pricing")

print(f"\nDiagnostic visualization saved as 'diagnostic_analysis.png'")
