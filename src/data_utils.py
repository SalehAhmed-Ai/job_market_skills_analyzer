"""
data_utils.py

Responsibility: General-purpose helper functions for loading, cleaning,
and saving the job postings dataset.

This file does NOT contain the full notebook workflow, analysis, or
hard-coded final answers - only reusable functions.
"""

import pandas as pd
from pathlib import Path


# Load data
def load_raw_data(path: str) -> pd.DataFrame:
    """
    Load the raw CSV file exactly as it is.
    """
    path = Path(path)
    df = pd.read_csv(path)
    print(f"[OK] Loaded {len(df)} rows and {len(df.columns)} columns from {path}")
    return df


# Clean column names
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names: lowercase, no extra spaces, underscores
    instead of spaces.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    return df


# Rename columns
def rename_columns(df: pd.DataFrame, rename_map: dict) -> pd.DataFrame:
    """
    Rename columns using a provided mapping dictionary.
    Example: {"title": "job_title", "company_name": "company"}
    Only renames columns that actually exist in the dataframe.
    """
    df = df.copy()
    existing_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=existing_map)
    print(f"[OK] Renamed {len(existing_map)} columns: {existing_map}")
    return df


# Sample data
def sample_data(df: pd.DataFrame, n: int = 1000, random_state: int = 42) -> pd.DataFrame:
    """
    Take a reproducible random sample from a large dataset.
    Resets the index so it runs cleanly from 0 to n-1.
    """
    if n >= len(df):
        print(f"[INFO] Requested sample size ({n}) >= dataset size ({len(df)}). Returning full dataset.")
        return df.reset_index(drop=True)

    df_sample = df.sample(n=n, random_state=random_state).reset_index(drop=True)
    print(f"[OK] Sampled {len(df_sample)} rows out of {len(df)} (random_state={random_state})")
    return df_sample


# Fill missing values from another column
def fill_missing_from_column(df: pd.DataFrame, target_col: str, source_col: str) -> pd.DataFrame:
    """
    Fill missing values in target_col using values from source_col.
    Example: fill missing 'location' values using 'search_location'.
    """
    df = df.copy()
    if target_col in df.columns and source_col in df.columns:
        missing_before = df[target_col].isna().sum()
        df[target_col] = df[target_col].fillna(df[source_col])
        missing_after = df[target_col].isna().sum()
        print(f"[OK] Filled {missing_before - missing_after} missing '{target_col}' values from '{source_col}'")
    return df


# Drop unused columns
def drop_unused_columns(df: pd.DataFrame, columns_to_drop: list) -> pd.DataFrame:
    """
    Drop columns that are not required for the analysis
    (e.g. Unnamed: 0, index, thumbnail, job_id, commute_time...).
    Only drops columns that actually exist in the dataframe.
    """
    df = df.copy()
    existing = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing)
    print(f"[OK] Dropped {len(existing)} unused columns: {existing}")
    return df


# Clean text
def clean_text(text):
    """
    Clean a single text value:
    - handle missing values
    - strip leading/trailing spaces
    - collapse repeated internal spaces
    """
    if pd.isna(text):
        return text
    text = str(text).strip()
    text = " ".join(text.split())
    return text


def clean_text_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Apply clean_text() to a list of text columns.
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    return df


# Remove duplicates
def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
    """
    Remove duplicate rows based on a subset of columns (e.g. job_title + company).
    If subset is None, checks duplication across all columns.
    """
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    after = len(df)
    print(f"[OK] Removed {before - after} duplicate rows ({before} -> {after})")
    return df


# Handle missing values
def handle_missing_values(df: pd.DataFrame, fill_value: str = "Unknown", columns: list = None) -> pd.DataFrame:
    """
    Fill missing values in the given text columns with a placeholder
    (default: "Unknown"). Does NOT invent numeric values.
    """
    df = df.copy()
    target_columns = columns if columns else df.columns
    for col in target_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                df[col] = df[col].fillna(fill_value)
                print(f"[INFO] Filled {missing_count} missing values in '{col}' with '{fill_value}'")
    return df


# Save cleaned data
def save_cleaned_data(df: pd.DataFrame, path: str) -> None:
    """
    Save the cleaned dataset to the given path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[OK] Saved cleaned dataset ({len(df)} rows) to {path}")