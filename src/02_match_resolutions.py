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
   Title similarity >= 0.90 -> auto; otherwise score 0.75-0.90 -> manual_check; < 0.75 -> no match.
   Pairs from titles that occur more than once in a session are also sent to manual_check.
5. Review of manual_check pairs:
   - identical titles (similarity 1.0) are accepted; position in the session breaks ties;
   - pairs whose titles name different countries are rejected (e.g. human rights in X vs. Y);
   - the rest are decided one by one in MANUAL_DECISIONS below (reviewed 13 Nov 2026).
   Unreviewed manual_check pairs are not used.
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

# Hand-reviewed borderline pairs (resolution_t, resolution_tm1) -> "accept" / "reject"
MANUAL_DECISIONS = {
    ("A/RES/58/51", "A/RES/57/59"): "accept",     # New Agenda Coalition resolution
    ("A/RES/58/307", "A/RES/57/325"): "accept",   # UNIFIL financing ("UN" vs "United Nations")
    ("A/RES/59/307", "A/RES/58/307"): "accept",   # UNIFIL financing
    ("A/RES/68/32", "A/RES/67/39"): "reject",     # convening a meeting vs. its follow-up
    ("A/RES/80/53", "A/RES/79/240"): "reject",    # expert group: establishment vs. work (to verify)
    # same resolution, title reworded
    ("A/RES/58/160", "A/RES/57/195"): "accept",   # racism / Durban follow-up
    ("A/RES/59/178", "A/RES/58/162"): "accept",   # use of mercenaries
    ("A/RES/60/65", "A/RES/59/76"): "accept",     # Japan's annual nuclear disarmament resolution
    ("A/RES/60/56", "A/RES/59/75"): "accept",     # New Agenda Coalition resolution
    ("A/RES/63/307", "A/RES/62/249"): "accept",   # IDPs and refugees from Abkhazia
    ("A/RES/65/72", "A/RES/64/47"): "accept",     # Japan's annual nuclear disarmament resolution
    ("A/RES/70/40", "A/RES/69/52"): "accept",     # Japan's annual nuclear disarmament resolution
    ("A/RES/78/221", "A/RES/77/229"): "accept",   # human rights in temporarily occupied Crimea
    # different resolutions with similar titles
    ("A/RES/56/24[O]", "A/RES/55/33[D]"): "reject",  # 2005 vs 2000 NPT Review Conference
    ("A/RES/69/247", "A/RES/68/304"): "reject",   # modalities vs. framework resolution
    ("A/RES/72/74", "A/RES/71/250"): "reject",    # cooperation with different organizations
    ("A/RES/77/263A", "A/RES/76/245"): "reject",  # budget items
    ("A/RES/78/273", "A/RES/77/301"): "reject",   # revised estimates vs. establishment
    ("A/RES/80/116", "A/RES/79/232"): "reject",   # ICJ opinion follow-up vs. request for opinion
    ("A/RES/80/290", "A/RES/79/333"): "reject",   # modalities of different meetings
    ("A/RES/80/153", "A/RES/79/276"): "reject", # different UN decades (to verify)
}

GENERIC = {"republic", "of", "the", "democratic", "united", "states", "kingdom", "islamic",
           "people", "peoples", "s", "and", "federation", "arab", "plurinational", "bolivarian",
           "federated", "socialist", "state", "islands", "saint", "new", "south", "north",
           "central", "african", "great", "britain", "northern", "ireland", "america", "lao",
           "union", "independent", "commonwealth", "grenadines", "principe", "herzegovina"}


def normalize_title(title) -> str:
    t = str(title).split(" : resolution")[0].lower()
    t = re.sub(r"\d+", " ", t)                 # years, session numbers
    t = re.sub(r"[^a-z\s]", " ", t)            # punctuation
    return re.sub(r"\s+", " ", t).strip()


def country_words(names) -> set:
    words = set()
    for n in names.dropna().unique():
        for w in re.sub(r"[^a-z\s]", " ", str(n).lower()).split():
            if w not in GENERIC and len(w) > 3:
                words.add(w)
    return words


def names_differ(t1: str, t2: str, cwords: set) -> bool:
    """True if one title names a country that the other does not."""
    a, b = set(t1.split()) & cwords, set(t2.split()) & cwords
    return a != b


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
    rmap.loc[rmap["sim"] < AUTO, "match_status"] = "manual_check"
    rmap.loc[rmap["resolution_t"].isin(dup) | rmap["resolution_tm1"].isin(dup),
             "match_status"] = "manual_check"

    # Review of manual_check pairs
    cwords = country_words(votes["member_state"])
    norm = reg.set_index("resolution")["title_norm"]
    man = rmap["match_status"] == "manual_check"
    rmap.loc[man & (rmap["sim"] == 1.0), "match_status"] = "manual_accept"
    differ = rmap.apply(lambda r: names_differ(norm[r["resolution_t"]], norm[r["resolution_tm1"]],
                                               cwords), axis=1)
    rmap.loc[man & differ & (rmap["sim"] < 1.0), "match_status"] = "rule_reject"
    for (ra, rb), d in MANUAL_DECISIONS.items():
        hit = (rmap["resolution_t"] == ra) & (rmap["resolution_tm1"] == rb)
        rmap.loc[hit, "match_status"] = "manual_" + d
    rmap["accepted"] = rmap["match_status"].isin(["auto", "manual_accept"])

    titles = res.set_index("resolution")["title"]
    rmap["title_t"] = rmap["resolution_t"].map(titles)
    rmap["title_tm1"] = rmap["resolution_tm1"].map(titles)
    rmap.to_parquet(PROC / "recurring_map.parquet", index=False)
    left = rmap[rmap["match_status"] == "manual_check"]
    left.to_csv(PROC / "manual_check.csv", index=False)

    print("\nMatched pairs:", len(rmap), "| status:", rmap["match_status"].value_counts().to_dict())
    print("Accepted pairs:", int(rmap["accepted"].sum()))
    if len(left):
        print("\nStill unreviewed (not used until decided in MANUAL_DECISIONS):")
        print(left[["resolution_t", "resolution_tm1", "sim"]].assign(
            title_t=left["title_t"].str[:50], title_tm1=left["title_tm1"].str[:50]).to_string(index=False))
    print("Share of regular-session resolutions matched to the previous session:",
          round(rmap["resolution_t"].nunique() / reg[reg["session"] > sessions[0]].shape[0], 3))

    # Preview of step 3: P5 vote switches on accepted pairs, by year of the session-t vote
    auto = rmap[rmap["accepted"]]
    p5 = votes[votes["iso3"].isin(P5)].pivot_table(index="resolution", columns="iso3",
                                                   values="vote", aggfunc="first")
    a = p5.reindex(auto["resolution_t"]).to_numpy()
    b = p5.reindex(auto["resolution_tm1"]).to_numpy()
    sw = pd.DataFrame((a != b) & ~pd.isna(a) & ~pd.isna(b), columns=p5.columns)
    sw["year"] = auto["resolution_t"].map(res.set_index("resolution")["year"]).to_numpy()
    print("\nP5 switches on accepted pairs, by year (preview of step 3):")
    print(sw.groupby("year")[P5].sum().astype(int).to_string())
    print("Total:", sw[P5].sum().astype(int).to_dict())


if __name__ == "__main__":
    main()