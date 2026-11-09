import os
import pandas as pd

# Folder this script lives in (the CSV files should be here too)
folder = os.path.dirname(os.path.abspath(__file__))

date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]
number_cols = ["ClosePrice", "ListPrice", "LivingArea", "DaysOnMarket", "BedroomsTotal",
               "BathroomsTotalInteger", "Latitude", "Longitude", "rate_30yr_fixed"]

# Run the same cleaning steps for each dataset
for name in ["sold", "listings"]:
    print("\n" + "=" * 60)
    print("CLEANING:", name)
    print("=" * 60)

    # Load the file
    df = pd.read_csv(os.path.join(folder, name + "_enriched.csv"), low_memory=False)
    rows_before = len(df)
    print("Rows before:", rows_before)

    # 1. Convert date columns to datetime (bad dates become NaT = missing)
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 2. Remove columns that are not useful: more than 90% empty, or the same value in every row
    for col in list(df.columns):
        if col in date_cols or col in number_cols or col in ["PropertyType", "year_month"]:
            continue  # keep the important columns
        if df[col].isnull().mean() > 0.9:
            print("Dropping (over 90% empty):", col)
            df = df.drop(columns=col)
        elif df[col].nunique() <= 1:
            print("Dropping (same value in every row):", col)
            df = df.drop(columns=col)

    # 3. Make number columns numeric (text that is not a number becomes NaN)
    for col in number_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Missing values: remove duplicates, then drop rows missing the key columns
    n = len(df)
    df = df.drop_duplicates()
    print("Duplicate rows removed:", n - len(df))

    if name == "sold":
        key_cols = ["CloseDate", "ClosePrice"]
    else:
        key_cols = ["ListingContractDate"]
    for col in key_cols:
        if col in df.columns:
            n = len(df)
            df = df[df[col].notnull()]
            print("Rows dropped for missing", col + ":", n - len(df))

    # 5. Remove invalid numbers (~ means "not", so rows with a blank value are kept here)
    if "ClosePrice" in df.columns:
        n = len(df)
        df = df[~(df["ClosePrice"] <= 0)]
        print("Removed ClosePrice <= 0:", n - len(df))
    if "LivingArea" in df.columns:
        n = len(df)
        df = df[~(df["LivingArea"] <= 0)]
        print("Removed LivingArea <= 0:", n - len(df))
    if "DaysOnMarket" in df.columns:
        n = len(df)
        df = df[~(df["DaysOnMarket"] < 0)]
        print("Removed DaysOnMarket < 0:", n - len(df))
    for col in ["BedroomsTotal", "BathroomsTotalInteger"]:
        if col in df.columns:
            n = len(df)
            df = df[~(df[col] < 0)]
            print("Removed", col, "< 0:", n - len(df))

    # 6. Date order flags (True = the dates are in the wrong order)
    # Start with False for every row, then fill in the checks that are possible
    df["listing_after_close_flag"] = False
    df["purchase_after_close_flag"] = False
    df["negative_timeline_flag"] = False

    if "ListingContractDate" in df.columns and "CloseDate" in df.columns:
        df["listing_after_close_flag"] = df["ListingContractDate"] > df["CloseDate"]
    if "PurchaseContractDate" in df.columns and "CloseDate" in df.columns:
        df["purchase_after_close_flag"] = df["PurchaseContractDate"] > df["CloseDate"]

    # negative_timeline_flag: any date out of order (listing -> purchase -> close)
    df["negative_timeline_flag"] = df["listing_after_close_flag"] | df["purchase_after_close_flag"]
    if "ListingContractDate" in df.columns and "PurchaseContractDate" in df.columns:
        listing_after_purchase = df["ListingContractDate"] > df["PurchaseContractDate"]
        df["negative_timeline_flag"] = df["negative_timeline_flag"] | listing_after_purchase

    print("\nDate flag counts:")
    print("listing_after_close_flag:", df["listing_after_close_flag"].sum())
    print("purchase_after_close_flag:", df["purchase_after_close_flag"].sum())
    print("negative_timeline_flag:", df["negative_timeline_flag"].sum())

    # 7. Geographic flags (California is roughly lat 32.5 to 42, lon -124.5 to -114.1)
    lat = df["Latitude"]
    lon = df["Longitude"]
    df["missing_coords_flag"] = lat.isnull() | lon.isnull()
    df["zero_coords_flag"] = (lat == 0) | (lon == 0)
    df["positive_lon_flag"] = lon > 0
    inside_california = (lat >= 32.5) & (lat <= 42) & (lon >= -124.5) & (lon <= -114.1)
    df["out_of_state_flag"] = ~df["missing_coords_flag"] & ~df["zero_coords_flag"] \
        & ~df["positive_lon_flag"] & ~inside_california

    print("\nGeographic flag counts:")
    for col in ["missing_coords_flag", "zero_coords_flag", "positive_lon_flag", "out_of_state_flag"]:
        print(col + ":", df[col].sum())

    # Show some of the bad coordinate rows
    bad_coords = df[df["missing_coords_flag"] | df["zero_coords_flag"]
                    | df["positive_lon_flag"] | df["out_of_state_flag"]]
    print("Rows with invalid coordinates:", len(bad_coords))
    print(bad_coords[["Latitude", "Longitude"]].head(10))

    # 8. Confirm data types
    print("\nData types:")
    for col in date_cols + number_cols:
        if col in df.columns:
            print(col, "->", df[col].dtype)

    # Row counts and save
    print("\nRows before:", rows_before, "| Rows after:", len(df))
    df.to_csv(os.path.join(folder, name + "_cleaned.csv"), index=False)
    print("Saved", name + "_cleaned.csv")