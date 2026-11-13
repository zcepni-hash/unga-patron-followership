"""Step 2: match the same resolution across consecutive regular sessions -> recurring_map.

Inputs:  data/processed/resolutions.parquet, data/processed/votes_long.parquet (from step 1)
Outputs: data/processed/recurring_map.parquet
         data/processed/manual_check.csv   (borderline pairs, open in Excel)

Matching rule (docs/research_design_tr.md, "Tekrarlanan karar eşleştirmesi"), adapted to the
UN Digital Library data, which has titles and agenda items but no full texts:
1. Regular sessions only; resolution in session s is compared with every resolution in s-1.
2. Titles are normalized: the " : resolution / adopted by ..." suffix, numbers, punctuation
   and case are removed.
3. Similarity = difflib ratio of normalized titles (0-1), +0.02 if the agenda item is the same.
4. One-to-one greedy assignment, best pairs first.
   score >= 0.90 -> auto; 0.75-0.90 -> manual_check; < 0.75 -> no match.
   Pairs from titles that occur more than once in a session are also sent to manual_check.
Emergency special sessions have no yearly rhythm and are left out here.

Validation: US switches per year should be close to Voeten (2026): 4 (2018), 3 (2019), 12 (2025).
"""

import re
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

PROC = Path("data/processed")
AUTO, MANUAL = 0.90, 0.75
P5 = ["USA", "GBR", "FRA", "RUS", "CHN"]


def normalize_title(title) -> str:
    t = str(title).split(" : resolution")[0].lower()
    t = re.sub(r"\d+", " ", t)                 # years, session numbers
    t = re.sub(r"[^a-z\s]", " ", t)            # punctuation
    return re.sub(r"\s+", " ", t).strip()


def res_number(symbol) -> int:
    m = re.search(r"/(\d+)\s*[A-Z]?$", str(symbol).strip())
    return int(m.group(1)) if m else 0


def match_sessions(cur: pd.DataFrame, prev: pd.DataFrame) -> pd.DataFrame:
    pairs = []
    for _, a in cur.iterrows():
        for _, b in prev.iterrows():
            sim = SequenceMatcher(None, a["title_norm"], b["title_norm"]).ratio()
            if sim < MANUAL - 0.02:
                continue
            same_agenda = (a["agenda_title"] == b["agenda_title"]) and pd.notna(a["agenda_title"])
            score = min(sim + 0.02 * same_agenda, 1.0)
            # tie-breaker for identical titles: similar position in the session
            tie = abs(a["rank"] - b["rank"])
            pairs.append((score, -tie, sim, a["resolution"], b["resolution"]))
    pairs.sort(reverse=True)
    used_a, used_b, out = set(), set(), []
    for score, _, sim, ra, rb in pairs:
        if ra in used_a or rb in used_b or score < MANUAL:
            continue
        used_a.add(ra)
        used_b.add(rb)
        out.append({"resolution_t": ra, "resolution_tm1": rb, "sim": round(sim, 3),
                    "score": round(score, 3)})
    return pd.DataFrame(out)


def main():
    res = pd.read_parquet(PROC / "resolutions.parquet")
    votes = pd.read_parquet(PROC / "votes_long.parquet")

    reg = res[res["session_type"] == "regular"].copy()
    reg["title_norm"] = reg["title"].apply(normalize_title)
    reg["rank"] = reg.groupby("session")["resolution"].transform(
        lambda s: s.map(res_number).rank(pct=True))
    dup_titles = reg.groupby(["session", "title_norm"])["resolution"].transform("count") > 1
    reg["dup_title"] = dup_titles

    maps = []
    sessions = sorted(reg["session"].dropna().unique())
    for s in sessions[1:]:
        cur, prev = reg[reg["session"] == s], reg[reg["session"] == s - 1]
        if prev.empty:
            continue
        m = match_sessions(cur, prev)
        if m.empty:
            continue
        m["session"] = int(s)
        maps.append(m)
        print(f"session {int(s)}: {len(cur)} resolutions, {len(m)} matched to session {int(s) - 1}")

    rmap = pd.concat(maps, ignore_index=True)
    dup = set(reg.loc[reg["dup_title"], "resolution"])
    rmap["match_status"] = "auto"
    rmap.loc[rmap["score"] < AUTO, "match_status"] = "manual_check"
    rmap.loc[rmap["resolution_t"].isin(dup) | rmap["resolution_tm1"].isin(dup),
             "match_status"] = "manual_check"

    titles = res.set_index("resolution")["title"]
    rmap["title_t"] = rmap["resolution_t"].map(titles)
    rmap["title_tm1"] = rmap["resolution_tm1"].map(titles)
    rmap.to_parquet(PROC / "recurring_map.parquet", index=False)
    rmap[rmap["match_status"] == "manual_check"].to_csv(PROC / "manual_check.csv", index=False)

    print("\nMatched pairs:", len(rmap), "| status:", rmap["match_status"].value_counts().to_dict())
    print("Share of regular-session resolutions matched to the previous session:",
          round(rmap["resolution_t"].nunique() / reg[reg["session"] > sessions[0]].shape[0], 3))

    # Preview of step 3: P5 vote switches on auto-matched pairs, by year of the session-t vote
    auto = rmap[rmap["match_status"] == "auto"]
    p5 = votes[votes["iso3"].isin(P5)].pivot_table(index="resolution", columns="iso3",
                                                   values="vote", aggfunc="first")
    a = p5.reindex(auto["resolution_t"]).to_numpy()
    b = p5.reindex(auto["resolution_tm1"]).to_numpy()
    sw = pd.DataFrame((a != b) & ~pd.isna(a) & ~pd.isna(b), columns=p5.columns)
    sw["year"] = auto["resolution_t"].map(res.set_index("resolution")["year"]).to_numpy()
    print("\nP5 switches on auto-matched pairs, by year (preview of step 3):")
    print(sw.groupby("year")[P5].sum().astype(int).to_string())
    print("Total:", sw[P5].sum().astype(int).to_dict())


if __name__ == "__main__":
    main()
    