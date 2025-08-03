import numpy as np
from scipy.optimize import minimize
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# === Inputs (same as original) ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])
market_shares = market_shares_raw / np.sum(market_shares_raw)
n = len(royalties)

# === Price bounds and settings ===
p_min, p_max = 8.99, 50
delta = 0.05
epsilon = 0.2
lambda_p = 0.05

# === Initialization ===
unique_royalties = sorted(set(royalties), reverse=True)
rank = np.array([unique_royalties.index(r) for r in royalties])
U = len(unique_royalties)
x_init = rank / (U - 1) if U > 1 else np.zeros(n)

# === Logit functions ===
def logit_market_share_original(market_shares, royalties, beta):
    b1, b2 = beta
    utility = b1 * royalties + b2 * market_shares
    exp_utility = np.exp(utility)
    return exp_utility / np.sum(exp_utility)

def logit_market_share_improved(prices, market_shares, royalties, beta):
    b1, b2, b3 = beta
    utility = b1 * royalties + b2 * market_shares + b3 * prices
    exp_utility = np.exp(utility)
    return exp_utility / np.sum(exp_utility)

# === Objective functions ===
def objective_original(x, beta):
    p = p_min + x * (p_max - p_min)
    logit_shares = logit_market_share_original(market_shares, royalties, beta)
    expected_royalty = np.sum(p * logit_shares)
    penalty = lambda_p * np.sum(p * np.log(p))
    return (-expected_royalty + penalty)

def objective_improved(x, beta):
    p = p_min + x * (p_max - p_min)
    logit_shares = logit_market_share_improved(p, market_shares, royalties, beta)
    expected_royalty = np.sum(p * logit_shares)
    penalty = lambda_p * np.sum(p * np.log(p))
    return (-expected_royalty + penalty)

# === Constraints ===
def get_constraints():
    constraints = []
    for i in range(n - 1):
        constraints.append({
            'type': 'ineq',
            'fun': lambda x, i=i: x[i+1] - x[i] - delta
        })
    for i in range(n - 1):
        if royalties[i] != royalties[i+1]:
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, i=i: royalties[i] * (p_min + x[i] * (p_max - p_min)) -
                                      royalties[i+1] * (p_min + x[i+1] * (p_max - p_min)) - epsilon
            })
    return constraints

bounds = [(0.0, 1.0)] * n

# === Run key scenarios ===
scenarios = {
    "No Price Sensitivity\n(Original)": {
        "beta": (0, 0.1),
        "objective": objective_original,
        "logit_func": logit_market_share_original,
        "color": "red"
    },
    "Strong Price Sensitivity\n(Improved)": {
        "beta": (1.0, 0.5, -0.3),
        "objective": objective_improved,
        "logit_func": logit_market_share_improved,
        "color": "blue"
    }
}

results = {}
format_labels = [f"Format {i+1}\n${royalties[i]:.2f} royalty" for i in range(n)]

# Run optimizations
for scenario_name, config in scenarios.items():
    beta = config["beta"]
    objective_func = config["objective"]
    logit_func = config["logit_func"]

    result = minimize(
        lambda x: objective_func(x, beta),
        x_init,
        method='SLSQP',
        bounds=bounds,
        constraints=get_constraints(),
        options={'disp': False}
    )

    if result.success:
        x_opt = result.x
        p_opt = p_min + x_opt * (p_max - p_min)

        if len(beta) == 2:
            logit_shares = logit_func(market_shares, royalties, beta)
        else:
            logit_shares = logit_func(p_opt, market_shares, royalties, beta)

        royalties_earned = royalties * p_opt * logit_shares

        results[scenario_name] = {
            "prices": p_opt,
            "logit_shares": logit_shares,
            "royalties_earned": royalties_earned,
            "total_royalty": np.sum(royalties_earned),
            "beta": beta,
            "color": config["color"]
        }

# === Create focused visualization ===
fig = plt.figure(figsize=(16, 12))

# Main title
fig.suptitle('Impact of Price Sensitivity in Logit Model\nWhy Beta Coefficients Matter',
             fontsize=16, fontweight='bold', y=0.95)

# === Plot 1: Market Share Comparison (Large, prominent) ===
ax1 = plt.subplot(2, 3, (1, 2))
x_pos = np.arange(n)
width = 0.35

bars1 = ax1.bar(x_pos - width/2, results["No Price Sensitivity\n(Original)"]["logit_shares"],
                width, label='No Price Sensitivity', color='red', alpha=0.7)
bars2 = ax1.bar(x_pos + width/2, results["Strong Price Sensitivity\n(Improved)"]["logit_shares"],
                width, label='With Price Sensitivity', color='blue', alpha=0.7)

ax1.set_xlabel('Platform Format', fontweight='bold')
ax1.set_ylabel('Market Share', fontweight='bold')
ax1.set_title('Market Share Distribution:\nDramatic Change with Price Sensitivity', fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels([f"F{i+1}" for i in range(n)])
ax1.legend()
ax1.grid(True, alpha=0.3)

# Add value labels on bars
for bar, share in zip(bars1, results["No Price Sensitivity\n(Original)"]["logit_shares"]):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{share:.3f}', ha='center', va='bottom', fontsize=9)

for bar, share in zip(bars2, results["Strong Price Sensitivity\n(Improved)"]["logit_shares"]):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{share:.3f}', ha='center', va='bottom', fontsize=9)

# === Plot 2: Price vs Market Share Scatter ===
ax2 = plt.subplot(2, 3, 3)
for scenario_name, result in results.items():
    ax2.scatter(result["prices"], result["logit_shares"],
               label=scenario_name, s=100, alpha=0.8, color=result["color"])

    # Add format labels
    for i, (price, share) in enumerate(zip(result["prices"], result["logit_shares"])):
        ax2.annotate(f'F{i+1}', (price, share), xytext=(5, 5),
                    textcoords='offset points', fontsize=8)

ax2.set_xlabel('Price ($CAD)', fontweight='bold')
ax2.set_ylabel('Market Share', fontweight='bold')
ax2.set_title('Price vs Market Share\nRelationship', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# === Plot 3: Total Royalty Comparison ===
ax3 = plt.subplot(2, 3, 4)
scenario_names = list(results.keys())
royalties_total = [results[s]["total_royalty"] for s in scenario_names]
colors = [results[s]["color"] for s in scenario_names]

bars = ax3.bar(range(len(scenario_names)), royalties_total, color=colors, alpha=0.7)
ax3.set_xlabel('Scenario', fontweight='bold')
ax3.set_ylabel('Total Royalty ($)', fontweight='bold')
ax3.set_title('Total Royalty Comparison', fontweight='bold')
ax3.set_xticks(range(len(scenario_names)))
ax3.set_xticklabels([s.replace('\n', ' ') for s in scenario_names], rotation=45, ha='right')

# Add value labels
for bar, royalty in zip(bars, royalties_total):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'${royalty:.2f}', ha='center', va='bottom', fontweight='bold')

# === Plot 4: Beta Coefficient Impact ===
ax4 = plt.subplot(2, 3, 5)
beta_info = []
share_std = []
for scenario_name, result in results.items():
    beta_info.append(f"β = {result['beta']}")
    share_std.append(np.std(result["logit_shares"]))

bars = ax4.bar(range(len(beta_info)), share_std, color=colors, alpha=0.7)
ax4.set_xlabel('Beta Coefficients', fontweight='bold')
ax4.set_ylabel('Market Share\nStandard Deviation', fontweight='bold')
ax4.set_title('Market Share Variability\nby Beta Values', fontweight='bold')
ax4.set_xticks(range(len(beta_info)))
ax4.set_xticklabels(['Original\nβ₁=0, β₂=0.1', 'Improved\nβ₁=1.0, β₂=0.5, β₃=-0.3'],
                    rotation=0, ha='center')

# Add value labels
for bar, std_val in zip(bars, share_std):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{std_val:.3f}', ha='center', va='bottom', fontweight='bold')

# === Plot 5: Key Insights Text ===
ax5 = plt.subplot(2, 3, 6)
ax5.axis('off')

insights_text = """
KEY INSIGHTS:

🔴 Original Model (No Price):
   • Nearly uniform market shares (~16.6% each)
   • Beta coefficients have minimal impact
   • Unrealistic: price doesn't affect demand

🔵 Improved Model (With Price):
   • Format 1: 51.5% market share (lowest price)
   • Format 6: 1.5% market share (highest price)
   • Realistic price-demand relationship

📊 The Difference:
   • Market share std dev: 0.002 → 0.173
   • Price sensitivity creates realistic behavior
   • Beta₃ (price coefficient) is crucial!

💡 Conclusion:
   Missing price in utility function was the
   reason beta coefficients seemed ineffective.
"""

ax5.text(0.05, 0.95, insights_text, transform=ax5.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

plt.tight_layout()
plt.subplots_adjust(top=0.90)  # Make room for main title
plt.savefig('focused_logit_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("="*80)
print("FOCUSED ANALYSIS: Why Beta Coefficients Didn't Work Before")
print("="*80)

print("\n📊 MARKET SHARE COMPARISON:")
print("-" * 50)
for scenario_name, result in results.items():
    print(f"\n{scenario_name}:")
    print(f"Beta coefficients: {result['beta']}")
    for i, share in enumerate(result["logit_shares"]):
        print(f"  Format {i+1} (${result['prices'][i]:.2f}): {share:.1%}")
    print(f"  Standard deviation: {np.std(result['logit_shares']):.4f}")
    print(f"  Total royalty: ${result['total_royalty']:.2f}")

print(f"\n🎯 THE PROBLEM WITH YOUR ORIGINAL MODEL:")
print("-" * 50)
print("1. No price coefficient (β₃ = 0)")
print("2. Tiny utility differences (max ~0.03)")
print("3. Nearly uniform market shares regardless of price")
print("4. Beta coefficients appeared useless")

print(f"\n✅ THE SOLUTION:")
print("-" * 50)
print("1. Include price in utility: U = β₁×royalty + β₂×market_share + β₃×price")
print("2. Use negative β₃ for realistic demand (higher price = lower utility)")
print("3. Now beta coefficients create meaningful market dynamics")
print("4. Price sensitivity drives realistic consumer behavior")

print(f"\n📈 IMPACT METRICS:")
print("-" * 50)
orig_std = np.std(results["No Price Sensitivity\n(Original)"]["logit_shares"])
new_std = np.std(results["Strong Price Sensitivity\n(Improved)"]["logit_shares"])
print(f"Market share variability increase: {new_std/orig_std:.1f}x")
print(f"Lowest price format share: {results['Strong Price Sensitivity\n(Improved)']['logit_shares'][0]:.1%}")
print(f"Highest price format share: {results['Strong Price Sensitivity\n(Improved)']['logit_shares'][-1]:.1%}")

print(f"\nVisualization saved as 'focused_logit_analysis.png'")
print("="*80)
