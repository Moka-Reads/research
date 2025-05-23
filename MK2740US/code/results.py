from slsqp2 import result_data as slsqp_result
from trcp import result_data as trcp_result
import pandas as pd

# Build comparison table
df = pd.DataFrame({
    "Format": [f"Format {i+1}" for i in range(len(slsqp_result["Optimal prices"]))],
    "Price (SLSQP)": [round(price, 2) for price in slsqp_result["Optimal prices"]],
    "Royalty-per-Unit (SLSQP)": [round(royalty, 2) for royalty in slsqp_result["Royalty per format"]],
    "Price (TrustRegion)": [round(price, 2) for price in trcp_result["Optimal prices"]],
    "Royalty-per-Unit (TrustRegion)": [round(royalty, 2) for royalty in trcp_result["Royalty per format"]]
})

# Add totals
df.loc["Total"] = [
    "",
    round(slsqp_result["Total price"], 2),
    round(slsqp_result["Total royalty"], 2),
    round(trcp_result["Total price"], 2),
    round(trcp_result["Total royalty"], 2)
]

# Save to CSV
df.to_csv("pricing_comparison.csv", index=False)
print("✅ Comparison table saved to pricing_comparison.csv")