"""Step 6: state x event analysis file -> panel.

Output: data/processed/panel.parquet  (variables listed in docs/research_design_tr.md, "panel değişkenleri")

For each event e = (patron P, resolution r, session t) with direction d:
- Risk set R_e: non-P5 states voting in both sessions with room to move toward P
    (v_{t-1} < 1 if d = +1; v_{t-1} > 0 if d = -1).
- Y       = 1[d * (v_t - v_{t-1}) > 0]
- Y_ord   = -1 opposite / 0 none / 1 partial / 2 full (v_t == v_P,t)
- Y_delta = d * (v_t - v_{t-1})
- E       = share of the state's partners (ranks 1-10, session t-1) in R_e with Y = 1
- E_w, E_noEU, E_noreg: kappa-weighted and bloc-excluded versions
- E_near  = same, using ranks 11-20 (near-partner placebo)
- pD_mean, pclose_mean: partners' mean D_index and mean kappa with P
- Z_iv    = mean D_index of partners-of-partners who are not partners (Bramoullé IV)
- m_partners = |partners in R_e| / 10
- ties and controls merged from year t-1

Non-event baseline: build the same panel for recurring resolutions where P did not
switch, with Y_any (state changed its vote) and E_any (share of partners who changed),
event_type = 0.
"""


def main():
    # TODO: build risk sets and outcomes
    # TODO: exposures from backbone (ranks 1-10 and 11-20)
    # TODO: merge ties, controls, communities
    # TODO: non-event baseline panel
    raise NotImplementedError


if __name__ == "__main__":
    main()
