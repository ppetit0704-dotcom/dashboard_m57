import pandas as pd

def to_float(val):
    if pd.isna(val):
        return 0.0
    return float(str(val).replace(",", "."))

def load_csv(file):
    df = pd.read_csv(file, sep=None, engine="python", encoding="utf-8-sig")

    for col in ["Total_Prévu", "Réalisé", "Reste_engagé"]:
        df[col] = df[col].apply(to_float)

    for col in df.columns:
        if col.startswith("Liquidé_N"):
            df[col] = df[col].apply(to_float)

    annees = [c for c in df.columns if c.startswith("Liquidé_N")]
    return df, annees
