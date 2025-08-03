import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Optional
import cvxpy as cp

@dataclass
class Platform:
    name: str
    royalty_rate: float  # e.g., 0.7 for 70%
    market_share: float  # normalized, should sum to 1.0
    is_own_store: bool = False

@dataclass
class PricingParameters:
    p_min: float = 9.99
    p_max: float = 49.99
    avg_market_price: float = 13.99
    min_revenue: float = 100.0
    demand_elasticity: float = 0.2

    # Objective weights
    alpha: float = 0.4  # Revenue weight
    beta: float = 0.3   # Price variance weight (minimize)
    gamma: float = 0.3  # Customer cost weight (minimize)

class EbookPricingOptimizer:
    def __init__(self, platforms: List[Platform], params: PricingParameters):
        self.platforms = platforms
        self.params = params
        self.n_platforms = len(platforms)

        # Normalize market shares if they don't sum to 1
        total_share = sum(p.market_share for p in platforms)
        if abs(total_share - 1.0) > 1e-6:
            for platform in self.platforms:
                platform.market_share /= total_share

    def demand_function(self, price: float) -> float:
        """Simple demand function: higher price = lower demand"""
        reference_price = self.params.avg_market_price
        return max(0.1, np.exp(-self.params.demand_elasticity * (price - reference_price)))

    def calculate_revenue(self, prices: np.ndarray) -> float:
        """Calculate total revenue across all platforms"""
        total_revenue = 0
        for i, platform in enumerate(self.platforms):
            demand = self.demand_function(prices[i])
            revenue = platform.royalty_rate * platform.market_share * prices[i] * demand
            total_revenue += revenue
        return total_revenue

    def calculate_price_variance(self, prices: np.ndarray) -> float:
        """Calculate price variance from market average"""
        return np.var(prices - self.params.avg_market_price)

    def calculate_customer_cost(self, prices: np.ndarray) -> float:
        """Calculate weighted average price customers pay"""
        weighted_price = sum(self.platforms[i].market_share * prices[i]
                           for i in range(self.n_platforms))
        return weighted_price

    def objective_function(self, prices: np.ndarray) -> float:
        """Multi-objective function (minimization form)"""
        revenue = self.calculate_revenue(prices)
        price_variance = self.calculate_price_variance(prices)
        customer_cost = self.calculate_customer_cost(prices)

        # Convert to minimization: maximize revenue = minimize -revenue
        objective = (-self.params.alpha * revenue +
                    self.params.beta * price_variance +
                    self.params.gamma * customer_cost)

        return objective

    def revenue_constraint(self, prices: np.ndarray) -> float:
        """Revenue must exceed minimum threshold"""
        return self.calculate_revenue(prices) - self.params.min_revenue

    def competitive_constraint(self, prices: np.ndarray) -> float:
        """No price should be more than 20% above market average"""
        max_allowed = 1.2 * self.params.avg_market_price
        return max_allowed - np.max(prices)

    def optimize_weighted_sum(self) -> Dict:
        """Solve using weighted sum method with scipy"""

        # Bounds for each platform's price
        bounds = [(self.params.p_min, self.params.p_max) for _ in range(self.n_platforms)]

        # Constraints
        constraints = [
            {'type': 'ineq', 'fun': self.revenue_constraint},
            {'type': 'ineq', 'fun': self.competitive_constraint}
        ]

        # Initial guess: start at market average
        x0 = np.full(self.n_platforms, self.params.avg_market_price)

        # Optimize
        result = minimize(
            self.objective_function,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )

        if result.success:
            prices = result.x
            return {
                'success': True,
                'prices': prices,
                'total_revenue': self.calculate_revenue(prices),
                'price_variance': self.calculate_price_variance(prices),
                'customer_cost': self.calculate_customer_cost(prices),
                'objective_value': result.fun,
                'platform_details': self._get_platform_details(prices)
            }
        else:
            return {
                'success': False,
                'message': result.message,
                'prices': result.x if hasattr(result, 'x') else None
            }

    def optimize_genetic_algorithm(self) -> Dict:
        """Alternative optimization using genetic algorithm"""

        bounds = [(self.params.p_min, self.params.p_max) for _ in range(self.n_platforms)]

        def constraint_penalty(prices):
            penalty = 0
            # Revenue constraint
            if self.revenue_constraint(prices) < 0:
                penalty += 1000 * abs(self.revenue_constraint(prices))
            # Competitive constraint
            if self.competitive_constraint(prices) < 0:
                penalty += 1000 * abs(self.competitive_constraint(prices))
            return penalty

        def penalized_objective(prices):
            return self.objective_function(prices) + constraint_penalty(prices)

        result = differential_evolution(
            penalized_objective,
            bounds,
            maxiter=300,
            popsize=15,
            seed=42
        )

        if result.success:
            prices = result.x
            return {
                'success': True,
                'prices': prices,
                'total_revenue': self.calculate_revenue(prices),
                'price_variance': self.calculate_price_variance(prices),
                'customer_cost': self.calculate_customer_cost(prices),
                'objective_value': self.objective_function(prices),
                'platform_details': self._get_platform_details(prices)
            }
        else:
            return {'success': False, 'message': 'Genetic algorithm failed to converge'}

    def pareto_analysis(self, n_points: int = 10) -> List[Dict]:
        """Generate different solutions by varying objective weights"""
        pareto_solutions = []

        # Vary the balance between revenue and customer cost
        alpha_values = np.linspace(0.2, 0.8, n_points)

        original_alpha = self.params.alpha
        original_gamma = self.params.gamma

        for alpha in alpha_values:
            # Keep beta constant, vary alpha and gamma
            self.params.alpha = alpha
            self.params.gamma = 1.0 - alpha - self.params.beta

            if self.params.gamma >= 0:  # Ensure valid weights
                solution = self.optimize_weighted_sum()
                if solution['success']:
                    solution['weight_alpha'] = alpha
                    solution['weight_gamma'] = self.params.gamma
                    pareto_solutions.append(solution)

        # Restore original weights
        self.params.alpha = original_alpha
        self.params.gamma = original_gamma

        return pareto_solutions

    def _get_platform_details(self, prices: np.ndarray) -> List[Dict]:
        """Get detailed results for each platform"""
        details = []
        for i, platform in enumerate(self.platforms):
            demand = self.demand_function(prices[i])
            revenue = platform.royalty_rate * platform.market_share * prices[i] * demand

            details.append({
                'platform': platform.name,
                'price': prices[i],
                'royalty_rate': platform.royalty_rate,
                'market_share': platform.market_share,
                'demand_multiplier': demand,
                'revenue_contribution': revenue,
                'is_own_store': platform.is_own_store
            })

        return details

    def sensitivity_analysis(self) -> Dict:
        """Analyze sensitivity to key parameters"""
        base_solution = self.optimize_weighted_sum()
        if not base_solution['success']:
            return {'error': 'Base optimization failed'}

        sensitivity_results = {}

        # Test different demand elasticities
        elasticity_values = [0.1, 0.15, 0.2, 0.25, 0.3]
        original_elasticity = self.params.demand_elasticity

        sensitivity_results['elasticity'] = []
        for elasticity in elasticity_values:
            self.params.demand_elasticity = elasticity
            solution = self.optimize_weighted_sum()
            if solution['success']:
                sensitivity_results['elasticity'].append({
                    'elasticity': elasticity,
                    'revenue': solution['total_revenue'],
                    'avg_price': np.mean(solution['prices'])
                })

        # Restore original elasticity
        self.params.demand_elasticity = original_elasticity

        # Test different minimum revenue requirements
        revenue_values = [800, 1000, 1200, 1500, 2000]
        original_min_revenue = self.params.min_revenue

        sensitivity_results['min_revenue'] = []
        for min_rev in revenue_values:
            self.params.min_revenue = min_rev
            solution = self.optimize_weighted_sum()
            if solution['success']:
                sensitivity_results['min_revenue'].append({
                    'min_revenue': min_rev,
                    'achieved_revenue': solution['total_revenue'],
                    'customer_cost': solution['customer_cost']
                })

        # Restore original minimum revenue
        self.params.min_revenue = original_min_revenue

        return sensitivity_results


def create_sample_data():
    """Create sample platforms and parameters for testing"""
    platforms = [
        Platform("Amazon Kindle", 0.35, 0.45, False),
        Platform("Apple Books", 0.70, 0.25, False),
        Platform("Our Store", 0.95, 0.15, True),
        Platform("Kobo", 0.60, 0.10, False),
        Platform("Google Play", 0.52, 0.05, False)
    ]

    params = PricingParameters(
        p_min=6.99,
        p_max=18.99,
        avg_market_price=11.99,
        min_revenue=1500.0,
        demand_elasticity=0.2,
        alpha=0.5,  # Revenue focus
        beta=0.2,   # Price variance
        gamma=0.3   # Customer cost
    )

    return platforms, params


def main():
    print("=== EBOOK PRICING OPTIMIZATION (Simplified) ===\n")

    # Create sample data
    platforms, params = create_sample_data()

    # Initialize optimizer
    optimizer = EbookPricingOptimizer(platforms, params)

    print("Platform Configuration:")
    print("-" * 50)
    for platform in platforms:
        print(f"{platform.name:15} | Royalty: {platform.royalty_rate:.1%} | "
              f"Market Share: {platform.market_share:.1%}")

    print(f"\nParameters:")
    print(f"Price Range: ${params.p_min:.2f} - ${params.p_max:.2f}")
    print(f"Market Average: ${params.avg_market_price:.2f}")
    print(f"Min Revenue Target: ${params.min_revenue:.2f}")
    print(f"Weights - Revenue: {params.alpha:.1f}, Variance: {params.beta:.1f}, Customer: {params.gamma:.1f}")

    # 1. Weighted Sum Optimization
    print(f"\n1. WEIGHTED SUM OPTIMIZATION")
    print("=" * 50)

    result = optimizer.optimize_weighted_sum()

    if result['success']:
        print(f"✅ Optimization successful!")
        print(f"Total Revenue: ${result['total_revenue']:.2f}")
        print(f"Price Variance: {result['price_variance']:.3f}")
        print(f"Customer Cost: ${result['customer_cost']:.2f}")

        print(f"\nOptimal Prices by Platform:")
        for detail in result['platform_details']:
            print(f"{detail['platform']:15} | ${detail['price']:6.2f} | "
                  f"Revenue: ${detail['revenue_contribution']:6.2f}")
    else:
        print(f"❌ Optimization failed: {result['message']}")
        if result['prices'] is not None:
            print(f"Last attempt prices: {result['prices']}")

    # 2. Genetic Algorithm Comparison
    print(f"\n2. GENETIC ALGORITHM COMPARISON")
    print("=" * 50)

    ga_result = optimizer.optimize_genetic_algorithm()

    if ga_result['success']:
        print(f"✅ GA Optimization successful!")
        print(f"Total Revenue: ${ga_result['total_revenue']:.2f}")
        print(f"Customer Cost: ${ga_result['customer_cost']:.2f}")

        if result['success']:
            revenue_diff = ga_result['total_revenue'] - result['total_revenue']
            print(f"Revenue difference from SLSQP: ${revenue_diff:+.2f}")
    else:
        print(f"❌ GA failed: {ga_result['message']}")

    # 3. Pareto Analysis
    print(f"\n3. PARETO ANALYSIS")
    print("=" * 50)

    pareto_solutions = optimizer.pareto_analysis(n_points=5)

    if pareto_solutions:
        print("Trade-off Solutions (Revenue vs Customer Cost):")
        print("Revenue Weight | Customer Weight | Revenue | Customer Cost")
        print("-" * 55)
        for sol in pareto_solutions:
            print(f"{sol['weight_alpha']:11.2f} | {sol['weight_gamma']:13.2f} | "
                  f"${sol['total_revenue']:7.2f} | ${sol['customer_cost']:11.2f}")
    else:
        print("No valid Pareto solutions found")

    # 4. Sensitivity Analysis
    print(f"\n4. SENSITIVITY ANALYSIS")
    print("=" * 50)

    sensitivity = optimizer.sensitivity_analysis()

    if 'error' not in sensitivity:
        print("Demand Elasticity Impact:")
        for item in sensitivity['elasticity']:
            print(f"Elasticity {item['elasticity']:.2f}: Revenue=${item['revenue']:.2f}, "
                  f"Avg Price=${item['avg_price']:.2f}")

        print(f"\nMinimum Revenue Requirement Impact:")
        for item in sensitivity['min_revenue']:
            print(f"Min Revenue ${item['min_revenue']:.0f}: "
                  f"Achieved=${item['achieved_revenue']:.2f}, "
                  f"Customer Cost=${item['customer_cost']:.2f}")
    else:
        print(f"Sensitivity analysis failed: {sensitivity['error']}")


if __name__ == "__main__":
    main()
