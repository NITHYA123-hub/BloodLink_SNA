
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

files = [
    BASE_DIR / "results" / "bloodlink_network_nodes.csv",
    BASE_DIR / "results" / "bloodlink_network_edges.csv"
]

for file in files:
    print("\n" + "=" * 50)
    print("FILE:", file.name)
    print("=" * 50)

    if file.exists():
        df = pd.read_csv(file)

        print("Shape:", df.shape)
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))
    else:
        print("FILE NOT FOUND:", file)
