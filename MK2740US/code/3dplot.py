import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# === Grid definition ===
m_values = np.linspace(0.01, 0.3, 100)   # market share range (as fractions)
r_values = np.linspace(0.3, 0.95, 100)   # royalty rate range
M, R = np.meshgrid(m_values, r_values)

# === Parameters ===
k = 1.0
gamma = 1.0
beta0 = 0
beta1 = 0.5
beta2 = 1
alpha_sigmoid = 20
beta_sigmoid = 10

# === Specific Data Points ===
royalties = np.array([0.925, 0.8, 0.7, 0.7, 0.7, 0.35])  # Royalty rates per platform
market_shares_raw = np.array([11, 11, 15, 19, 3, 29])    # 2022 market share data
market_shares = market_shares_raw / np.sum(market_shares_raw)  # Normalize to sum to 1

# === Raw Sensitivity Models ===
S1_raw = (1 - R)**gamma / M**k
S2_raw = np.exp(beta0) * M**beta1 * (1 - R)**beta2
S3_raw = (1 - R)**gamma / M**k
S3 = S3_raw / np.sum(S3_raw, axis=1, keepdims=True)  # Already [0, 1] row-normalized
S4 = 1 / (1 + np.exp(alpha_sigmoid * (M - 0.15) - beta_sigmoid * (1 - R)))  # Already [0, 1]

# === Normalize other models to [0, 1] ===
S1 = (S1_raw - np.min(S1_raw)) / (np.max(S1_raw) - np.min(S1_raw))
S2 = (S2_raw - np.min(S2_raw)) / (np.max(S2_raw) - np.min(S2_raw))

# === Calculate sensitivity values for specific data points ===
S1_points_raw = (1 - royalties)**gamma / market_shares**k
S2_points_raw = np.exp(beta0) * market_shares**beta1 * (1 - royalties)**beta2
S3_points_raw = (1 - royalties)**gamma / market_shares**k
S4_points = 1 / (1 + np.exp(alpha_sigmoid * (market_shares - 0.15) - beta_sigmoid * (1 - royalties)))

# Normalize points using same scaling as surfaces
S1_points = (S1_points_raw - np.min(S1_raw)) / (np.max(S1_raw) - np.min(S1_raw))
S2_points = (S2_points_raw - np.min(S2_raw)) / (np.max(S2_raw) - np.min(S2_raw))
S3_points = S3_points_raw / np.sum(S3_points_raw)  # Row-normalize like S3

# === 3D Plotting ===
fig = plt.figure(figsize=(24, 5))

# Plot 1
ax1 = fig.add_subplot(141, projection='3d')
ax1.plot_surface(M, R, S1, cmap='viridis', alpha=0.8)
ax1.scatter(market_shares, royalties, S1_points, color='red', s=100, alpha=1.0)
ax1.set_title("Inverse Power (Normalized)")
ax1.set_xlabel("Market Share (m)")
ax1.set_ylabel("Royalty Rate (r)")
ax1.set_zlabel("Sensitivity [0, 1]")

# Plot 2
ax2 = fig.add_subplot(142, projection='3d')
ax2.plot_surface(M, R, S2, cmap='plasma', alpha=0.8)
ax2.scatter(market_shares, royalties, S2_points, color='red', s=100, alpha=1.0)
ax2.set_title("Log-Log Elasticity (Normalized)")
ax2.set_xlabel("Market Share (m)")
ax2.set_ylabel("Royalty Rate (r)")
ax2.set_zlabel("Sensitivity [0, 1]")

# Plot 3
ax3 = fig.add_subplot(143, projection='3d')
ax3.plot_surface(M, R, S3, cmap='cividis', alpha=0.8)
ax3.scatter(market_shares, royalties, S3_points, color='red', s=100, alpha=1.0)
ax3.set_title("Normalized Sensitivity (Relative)")
ax3.set_xlabel("Market Share (m)")
ax3.set_ylabel("Royalty Rate (r)")
ax3.set_zlabel("Relative S [0, 1]")

# Plot 4
ax4 = fig.add_subplot(144, projection='3d')
ax4.plot_surface(M, R, S4, cmap='coolwarm', alpha=0.8)
ax4.scatter(market_shares, royalties, S4_points, color='red', s=100, alpha=1.0)
ax4.set_title("Sigmoid Sensitivity")
ax4.set_xlabel("Market Share (m)")
ax4.set_ylabel("Royalty Rate (r)")
ax4.set_zlabel("Sigmoid S [0, 1]")

plt.tight_layout()
plt.show()
