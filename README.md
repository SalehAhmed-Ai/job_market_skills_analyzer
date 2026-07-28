# Job Market Skills Analyzer

## Project Overview
This project analyzes job posting data to identify the most common job 
roles, the most requested technical skills, work mode trends, experience 
requirements, and salary patterns in the data analytics job market. The 
goal is to help students and job seekers understand which skills and 
roles are currently in demand.

## Data Source
- **Source:** Kaggle - Data Analyst Job Postings dataset
- **Route:** Approved Dataset (Route 1)
- **Original size:** 61,953 rows
- **Working sample:** 977 rows, after a reproducible random sample of 
  1,000 rows (`random_state=42`) followed by cleaning and duplicate 
  removal
- Full details in [`data/source_notes.md`](data/source_notes.md)

## Repository Structure
```
job_market_skills_analyzer/
├── data/
│   ├── raw/job_postings_raw.csv
│   ├── cleaned/job_postings_cleaned.csv
│   └── source_notes.md
├── src/
│   ├── data_utils.py
│   └── text_processing.py
├── config/
│   ├── skills_list.txt
│   └── role_mapping.csv
├── charts/
│   ├── static/
│   └── interactive/
├── job_market_analysis.ipynb
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Tools and Libraries
- **Data handling:** pandas, numpy
- **Text processing:** re (regex)
- **Visualization:** matplotlib, seaborn, plotly
- **Dashboard (optional bonus):** streamlit

## Data Loading
The raw dataset is loaded directly from `data/raw/job_postings_raw.csv` 
using `src/data_utils.py`. No manual edits were made to the raw file.

## Data Cleaning and Feature Engineering
Key cleaning steps (see `job_market_analysis.ipynb`, Sections 5-7):
- Standardized column names and renamed fields to match the required 
  project schema (e.g., `title` → `job_title`)
- Took a reproducible random sample of 1,000 rows before cleaning
- Filled missing `location` values from `search_location`
- Dropped unused/empty columns (e.g., `commute_time`, `thumbnail`)
- Removed duplicate postings based on job title, company, and location
- Validated salary columns as numeric and added a `has_salary` flag 
  instead of inventing missing salary values
- Extracted skills, years of experience, and work mode from free text 
  using regex (`src/text_processing.py`)
- Built `main_role` using a keyword-based mapping (`config/role_mapping.csv`)
- Built `skill_count`, `seniority_level`, and an experience-level category

## Analysis and Visualizations
Full analysis is available in `job_market_analysis.ipynb`, Section 8, 
covering: most common roles and skills, work mode and seniority 
distribution, salary distribution and its relationship with experience, 
skill co-occurrence, required skills by role, top hiring companies and 
locations, and salary by skill requirement.

## Key Findings
1. Data Analyst dominates the sample (64.1% of postings, 626 out of 977).
2. SQL is the most requested skill (49.8%), followed by Python (32.8%) 
   and Excel (30.5%).
3. SQL and Python frequently co-occur in the same postings.
4. Work mode is stated in only 39.3% of postings; among those, Remote 
   dominates (258) over Hybrid (97) and On-site (29).
5. Seniority is stated in only 22.1% of titles; Senior (151) far 
   outnumbers Junior (38) and Lead (27).
6. Salary is disclosed in only 15.6% of postings (152/977), with a 
   median standardized annual salary of ~$93,600.
7. Python shows the highest average salary premium (~$106,000 vs. 
   ~$85,000 without it), followed by Tableau and SQL.

## Limitations
- Analysis is based on a random sample (977 of 61,953 rows) for 
  processing efficiency; findings may not generalize to the full dataset.
- Only 15.6% of postings disclose salary; no values were invented, and 
  salary analysis is based on this subset only.
- Experience was extracted from free text and found in 56.7% of postings; 
  values above 30 years were treated as regex false positives and 
  discarded.
- Work mode and seniority were identifiable in 39.3% and 22.1% of 
  postings respectively, based on explicit text mentions only.
- 23.2% of job titles did not match a predefined role category 
  ("Other"/"Other Analyst").
- Some "companies" are staffing platforms (e.g., Upwork, Dice) rather 
  than direct employers; "Anywhere"/"United States" mix remote and 
  country-level entries with specific cities.
- Skill-salary comparisons are based on small samples (under 70 postings 
  per group) and should be treated as indicative, not statistically 
  robust.

## How to Run the Project

1. Clone the repository:
   ```
   git clone <repository-url>
   cd job_market_skills_analyzer
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

4. Run the analysis notebook:
   Open `job_market_analysis.ipynb` in VS Code or Jupyter and run all 
   cells from top to bottom. This will regenerate the cleaned dataset in 
   `data/cleaned/` and save charts in `charts/static/` and 
   `charts/interactive/`.

5. (Optional) Run the Streamlit dashboard:
   ```
   streamlit run app.py
   ```
