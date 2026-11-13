"""Step 2: match the same resolution across consecutive sessions -> recurring_map.

Output: data/processed/recurring_map.parquet
Columns: rcid_t, rcid_tm1, sim, match_status  (auto / manual_check / rejected)

A resolution in session t matches one in session t-1 if:
1. normalized titles match (lowercase, punctuation and session numbers removed),
2. same committee or agenda item,
3. TF-IDF cosine similarity of the texts >= 0.80.
   0.60-0.80 -> exported to Excel for manual checking; < 0.60 -> no match.

Validation: US switches should be 4 (2018), 3 (2019), 12 (2025) per Voeten (2026).
"""

SIM_AUTO = 0.80
SIM_MANUAL = 0.60


def normalize_title(title: str) -> str:
    # TODO: lowercase, strip punctuation, remove session numbers and years
    raise NotImplementedError


def main():
    # TODO: build candidate pairs by normalized title + committee
    # TODO: TF-IDF cosine on resolution texts (scikit-learn)
    # TODO: export manual_check pairs to data/processed/manual_check.xlsx
    raise NotImplementedError


if __name__ == "__main__":
    main()
