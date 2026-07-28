# Source Notes

- **Source:** Kaggle - Data Analyst Job Postings dataset
- **Route:** Approved Dataset (Route 1)
- **Original dataset size:** 61,953 rows, 27 columns
- **Sampling method:** Random sample of 1,000 rows using 
  `pandas.DataFrame.sample(n=1000, random_state=42)` for reproducibility. 
  After cleaning and duplicate removal, the final working dataset contains 
  977 rows.
- **Reason for sampling:** Reduce processing time while keeping a 
  statistically representative, reproducible subset of the original data.
- **Collection date (of original dataset):** As published on Kaggle 
  (exact scrape date not specified by the original dataset author).

## Known Source Limitations

- Only ~16% of postings in the original dataset include disclosed salary 
  information.
- The `work_from_home` field in the original dataset is a simple Boolean 
  (True/False), with no distinction for "Hybrid" arrangements.
- No `source_url` field is available in this dataset; only the posting 
  platform (e.g., LinkedIn, Indeed, Upwork) is recorded via the `source` 
  column.
- Some recorded "companies" are staffing/recruitment platforms 
  (e.g., Upwork, Dice, Insight Global) rather than the direct employer.
