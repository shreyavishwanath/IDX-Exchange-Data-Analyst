import os
import pandas as pd

folder = os.path.dirname(os.path.abspath(__file__))

# Load the cleaned sold data
df = pd.read_csv(os.path.join(folder, "sold_cleaned.csv"), low_memory=False)

# CSV files
for col in ["CloseDate", "PurchaseContractDate", "ListingContractDate"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# Treat an original list price of 0 as missing so we never divide by zero
original_price = df["OriginalListPrice"].where(df["OriginalListPrice"] > 0)
living_area = df["LivingArea"].where(df["LivingArea"] > 0)

# Price Ratio = ClosePrice / OriginalListPrice (negotiation strength)
df["price_ratio"] = df["ClosePrice"] / original_price

# Close to Original List Ratio uses the same formula in the handbook table
df["close_to_original_list_ratio"] = df["ClosePrice"] / original_price

# Price Per Sq Ft = ClosePrice / LivingArea
df["price_per_sqft"] = df["ClosePrice"] / living_area

# Days on Market - no new column needed

# Year, Month and YrMo from CloseDate
df["Year"] = df["CloseDate"].dt.year
df["Month"] = df["CloseDate"].dt.month
df["YrMo"] = df["CloseDate"].dt.strftime("%Y-%m")

# Listing to Contract Days = PurchaseContractDate - ListingContractDate
df["listing_to_contract_days"] = (df["PurchaseContractDate"] - df["ListingContractDate"]).dt.days

# Contract to Close Days = CloseDate - PurchaseContractDate
df["contract_to_close_days"] = (df["CloseDate"] - df["PurchaseContractDate"]).dt.days

# output
new_cols = ["price_ratio", "close_to_original_list_ratio", "price_per_sqft", "DaysOnMarket",
            "Year", "Month", "YrMo", "listing_to_contract_days", "contract_to_close_days"]
sample = df[["CloseDate", "ClosePrice"] + new_cols].head(10)
sample.to_csv(os.path.join(folder, "week6_sample_output.csv"), index=False)

# Null count for each new column to check they filled in
df[new_cols].isnull().sum().to_csv(os.path.join(folder, "week6_new_column_null_counts.csv"),
                                   header=["null_count"])

# segment analysis
segments = ["PropertyType", "PropertySubType", "CountyOrParish", "MLSAreaMajor",
            "ListOfficeName", "BuyerOfficeName"]

for col in segments:
    if col in df.columns:
        table = df.groupby(col).agg(
            sales=("ClosePrice", "count"),
            median_close_price=("ClosePrice", "median"),
            median_price_per_sqft=("price_per_sqft", "median"),
            median_days_on_market=("DaysOnMarket", "median"),
            median_price_ratio=("price_ratio", "median"),
        )
        table = table.sort_values("sales", ascending=False)
        table.to_csv(os.path.join(folder, "segment_" + col + ".csv"))

# Save the dataset with the new columns
df.to_csv(os.path.join(folder, "sold_cleaned_features.csv"), index=False)
print("Done. Saved sold_cleaned_features.csv, week6_sample_output.csv, "
      "week6_new_column_null_counts.csv and segment_*.csv")