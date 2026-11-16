import os
import pandas as pd

folder = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(os.path.join(folder, "sold_cleaned_features.csv"), low_memory=False)
rows_before = len(df)

cols = ["ClosePrice", "LivingArea", "DaysOnMarket"]
lines = []  # for everything in the report

# IQR method
# Step 1: flag extreme values
df["outlier_any_flag"] = False

lines.append("IQR outlier ranges")
for col in cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    # Percentiles to check the IQR range
    p1 = df[col].quantile(0.01)
    p99 = df[col].quantile(0.99)

    # True means this row is outside the IQR range for this column
    df[col + "_outlier_flag"] = (df[col] < lower) | (df[col] > upper)
    df["outlier_any_flag"] = df["outlier_any_flag"] | df[col + "_outlier_flag"]

    lines.append(col + ": IQR range " + str(round(lower, 2)) + " to " + str(round(upper, 2))
                 + " | 1st/99th percentile " + str(round(p1, 2)) + " / " + str(round(p99, 2))
                 + " | outliers flagged: " + str(df[col + "_outlier_flag"].sum()))

# Step 2: business rules (these values are always invalid)
df["invalid_flag"] = (df["ClosePrice"] <= 0) | (df["LivingArea"] <= 0) | (df["DaysOnMarket"] < 0)
lines.append("")
lines.append("Rows breaking business rules: " + str(df["invalid_flag"].sum()))
lines.append("Rows with any outlier flag: " + str(df["outlier_any_flag"].sum()))

# Step 3: the full dataset keeps every row, plus the flag columns
df.to_csv(os.path.join(folder, "sold_cleaned_flagged.csv"), index=False)

# Step 4: the filtered dataset leaves out flagged rows
filtered = df[~df["outlier_any_flag"] & ~df["invalid_flag"]]
filtered.to_csv(os.path.join(folder, "sold_cleaned_filtered.csv"), index=False)

# Step 5: compare before and after
lines.append("")
lines.append("Dataset size before filtering: " + str(rows_before) + " rows")
lines.append("Dataset size after filtering:  " + str(len(filtered)) + " rows")
lines.append("Rows removed: " + str(rows_before - len(filtered)))
lines.append("")
lines.append("Median before -> after filtering:")
for col in cols:
    lines.append("  " + col + ": " + str(round(df[col].median(), 2)) + " -> "
                 + str(round(filtered[col].median(), 2)))

# Write the report to a text file
with open(os.path.join(folder, "outlier_comparison.txt"), "w") as f:
    f.write("\n".join(lines))
print("Done. Saved sold_cleaned_flagged.csv, sold_cleaned_filtered.csv and outlier_comparison.txt")