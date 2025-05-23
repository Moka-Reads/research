from dataset import df_google

import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

# Optional: check working directory
print("Saving to:", os.getcwd())

# 1. Scatter plot: Price vs. Pages
plt.figure(figsize=(8, 5))
plt.scatter(df_google['Pages'], df_google['PriceValue'], alpha=0.6)
plt.xlabel('Page Count')
plt.ylabel('Price ($)')
plt.title('Price vs. Page Count')
plt.grid(True)
plt.tight_layout()
plt.savefig('price_vs_pages.png', dpi=300)  # Save before show
plt.close()

# 2. Linear Regression
X = df_google[['Pages']].astype(float)
y = df_google['PriceValue']
model = LinearRegression().fit(X, y)
print(f"Linear Model: Price = {model.intercept_:.2f} + {model.coef_[0]:.4f} * Pages")

# 3. Regression Line Plot
plt.figure(figsize=(8, 5))
plt.scatter(X, y, alpha=0.5, label='Data')
plt.plot(X, model.predict(X), color='red', label='Regression Line')
plt.xlabel("Pages")
plt.ylabel("Price ($)")
plt.title("Linear Regression: Price vs. Pages")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('linear_regression_price_vs_pages.png', dpi=300)  # Save first
plt.close()

# 4. Price per Page Distribution
plt.figure(figsize=(8, 5))
plt.hist(df_google['PricePerPage'], bins=30, alpha=0.7)
plt.xlabel('Price per Page ($)')
plt.ylabel('Number of Books')
plt.title('Distribution of Price per Page')
plt.grid(True)
plt.tight_layout()
plt.savefig('price_per_page_distribution.png', dpi=300)
plt.close()

correlation = df_google['Pages'].corr(df_google['PricePerPage'])
print(f"Correlation between Page Count and Price/Page: {correlation:.3f}")
