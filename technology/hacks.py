import pandas as pd

# Load your dataset
df = pd.read_csv("technology\Global_Cybersecurity_Threats_2015-2024.csv")

# Ensure numeric columns are correct
df["Financial Loss (in Million $)"] = pd.to_numeric(df["Financial Loss (in Million $)"], errors="coerce")
df["Incident Resolution Time (in Hours)"] = pd.to_numeric(df["Incident Resolution Time (in Hours)"], errors="coerce")

# Drop rows with missing critical values
df.dropna(subset=["Country", "Target Industry", "Financial Loss (in Million $)"], inplace=True)

# === 1. Total Financial Loss by Country and Sector ===
agg_df = df.groupby(["Country", "Target Industry"]).agg({
    "Financial Loss (in Million $)": "sum",
    "Incident Resolution Time (in Hours)": "mean",
    "Number of Affected Users": "sum",
    "Attack Type": "count"
}).rename(columns={"Attack Type": "Incident Count"}).reset_index()

# === 2. Identify Worst Hit Country + Sector ===
worst = agg_df.sort_values("Financial Loss (in Million $)", ascending=False).head(10)

# Display top 10 worst-hit combinations
print("\nTop 10 Worst-Hit Country & Industry Combinations (by Financial Loss):")
print(worst.to_string(index=False))
