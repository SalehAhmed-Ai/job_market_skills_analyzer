"""
text_processing.py

Responsibility: Regex-based text processing functions for job postings:
- Skill detection from job descriptions
- Experience extraction from job descriptions
- Work mode detection (Remote / Hybrid / On-site)

These functions work directly on raw text and do NOT invent
missing information - unmatched text stays as missing/unknown.
"""

import re
import pandas as pd



# 1. Load the controlled skills list from config

def load_skills_list(path: str = "config/skills_list.txt") -> list:
    """
    Load the list of skills to search for, one skill per line.
    Preserves the exact casing written in the file (e.g. "SQL", "Power BI")
    so it can be used directly for display in charts and column names.
    """
    with open(path, "r", encoding="utf-8") as f:
        skills = [line.strip() for line in f if line.strip()]
    print(f"[OK] Loaded {len(skills)} skills from {path}")
    return skills



# 2. Skill detection using Regex with word boundaries

def detect_skills(text: str, skills_list: list) -> dict:
    """
    Search a single job description for each skill in skills_list.
    Uses word boundaries (\b) to avoid partial matches
    (e.g. 'r' matching inside 'server'). Matching is case-insensitive,
    but the resulting column name keeps the original casing from the
    skills list file (e.g. "SQL", "Power BI" -> "Power_BI").
    Returns a dict: {skill_name: 0 or 1}
    """
    result = {}
    if pd.isna(text):
        text = ""
    text_lower = str(text).lower()

    for skill in skills_list:
        # Escape special regex characters in the skill name (e.g. "c++")
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        match = re.search(pattern, text_lower)
        # Use the original casing for the column name (spaces -> underscores)
        column_name = skill.replace(" ", "_")
        result[column_name] = 1 if match else 0

    return result


def add_skill_columns(df: pd.DataFrame, text_column: str, skills_list: list) -> pd.DataFrame:
    """
    Apply detect_skills() to every row and add one indicator column
    per skill to the dataframe.
    """
    df = df.copy()
    skill_dicts = df[text_column].apply(lambda text: detect_skills(text, skills_list))
    skill_df = pd.DataFrame(list(skill_dicts))
    df = pd.concat([df.reset_index(drop=True), skill_df.reset_index(drop=True)], axis=1)
    print(f"[OK] Added {len(skills_list)} skill indicator columns based on '{text_column}'")
    return df



# 3. Experience extraction from free text

def extract_experience(text: str):
    """
    Extract minimum and maximum years of experience mentioned in text.
    Handles patterns like:
      "2 years", "3+ years", "2-5 years", "at least 3 years"

    Applies a sanity cap:
      Accept only values between 0 and 40 years.
      Unrealistic values (e.g. 50, 90) are treated as missing.
    """
    if pd.isna(text):
        return None, None

    text_lower = str(text).lower()

    # Accept only realistic experience values
    def valid_years(value):
        return 0 <= value <= 30

    # Pattern 1: range (e.g. "2-5 years" or "2 to 5 years")
    range_match = re.search(
        r"(\d{1,2})\s*(?:-|to)\s*(\d{1,2})\s*year",
        text_lower
    )
    if range_match:
        min_exp = int(range_match.group(1))
        max_exp = int(range_match.group(2))

        if valid_years(min_exp) and valid_years(max_exp):
            return min_exp, max_exp
        return None, None

    # Pattern 2: "3+ years"
    plus_match = re.search(r"(\d{1,2})\s*\+\s*year", text_lower)
    if plus_match:
        min_exp = int(plus_match.group(1))

        if valid_years(min_exp):
            return min_exp, None
        return None, None

    # Pattern 3: "at least 3 years" / "minimum 3 years"
    min_match = re.search(
        r"(?:at least|minimum(?:\s+of)?)\s*(\d{1,2})\s*year",
        text_lower
    )
    if min_match:
        min_exp = int(min_match.group(1))

        if valid_years(min_exp):
            return min_exp, None
        return None, None

    # Pattern 4: plain "3 years"
    single_match = re.search(r"(\d{1,2})\s*year", text_lower)
    if single_match:
        years = int(single_match.group(1))

        if valid_years(years):
            return years, years
        return None, None

    return None, None
def add_experience_columns(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Apply extract_experience() to every row and add min/max experience columns.
    """
    df = df.copy()
    extracted = df[text_column].apply(extract_experience)
    df["min_experience"] = extracted.apply(lambda x: x[0])
    df["max_experience"] = extracted.apply(lambda x: x[1])
    found_count = df["min_experience"].notna().sum()
    print(f"[OK] Extracted experience info from {found_count} out of {len(df)} rows")
    return df



# 4. Work mode detection (Remote / Hybrid / On-site)

def detect_work_mode_from_text(text: str) -> str:
    """
    Detect work mode from free text (e.g. job description or extensions).
    Returns one of: 'Remote', 'Hybrid', 'On-site', or 'Unknown'.
    """
    if pd.isna(text):
        return "Unknown"
    text_lower = str(text).lower()

    if re.search(r"\bhybrid\b", text_lower):
        return "Hybrid"
    if re.search(r"\bremote\b|work from home|work-from-home|wfh\b", text_lower):
        return "Remote"
    if re.search(r"\bon[\s-]?site\b|in[\s-]?office\b", text_lower):
        return "On-site"

    return "Unknown"


def add_work_mode_check_column(df: pd.DataFrame, text_column: str, new_column: str = "work_mode_from_text") -> pd.DataFrame:
    """
    Add a work-mode column detected from raw text, useful to validate
    against an existing pre-extracted work_mode column (if present).
    """
    df = df.copy()
    df[new_column] = df[text_column].apply(detect_work_mode_from_text)
    print(f"[OK] Added '{new_column}' column based on '{text_column}'")
    return df



# 6. Main Role assignment (keyword-based, order-sensitive)

def load_role_mapping(path: str = "config/role_mapping.csv") -> list:
    """
    Load the role mapping as an ordered list of (keyword, main_role) tuples.
    Order matters: more specific keywords must appear first in the CSV.
    """
    mapping_df = pd.read_csv(path)
    return list(mapping_df.itertuples(index=False, name=None))


def assign_main_role(title: str, role_mapping: list) -> str:
    """
    Match a job title against an ordered list of keywords and return
    the first matching main_role. Returns 'Other' if nothing matches.
    """
    if pd.isna(title):
        return "Other"
    title_lower = str(title).lower()
    for keyword, role in role_mapping:
        if keyword.lower() in title_lower:
            return role
    return "Other"


def add_main_role_column(df: pd.DataFrame, title_column: str, role_mapping: list) -> pd.DataFrame:
    """
    Apply assign_main_role() to every row and add a main_role column.
    """
    df = df.copy()
    df["main_role"] = df[title_column].apply(lambda t: assign_main_role(t, role_mapping))
    other_count = (df["main_role"] == "Other").sum()
    print(f"[OK] Assigned main_role. 'Other' count: {other_count} out of {len(df)}")
    return df



# 7. Skill count feature

def add_skill_count_column(df: pd.DataFrame, skill_columns: list) -> pd.DataFrame:
    """
    Sum the skill indicator columns (0/1) for each row into a single
    skill_count column.
    """
    df = df.copy()
    df["skill_count"] = df[skill_columns].sum(axis=1)
    print(f"[OK] Added skill_count column (range: {df['skill_count'].min()}-{df['skill_count'].max()})")
    return df



# 8. Seniority level from job title

def detect_seniority(title: str) -> str:
    """
    Detect seniority level mentioned directly in the job title.
    Returns 'Senior', 'Junior', 'Lead', or 'Not Specified'.
    """
    if pd.isna(title):
        return "Not Specified"
    title_lower = str(title).lower()

    if re.search(r"\b(senior|sr\.?)\b", title_lower):
        return "Senior"
    if re.search(r"\blead\b", title_lower):
        return "Lead"
    if re.search(r"\b(junior|jr\.?|entry[\s-]?level|intern)\b", title_lower):
        return "Junior"
    return "Not Specified"


def add_seniority_column(df: pd.DataFrame, title_column: str) -> pd.DataFrame:
    """
    Apply detect_seniority() to every row and add a seniority_level column.
    """
    df = df.copy()
    df["seniority_level"] = df[title_column].apply(detect_seniority)
    print(f"[OK] Added seniority_level column")
    return df
def standardize_existing_work_mode(value) -> str:
    """
    Convert an existing work_mode value (which may be Boolean True/False
    or already 'Unknown') into the same category labels used by
    detect_work_mode_from_text(): 'Remote', 'On-site', or 'Unknown'.
    """
    if value is True:
        return "Remote"
    if value is False:
        return "On-site"
    return "Unknown"


def add_standardized_work_mode_column(df: pd.DataFrame, source_column: str, new_column: str = "work_mode_standardized") -> pd.DataFrame:
    """
    Apply standardize_existing_work_mode() to an existing column so it
    can be fairly compared with our regex-based work_mode_from_text column.
    """
    df = df.copy()
    df[new_column] = df[source_column].apply(standardize_existing_work_mode)
    print(f"[OK] Added '{new_column}' column standardized from '{source_column}'")
    return df