

import pandas as pd

file1 = "4CHP_Data.csv"
file2 = "housing.csv"

def compare_csv(file1, file2):
    print(f"\nComparing:\n - {file1}\n - {file2}\n")

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # 1) Compare columns
    print("=== COLUMN CHECK ===")
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)

    print("Columns only in File 1:", cols1 - cols2)
    print("Columns only in File 2:", cols2 - cols1)

    # 2) Compare row counts
    print("\n=== ROW COUNT CHECK ===")
    print(f"File 1 rows: {len(df1)}")
    print(f"File 2 rows: {len(df2)}")

    # 3) Compare entire dataframe
    print("\n=== FULL DATA CHECK ===")
    if df1.equals(df2):
        print("✔ The two CSV files are IDENTICAL.")
        return

    print("✘ The two CSV files are DIFFERENT.")

    # 4) Optional: show differences
    print("\n=== DETAILED DIFFERENCES (first 10 mismatched rows) ===")
    diff = df1.compare(df2)
    print(diff.head(10))

compare_csv(file1, file2)