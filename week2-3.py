import pandas as pd
 
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:,.2f}".format)
 
# Load data
sold = pd.read_csv("sold.csv", low_memory=False)
 
# Inspect structure
print("Columns:", list(sold.columns))
print(sold.head())
 
# Unique property types
print("\nUnique PropertyType values:", sold["PropertyType"].unique())
 
# Filter to Residential
before = len(sold)
sold = sold[sold.PropertyType == "Residential"]
print(f"\nFilter: PropertyType == 'Residential' -> {before} rows down to {len(sold)}")

#  Columns above 90% null
print("\nColumns above 90% null:")
flagged = null_table[null_table.null_pct > 90]
print(flagged if not flagged.empty else "None")