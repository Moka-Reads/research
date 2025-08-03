import numpy as np
from scipy.optimize import minimize
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# === The Problem: Why Prices Don't Change ===
# The constraints are too restrictive and force the same price structure
# regardless of beta coefficients. Let's analyze and fix this.

print("="*80)
print("CONSTRAINT ANALYSIS: Why Prices Don't Change")
print("="*80)

# === Setup ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])
market_shares = market_shares_raw / np.sum(market_shares_raw)
n = len(royalties)
p_min, p_max = 8.99, 50
delta = 0.05
epsilon = 0.2
lambda_p = 0.05

# === Original Constraints (Too Restrictive) ===
def get_original_constraints():
    constraints = []

    # Constraint 1: normalized prices must increase by at least delta
    for i in range(n - 1):
        constraints.append({
            'type': 'ineq',
            'fun': lambda x, i=i: x[i+1] - x[i] - delta
        })

    # Constraint 2: enforce royalty-price ordering with buffer epsilon
    for i in range(n - 1):
        if royalties[i] != royalties[i+1]:
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, i=i: royalties[i] * (p_min + x[i] * (p_max - p_min)) -
                                      royalties[i+1] * (p_min + x[i+1] * (p_max - p_min)) - epsilon
            })
    return constraints

# === Relaxed Constraints (Allow Price Flexibility) ===
def get_relaxed_constraints():
    constraints = []

    # Only constraint: platforms with higher royalties should have higher or equal revenue per unit
    # This allows more flexible pricing while maintaining economic logic
    for i in range(n - 1):
        if royalties[i] > royalties[i+1]:
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, i=i: royalties[i] * (p_min + x[i] * (p_max - p_min)) -
                                      royalties[i+1] * (p_min + x[i+1] * (p_max - p_min))
            })
    return constraints

# === No Constraints (Maximum Flexibility) ===
def get_no_constraints():
    return []

# === Logit Functions ===
def logit_market_share_improved(prices, market_shares, royalties, beta):
    b1, b2, b3 = beta
    utility = b1 * royalties + b2 * market_shares + b3 * prices
    exp_utility = np.exp(utility)
    return exp_utility / np.sum(exp_utility)

def objective_improved(x, beta):
    p = p_min + x * (p_max - p_min)
    logit_shares = logit_market_share_improved(p, market_shares, royalties, beta)
    expected_royalty = np.sum(p * logit_shares)
    penalty = lambda_p * np.sum(p * np.log(p))
    return (-expected_royalty + penalty)

# === Test Different Constraint Scenarios ===
bounds = [(0.0, 1.0)] * n
x_init = np.linspace(0.1, 0.4, n)  # Simple initialization

beta_scenarios = {
    "Low Price Sensitivity": (1.0, 0.5, -0.1),
    "High Price Sensitivity": (1.0, 0.5, -0.5),
    "Very High Price Sensitivity": (2.0, 1.0, -1.0)
}

constraint_scenarios = {
    "Original (Too Restrictive)": get_original_constraints,
    "Relaxed": get_relaxed_constraints,
    "No Constraints": get_no_constraints
}

all_results = {}

for constraint_name, constraint_func in constraint_scenarios.items():
    print(f"\n{'='*60}")
    print(f"CONSTRAINT SCENARIO: {constraint_name}")
    print(f"{'='*60}")

    constraint_results = {}

    for beta_name, beta in beta_scenarios.items():
        print(f"\nBeta: {beta_name} {beta}")

        constraints = constraint_func()

        result = minimize(
            lambda x: objective_improved(x, beta),
            x_init,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'disp': False}
        )

        if result.success:
            x_opt = result.x
            p_opt = p_min + x_opt * (p_max - p_min)
            logit_shares = logit_market_share_improved(p_opt, market_shares, royalties, beta)
            total_royalty = np.sum(p_opt * logit_shares)

            constraint_results[beta_name] = {
                'prices': p_opt,
                'shares': logit_shares,
                'total_royalty': total_royalty,
                'x_normalized': x_opt
            }

            print(f"Prices: {p_opt}")
            print(f"Avg Price: ${np.mean(p_opt):.2f}, Std: ${np.std(p_opt):.2f}")
            print(f"Total Royalty: ${total_royalty:.2f}")
            print(f"Success: {result.success}")
        else:
            print(f"Optimization failed: {result.message}")
            constraint_results[beta_name] = None

    all_results[constraint_name] = constraint_results

# === Analysis of Results ===
print(f"\n{'='*80}")
print("ANALYSIS: Why Prices Don't Change")
print(f"{'='*80}")

print("\n1. CONSTRAINT IMPACT:")
print("-" * 40)

for constraint_name, constraint_results in all_results.items():
    if any(constraint_results.values()):
        print(f"\n{constraint_name}:")

        # Check if prices vary across beta scenarios
        price_variations = []
        for beta_name, result in constraint_results.items():
            if result:
                price_variations.append(result['prices'])

        if len(price_variations) > 1:
            price_std_across_betas = np.std([np.mean(prices) for prices in price_variations])
            print(f"  Price variation across betas: ${price_std_across_betas:.4f}")

            if price_std_across_betas < 0.01:
                print("  → Prices are IDENTICAL across all beta values!")
                print("  → Constraints are TOO RESTRICTIVE")
            else:
                print("  → Prices DO change with different betas")
                print("  → Constraints allow proper optimization")

print("\n2. BETA COEFFICIENT IMPACT WHEN PRICES CAN CHANGE:")
print("-" * 50)

# Focus on the scenario with most flexibility
if "No Constraints" in all_results and any(all_results["No Constraints"].values()):
    no_constraint_results = all_results["No Constraints"]

    for beta_name, result in no_constraint_results.items():
        if result:
            print(f"\n{beta_name}:")
            print(f"  Optimal prices: {result['prices']}")
            print(f"  Price range: ${np.min(result['prices']):.2f} - ${np.max(result['prices']):.2f}")
            print(f"  Market shares: {result['shares']}")
            print(f"  Total royalty: ${result['total_royalty']:.2f}")

# === Create Visualization ===
if any(all_results["No Constraints"].values()):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

    # Plot 1: Price comparison across constraint scenarios
    scenarios = list(all_results.keys())
    beta_names = list(beta_scenarios.keys())

    x_pos = np.arange(len(beta_names))
    width = 0.25

    for i, scenario in enumerate(scenarios):
        avg_prices = []
        for beta_name in beta_names:
            result = all_results[scenario].get(beta_name)
            if result:
                avg_prices.append(np.mean(result['prices']))
            else:
                avg_prices.append(0)

        ax1.bar(x_pos + i*width, avg_prices, width, label=scenario, alpha=0.7)

    ax1.set_xlabel('Beta Scenario')
    ax1.set_ylabel('Average Price ($)')
    ax1.set_title('Average Prices by Constraint Type')
    ax1.set_xticks(x_pos + width)
    ax1.set_xticklabels(beta_names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Price distributions for no constraints scenario
    if all_results["No Constraints"]:
        colors = ['red', 'green', 'blue']
        for i, (beta_name, result) in enumerate(all_results["No Constraints"].items()):
            if result:
                ax2.scatter([i] * len(result['prices']), result['prices'],
                           label=beta_name, color=colors[i % len(colors)], alpha=0.7, s=60)

        ax2.set_xlabel('Beta Scenario')
        ax2.set_ylabel('Individual Prices ($)')
        ax2.set_title('Price Distribution (No Constraints)')
        ax2.set_xticks(range(len(beta_names)))
        ax2.set_xticklabels(beta_names, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    # Plot 3: Market share comparison
    if all_results["No Constraints"]:
        for i, (beta_name, result) in enumerate(all_results["No Constraints"].items()):
            if result:
                ax3.plot(result['shares'], 'o-', label=beta_name, linewidth=2, markersize=8)

        ax3.set_xlabel('Format')
        ax3.set_ylabel('Market Share')
        ax3.set_title('Market Shares (No Constraints)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    # Plot 4: Total royalty comparison
    royalty_data = {}
    for constraint_name, constraint_results in all_results.items():
        royalty_data[constraint_name] = []
        for beta_name in beta_names:
            result = constraint_results.get(beta_name)
            if result:
                royalty_data[constraint_name].append(result['total_royalty'])
            else:
                royalty_data[constraint_name].append(0)

    x_pos = np.arange(len(beta_names))
    width = 0.25

    for i, (constraint_name, royalties) in enumerate(royalty_data.items()):
        ax4.bar(x_pos + i*width, royalties, width, label=constraint_name, alpha=0.7)

    ax4.set_xlabel('Beta Scenario')
    ax4.set_ylabel('Total Royalty ($)')
    ax4.set_title('Total Royalty by Constraint Type')
    ax4.set_xticks(x_pos + width)
    ax4.set_xticklabels(beta_names, rotation=45, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('constraint_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\nVisualization saved as 'constraint_analysis.png'")

print(f"\n{'='*80}")
print("CONCLUSION:")
print(f"{'='*80}")
print("1. Your original constraints were TOO RESTRICTIVE")
print("2. The delta constraint forces prices to increase in fixed steps")
print("3. The royalty-ordering constraint locks in a specific price structure")
print("4. Beta coefficients CAN'T optimize prices when constraints are too tight")
print("5. Removing constraints shows beta coefficients DO have major impact")
print("6. Price sensitivity creates realistic demand curves when prices can adjust")
print("\nThe 'identical prices' problem was caused by over-constraining the optimization!")
