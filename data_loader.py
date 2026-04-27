"""
data_loader.py
--------------
Loads and cleans the Titanic dataset for the Streamlit dashboard.

Key cleaning decisions (and why):
  * Age missing -> impute with the median of the passenger's Pclass + Sex group.
    A single global median washes out the very signal we want to study.
  * Cabin missing 77% of the time -> drop as a string field, keep as HasCabin (0/1).
  * Embarked missing in 2 rows -> fill with the modal port ('S' / Southampton).
  * Embarked codes (C/Q/S) -> human-readable port names.
  * Engineered features: FamilySize, IsAlone, Title (from Name), AgeGroup, FareBand.
"""

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner="Loading Titanic passenger manifest...")
def load_and_clean_data(path: str = "Titanic-Dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # --- 1. Impute Age by Pclass + Sex group median (preserves group differences) ---
    df["Age"] = (
        df.groupby(["Pclass", "Sex"])["Age"]
          .transform(lambda s: s.fillna(s.median()))
    )

    # --- 2. Cabin: too sparse to use as a category. Keep presence as a feature. ---
    df["HasCabin"] = df["Cabin"].notna().astype(int)

    # --- 3. Embarked: fill the 2 missing values with the most common port ---
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])
    port_map = {"C": "Cherbourg", "Q": "Queenstown", "S": "Southampton"}
    df["EmbarkedPort"] = df["Embarked"].map(port_map)

    # --- 4. Engineered features ---
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1          # +1 for the passenger themself
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)
    df["TravelStatus"] = df["IsAlone"].map({1: "Alone", 0: "With Family"})

    # Title extracted from Name, e.g. "Mrs.", "Master.", etc.
    df["Title"] = df["Name"].str.extract(r" ([A-Za-z]+)\.", expand=False)
    rare_titles = ["Lady", "Countess", "Capt", "Col", "Don", "Dr",
                   "Major", "Rev", "Sir", "Jonkheer", "Dona"]
    df["Title"] = df["Title"].replace({"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs"})
    df["Title"] = df["Title"].where(~df["Title"].isin(rare_titles), "Rare")
    df.loc[~df["Title"].isin(["Mr", "Mrs", "Miss", "Master", "Rare"]), "Title"] = "Rare"

    # Age groups for categorical analysis
    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 12, 18, 35, 60, 100],
        labels=["Child (0-12)", "Teen (13-18)", "Young Adult (19-35)",
                "Adult (36-60)", "Senior (60+)"]
    )

    # Fare quartile bands
    df["FareBand"] = pd.qcut(df["Fare"], 4, labels=["Low", "Medium", "High", "Premium"])

    # --- 5. Tidy types for downstream code ---
    df["SurvivedBin"] = (df["Survived"] == "Yes").astype(int)   # numeric for aggregations
    df["Sex"] = df["Sex"].str.title()                            # "Female" / "Male"

    return df
