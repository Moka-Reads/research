import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import os

# === Inputs ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])  # Used for beta tuning
market_shares = market_shares_raw / np.sum(market_shares_raw)
n = len(royalties)

# Platform names from figures/prices.csv
platforms = ['MoKa Reads', 'Leanpub', 'Kobo', 'Google Books', 'Barnes & Noble', 'Amazon (KDP)']

p_min, p_max = 8.99, 49.99
price_target = 13.69
lambda_v = 0.1
lambda_e = 0.1
omega_r = 0.5
omega_m = 0.5
beta_min, beta_max = 0.8, 1.5
# === Smart initialization of x ===
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# === Price sensitivity based on royalty & market share
#r_norm = (max(royalties) - royalties) / (max(royalties) - min(royalties))
score = omega_r * royalties + omega_m * market_shares
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
    return -revenue(x) + lambda_v * variance(x) + lambda_e * deviation(x)

# === Optimization
def optimize():
    result = minimize(objective, x_init, method='SLSQP', bounds=[(0, 1)] * n)
    return result.x

x = optimize()
print("Prices:", price(x))
print("Logit Shares:", logit_shares(x))
print("Revenue:", revenue(x))

# === Simple Weight Impact Analysis ===
def analyze_weight_effects():
    # Test key weight scenarios: Pure Market Share, Current (50/50), Pure Royalty
    weight_scenarios = [0.0, 0.25, 0.5, 0.75, 1.0]
    scenario_names = ['Pure Market Share', '25% Royalty', 'Current (50/50)', '75% Royalty', 'Pure Royalty']

    results = {}

    print("\n=== WEIGHT RATIO IMPACT ON PRICES ===")
    print("Royalty Weight | " + " | ".join([f"{platforms[i]:>12}" for i in range(n)]) + " | Total Revenue")
    print("-" * (15 + 14 * n + 15))

    for i, w in enumerate(weight_scenarios):
        # Calculate beta with current weight
        score = w * royalties + (1 - w) * market_shares
        beta_current = beta_min + (beta_max - beta_min) * score

        # Redefine functions with current beta
        def logit_shares_current(x):
            p = price(x)
            v = -beta_current * p
            expv = np.exp(v - np.max(v))
            return expv / np.sum(expv)

        def revenue_current(x):
            p = price(x)
            s = logit_shares_current(x)
            return np.sum(p * royalties * s)

        def objective_current(x):
            return -revenue_current(x) + lambda_v * variance(x) + lambda_e * deviation(x)

        # Optimize with current beta
        result = minimize(objective_current, x_init, method='SLSQP', bounds=[(0, 1)] * n)
        x_opt = result.x

        # Store results
        prices = price(x_opt)
        shares = logit_shares_current(x_opt)
        rev = revenue_current(x_opt)

        results[w] = {'prices': prices, 'shares': shares, 'revenue': rev}

        # Print results in table format
        price_str = " | ".join([f"${p:>6.2f}" for p in prices])
        print(f"{scenario_names[i]:>14} | {price_str} | ${rev:>11.2f}")

    # Create figures directory if it doesn't exist
    os.makedirs('../figures', exist_ok=True)

    # Plot 1: Price impact
    plt.figure(figsize=(10, 6))
    for j in range(n):
        prices_for_product = [results[w]['prices'][j] for w in weight_scenarios]
        plt.plot(weight_scenarios, prices_for_product, 'o-', linewidth=3, markersize=8,
                label=platforms[j])

    plt.xlabel('Weight Ratio (0=Market Share Focus, 1=Royalty Focus)', fontsize=12)
    plt.ylabel('Optimized Price ($)', fontsize=12)
    plt.title('How Weight Ratio Affects Optimized Prices', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('figures/price_impact_by_weight.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Plot 2: Revenue impact
    plt.figure(figsize=(8, 6))
    revenues = [results[w]['revenue'] for w in weight_scenarios]
    plt.plot(weight_scenarios, revenues, 'ro-', linewidth=4, markersize=10)
    plt.xlabel('Weight Ratio', fontsize=12)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    plt.title('Revenue vs Weight Ratio', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('figures/revenue_vs_weight.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Plot 3: Price change from current (50/50)
    plt.figure(figsize=(10, 6))
    current_prices = results[0.5]['prices']
    for j in range(n):
        price_changes = [(results[w]['prices'][j] - current_prices[j]) for w in weight_scenarios]
        plt.plot(weight_scenarios, price_changes, 'o-', linewidth=2, markersize=6,
                label=platforms[j])

    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    plt.xlabel('Weight Ratio', fontsize=12)
    plt.ylabel('Price Change from Current ($)', fontsize=12)
    plt.title('Price Change from Current 50/50 Mix', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('figures/price_change_from_current.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Plot 4: Input data context
    plt.figure(figsize=(10, 6))
    x_pos = np.arange(n)
    width = 0.35
    plt.bar(x_pos - width/2, royalties, width, label='Royalties', alpha=0.8, color='skyblue')
    plt.bar(x_pos + width/2, market_shares, width, label='Market Shares', alpha=0.8, color='lightcoral')
    plt.xlabel('Platform', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.title('Input Data Context', fontsize=14, fontweight='bold')
    plt.legend()
    plt.xticks(x_pos, [platforms[i][:8] + '...' if len(platforms[i]) > 8 else platforms[i] for i in range(n)], rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('figures/input_data_context.png', dpi=300, bbox_inches='tight')
    plt.show()

    # Key insights
    print(f"\n=== KEY INSIGHTS ===")
    best_rev_weight = max(results.keys(), key=lambda w: results[w]['revenue'])
    worst_rev_weight = min(results.keys(), key=lambda w: results[w]['revenue'])

    print(f"• Best revenue at weight {best_rev_weight}: ${results[best_rev_weight]['revenue']:.2f}")
    print(f"• Worst revenue at weight {worst_rev_weight}: ${results[worst_rev_weight]['revenue']:.2f}")
    print(f"• Revenue difference: ${results[best_rev_weight]['revenue'] - results[worst_rev_weight]['revenue']:.2f}")

    print(f"\n• Platforms most affected by weight change:")
    for j in range(n):
        price_range = max([results[w]['prices'][j] for w in weight_scenarios]) - min([results[w]['prices'][j] for w in weight_scenarios])
        print(f"  {platforms[j]}: ${price_range:.2f} price range")

# Run the analysis
analyze_weight_effects()
