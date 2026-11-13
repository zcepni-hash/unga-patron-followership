
"""Step 1: UN Digital Library voting data -> votes_long + resolutions.

Input (data/raw/):
- *_votes_ga.csv : UN Dag Hammarskjöld Library, "United Nations General Assembly Voting Data"
                   (https://digitallibrary.un.org/record/4060887). The newest file is used.
                   One row per Member State per adopted resolution.

Outputs (data/processed/):
- resolutions.parquet : one row per resolution adopted by recorded vote
    resolution, draft, date, year, session, session_type, title, agenda_title, subjects,
    total_yes, total_no, total_abstentions, total_non_voting, total_ms
- votes_long.parquet  : one row per Member State per resolution
    resolution, iso3, member_state, vote

Coding rules (docs/research_design_tr.md, "Oy kodlaması"):
- Y = 1, A = 0.5, N = 0, X (non-voting) = NaN. Absence is missing, never 0.5.
  Article 19 suspensions are also X; they drop out of the risk set because they are missing.
- Only resolutions adopted by recorded vote. This source already excludes paragraph votes
  and failed drafts.
- Period: votes from 1 September 2000 (start of session 55) onward.
- Country key: ms_code (three-letter code).
- Session and session type are parsed from the resolution symbol:
  A/RES/79/12 -> regular 79; A/RES/ES-11/7 -> emergency special 11; A/RES/S-30/1 -> special 30.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/processed")

VOTE_MAP = {"Y": 1.0, "A": 0.5, "N": 0.0, "X": np.nan}
START = "2000-09-01"
P5 = ["USA", "GBR", "FRA", "RUS", "CHN"]
SYMBOL = re.compile(r"A/RES/(ES-|S-)?(\d+)/")


def parse_symbol(symbol: str):
    """Return (session_type, session_number) from a resolution symbol."""
    m = SYMBOL.search(str(symbol))
    if not m:
        return None, np.nan
    kind = {"ES-": "emergency special", "S-": "special", None: "regular"}[m.group(1)]
    return kind, int(m.group(2))


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    path = sorted(RAW.glob("*_votes_ga.csv"))[-1]
    print("Reading", path)
    df = pd.read_csv(path, low_memory=False, dtype=str)
    print("Columns:", list(df.columns))

    # 1. Period and valid votes
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"] >= START]
    df["ms_vote"] = df["ms_vote"].str.strip().str.upper()
    print("ms_vote values (from 2000):", df["ms_vote"].value_counts(dropna=False).to_dict())
    df = df[df["ms_vote"].isin(VOTE_MAP.keys())].copy()
    df["vote"] = df["ms_vote"].map(VOTE_MAP)

    # 2. Resolution table
    parsed = df["resolution"].apply(parse_symbol)
    df["session_type"] = parsed.str[0]
    df["session"] = parsed.str[1]
    df["year"] = df["date"].dt.year
    res_cols = ["resolution", "draft", "date", "year", "session", "session_type", "title",
                "agenda_title", "subjects", "total_yes", "total_no", "total_abstentions",
                "total_non_voting", "total_ms"]
    res = df[res_cols].drop_duplicates("resolution").reset_index(drop=True)
    for c in ["total_yes", "total_no", "total_abstentions", "total_non_voting", "total_ms"]:
        res[c] = pd.to_numeric(res[c], errors="coerce")

    # 3. Vote table
    votes = df[["resolution", "ms_code", "ms_name", "vote"]].rename(
        columns={"ms_code": "iso3", "ms_name": "member_state"})
    dup = votes.duplicated(["resolution", "iso3"]).sum()
    votes = votes.drop_duplicates(["resolution", "iso3"])

    res.to_parquet(OUT / "resolutions.parquet", index=False)
    votes.to_parquet(OUT / "votes_long.parquet", index=False)

    # 4. Checks
    print("\nResolutions:", len(res), "| vote rows:", len(votes), "| duplicate rows dropped:", dup)
    print("Dates:", res["date"].min().date(), "to", res["date"].max().date())
    print("Unparsed resolution symbols:", res["session_type"].isna().sum())
    print("\nResolutions by year and session type:")
    print(res.pivot_table(index="year", columns="session_type", values="resolution",
                          aggfunc="count", fill_value=0).to_string())
    print("\nVote shares:", votes["vote"].value_counts(dropna=False, normalize=True).round(3).to_dict())
    print("Countries per year (max):", votes.merge(res[["resolution", "year"]])
          .groupby("year")["iso3"].nunique().max())
    missing_p5 = [c for c in P5 if c not in set(votes["iso3"])]
    print("P5 missing:", missing_p5 or "none")

    # Totals in the file vs. counted votes
    counted = votes.assign(y=votes["vote"].eq(1), n=votes["vote"].eq(0), a=votes["vote"].eq(0.5)) \
        .groupby("resolution")[["y", "n", "a"]].sum()
    chk = res.set_index("resolution").join(counted)
    bad = chk[(chk["total_yes"] != chk["y"]) | (chk["total_no"] != chk["n"])
              | (chk["total_abstentions"] != chk["a"])].dropna(subset=["total_yes"])
    print("Resolutions where counted votes differ from reported totals:", len(bad))

    # Validation: Ukraine, 24 February 2025 (expected 93 yes, 18 no, 65 abstain)
    ukr = res[(res["date"] == "2025-02-24") & res["title"].str.contains("Ukraine", case=False, na=False)]
    for _, r in ukr.iterrows():
        v = votes[votes["resolution"] == r["resolution"]].set_index("iso3")["vote"]
        print(f"\n{r['resolution']} | {r['title'][:70]}")
        print(f"  yes={int((v == 1).sum())} no={int((v == 0).sum())} "
              f"abstain={int((v == 0.5).sum())} non-voting={int(v.isna().sum())} | "
              f"USA={v.get('USA')} RUS={v.get('RUS')} CHN={v.get('CHN')}")


if __name__ == "__main__":
    main()
    