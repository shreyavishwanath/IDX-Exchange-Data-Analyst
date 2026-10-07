import os
import pandas as pd
import glob

# Months: January 2024 through the most recently completed month (September 2026)
START = "2024-01"                                # from the assignment
END = "2026-03"                                 # last completed month
months = pd.period_range(START, END, freq="M").strftime("%Y%m")


def combine(prefix, label):
    frames = []
    for m in months:
        matches = glob.glob(f"{prefix}{m}*.csv")
        if len(matches) == 1:
            frames.append(pd.read_csv(matches[0], low_memory=False))
        elif len(matches) > 1:
            print(f"Multiple files for {prefix}{m}: {matches}, skipped. Pick one.")
        else:
            print(f"Missing file, skipped: {prefix}{m}")

    # Row count BEFORE concatenation (sum of all monthly files)
    before_concat = sum(len(f) for f in frames)
    print(f"{label}: {len(frames)} files, {before_concat:,} rows before concatenation")

    df = pd.concat(frames, ignore_index=True)

    # Row count AFTER concatenation (should match the number above)
    print(f"{label}: {len(df):,} rows after concatenation")

    # Row count BEFORE the Residential filter
    print(f"{label}: {len(df):,} rows before Residential filter")

    df = df[df["PropertyType"] == "Residential"]

    # Row count AFTER the Residential filter
    print(f"{label}: {len(df):,} rows after Residential filter\n")
    return df


sold = combine("CRMLSSold", "Sold")
listings = combine("CRMLSListing", "Listings")

sold.to_csv("CRMLSSold_Residential_Combined.csv", index=False)
listings.to_csv("CRMLSListing_Residential_Combined.csv", index=False)