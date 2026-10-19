import glob
import os
import sys
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:,.2f}".format)

# Look for sold files in the same folder as this script (not the terminal's folder)
folder = os.path.dirname(os.path.abspath(__file__))
all_csvs = sorted(glob.glob(os.path.join(folder, "*.csv")))
sold_files = [f for f in all_csvs
              if "sold" in os.path.basename(f).lower()
              and "filtered" not in os.path.basename(f).lower()]
print(f"Looking in: {folder}")
print(f"Found {len(sold_files)} sold files")
if not sold_files:
    print("No CSV with 'sold' in its name. CSVs in this folder:")
    for f in all_csvs:
        print("  ", os.path.basename(f))
    sys.exit(1)

# Read each file's property types
property_types = []
for sold_path in sold_files:
    sold_df = pd.read_csv(sold_path, low_memory=False)
    property_types.append(sold_df["PropertyType"])

# Join all files' property types
all_property_types = pd.concat(property_types, ignore_index=True)

# Count each property type (unique types found)
property_counts = all_property_types.value_counts(dropna=False)
print("\nProperty types before filtering:")
print(property_counts)

# Calculate residential percentage
residential_share = (all_property_types == "Residential").mean() * 100
print(f"\nResidential share of all sold rows: {residential_share:.2f}%")

# Combine all files into one dataframe
sold = pd.concat((pd.read_csv(f, low_memory=False) for f in sold_files), ignore_index=True)
print("\nColumns:", list(sold.columns))
print(sold.head())

# Filter to Residential
# before = len(sold)
#sold = sold[sold.PropertyType == "Residential"]
#print(f"\nFilter: PropertyType == 'Residential' -> {before} rows down to {len(sold)}")

# Null-count summary table
nulls = sold.isnull().sum()
null_table = pd.DataFrame({"null_count": nulls, "null_pct": nulls / len(sold) * 100})
print("\nNull-count summary:")
print(null_table.sort_values("null_pct", ascending=False))

# Missing value report: columns above 90% null
print("\nColumns above 90% null:")
flagged = null_table[null_table.null_pct > 90]
print(flagged if not flagged.empty else "None")

# Numeric distribution summary
cols = ["ClosePrice", "LivingArea", "DaysOnMarket"]
summary = sold[cols].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).T
summary["median"] = sold[cols].median()
print("\nNumeric distribution summary:")
print(summary[["min", "max", "mean", "median", "1%", "5%", "25%", "75%", "95%", "99%"]])

# Save filtered dataset
out_path = os.path.join(folder, "sold_residential_filtered.csv")
sold.to_csv(out_path, index=False)
print("\nSaved", out_path)