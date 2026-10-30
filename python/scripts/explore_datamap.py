"""Explore the datamap structure"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
file_path = DATA_DIR / "datamap-info-arcom.xlsx"
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")

# Read TEXTS sheet
texts = pd.read_excel(file_path, sheet_name='TEXTS')

# Check RSINFO columns
rsinfo_cols = [c for c in df.columns if 'RSINFO_2' in c]
print("RSINFO_2 columns:", rsinfo_cols[:15])

# Check the datamap for RSINFO
print("\nRSINFO in datamap:")
rsinfo_labels = texts[texts['NAME'].str.contains('RSINFO', na=False)]
for _, row in rsinfo_labels.head(30).iterrows():
    name = row['NAME']
    code = row['CODE']
    label = str(row['FR:L'])[:50] if pd.notna(row['FR:L']) else "N/A"
    print(f"  {name}: {code} = {label}")
