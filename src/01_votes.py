"""Step 1: raw UN votes -> votes_long.

Output: data/processed/votes_long.parquet
Columns: rcid, session, date, iso3, vote  (1 = yes, 0.5 = abstain, 0 = no, NaN = absent)

Coding rules (docs/research_design_tr.md, "Oy kodlaması"):
- Absent (BSV code 8) -> NaN, never 0.5.
- Non-member (code 9) and states suspended under Article 19 -> dropped for that session.
- Keep only votes on resolutions as a whole; drop separate paragraph votes.
"""

from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/processed")

VOTE_MAP = {"Y": 1.0, "A": 0.5, "N": 0.0}  # anything else -> NaN


def main():
    # TODO: read RAW / "un_votes.csv"
    # TODO: map country names to ISO3 (countrycode equivalent, e.g. `country_converter`)
    # TODO: apply VOTE_MAP; drop paragraph votes; drop Article 19 suspensions
    # TODO: cross-check against RAW / "voeten_votes.csv" (target: 99.6% match)
    # TODO: write OUT / "votes_long.parquet"
    raise NotImplementedError


if __name__ == "__main__":
    main()
