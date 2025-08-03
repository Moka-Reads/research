import matplotlib.pyplot as plt
import numpy as np
market_shares_raw = np.array([26, 26, 15, 19, 3, 29])
market_shares = market_shares_raw / market_shares_raw.sum()

print(market_shares)
market_shares = np.sort(market_shares)
# let sensitivity be presented as a decay model
sensitivity_inv_root = 1/np.sqrt(market_shares)

alpha = 0.5
beta = 2
exp_decay = np.exp(-alpha * market_shares)
log_decay = 1/np.log(beta + market_shares)

# multiplication form 


plt.figure(figsize=(10, 6))
plt.plot(market_shares, sensitivity_inv_root, marker='o', linestyle='-', color='b')
plt.plot(market_shares, exp_decay, marker='o', linestyle='-', color='r')
plt.plot(market_shares, log_decay, marker='o', linestyle='-', color='g')
plt.title('Market Shares vs Sensitivity')
plt.xlabel('Market Share')
plt.ylabel('Sensitivity')
plt.grid(True)
plt.show()
