import numpy as np
import pandas as pd
from pyDecision.algorithm import ahp_method

# === 1. Load Pairwise Matrix from CSV ===
# Format: A square matrix with no headers, where rows = criteria and values = pairwise comparisons

file_path = "insert file path"  # Change this to your actual file name
df = pd.read_csv(file_path, header=None)

# === 2. Convert all values to numeric (float), raise error if any non-numeric found ===
try:
    df = df.astype(float)
except ValueError as e:
    print("Error: Non-numeric values found in CSV. Please check your input file.")
    raise e

# === 3. Convert to NumPy array ===
dataset = df.to_numpy()

# === 4. Choose how weights are derived ===
weight_derivation = 'geometric'  # Options: 'mean', 'geometric', 'max_eigen'

# === 5. Run AHP method ===
weights, rc = ahp_method(dataset, wd=weight_derivation)

# === 6. Display Results ===
print("\nComputed Weights:")
for i in range(len(weights)):
    print(f"w(g{i+1}): {round(weights[i], 3)}")

# === 7. Consistency Check ===
print(f"\nConsistency Ratio (RC): {round(rc, 2)}")
if rc > 0.10:
    print("The solution is inconsistent. Review your pairwise comparisons.")
else:
    print("The solution is consistent.")

# === 8. Save weights to CSV ===
weights_df = pd.DataFrame(weights, columns=["Weight"])
weights_df.index = [f"Criterion_{i+1}" for i in range(len(weights))]
output_path = 'insert output path'
weights_df.to_csv(output_path)

print(f"\nWeights saved to: {output_path}")





