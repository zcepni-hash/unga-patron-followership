"""Step 3: P5 vote switches -> events.

Output: data/processed/events.parquet
Columns: event_id, patron, rcid_t, rcid_tm1, session, dir, S, p_govchange

- Event: patron's vote on rcid_t differs from its vote on the matched rcid_tm1.
- dir = sign(v_P,t - v_P,t-1) in {-1, +1}.
- S (salience): 1 if the resolution is on the US State Dept. "important votes" list
  (US events); proxy for all patrons: patron is main sponsor or emergency special session.
- p_govchange: 1 if the switch is in the first session after a change of head of
  government in the patron (e.g. US 2009, 2017, 2021, 2025).
"""

P5 = ["USA", "CHN", "RUS", "FRA", "GBR"]


def main():
    # TODO: join votes_long to recurring_map for P5 only
    # TODO: keep pairs where vote differs and both votes are non-missing
    # TODO: add S and p_govchange
    raise NotImplementedError


if __name__ == "__main__":
    main()
