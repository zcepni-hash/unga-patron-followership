# Who Follows a Great Power?
### Patron Vote Switches and Followership in the UN General Assembly

**Authors:** Zehra Çepni · Mükerrem Said Özdemir
**Course:** DSAI 581 Network Analysis, Boğaziçi University (Fall 2026)
**Status:** Work in progress. The research design is complete; data collection and coding are under way.

---

## Research question

> When a great power switches its vote on a recurring UNGA resolution, do states follow the patron they are tied to, or the network of states they usually vote with?

While a patron's position stays the same, *following* it and simply *agreeing* with it look identical in voting data. A patron that **switches** its vote separates the two. Between 2001 and 2025 the five permanent members of the Security Council switched their vote on a recurring resolution 209 times. Each switch is a small natural test of who moves with the patron. The February 2025 Ukraine resolution, on which the United States voted with Russia, is the most visible recent case.

## Hypotheses

| | Channel | Hypothesis |
|---|---|---|
| **H1** | Vertical | States more dependent on the patron (security, trade, aid) are more likely to move in the patron's direction. |
| **H2** | Horizontal | States whose voting partners moved with the patron are more likely to move too, net of their own ties to the patron. |
| **H3** | Condition | The effect of dependence is stronger on votes the patron treats as important. |

The research question is answered by comparing the standardized effects and the explanatory power of the vertical block (H1) and the horizontal variable (H2).

## Design in brief

- **Unit of analysis:** state × event, about 25,000–40,000 rows. An *event* is a P5 member voting differently on the same recurring resolution than in the previous session.
- **Outcome:** `Y = 1` if the state moved in the patron's direction (votes coded yes = 1, abstain = 0.5, no = 0; absences are treated as missing).
- **Multiplex network:** one node set (UN member states) with four layers:

  | Layer | Edge | Role |
  |---|---|---|
  | L1 Co-voting | Weighted Cohen's κ, each state's 10 closest partners (patrons excluded) | Horizontal channel (H2), communities |
  | L2 Alliance | ATOP defense pact | Vertical channel (edges to the patron) |
  | L3 Trade | Export and import shares | Vertical channel |
  | L4 Arms | SIPRI main supplier, TIV share | Vertical channel |

- **Model:** linear probability model with event fixed effects, standard errors clustered by state and event:

  ```
  Y_ie = α_e + β·D_iP + γ·E_ie + δ·(D_iP × S_e) + θ'X_i + μ_region + ε_ie
  ```

  `D` = dependence on the patron, `E` = share of voting partners who moved with the patron, `S` = salience of the vote.
- **Identification checks:** pre-trend placebo, a wrong-patron placebo, a subsample of switches that follow the patron's own change of government, event × region fixed effects, a "near-partner" placebo (states ranked 11–20 by κ), a non-event baseline, and a Bramoullé-type instrument.
- **Descriptive:** a directed follower network (state → patron) and an overlap analysis of the multiplex layers.

The full design and codebook are in [`docs/research_design_tr.md`](docs/research_design_tr.md). The literature review and coding decisions are in [`docs/conceptual_framework_tr.pdf`](docs/conceptual_framework_tr.pdf). Both are in Turkish.

## Data

All recorded UNGA votes, 2000–2026, plus tie and control data from public sources. Raw data are **not** stored in this repository; see [`data/raw/README.md`](data/raw/README.md) for sources and download instructions.

## Repository structure

```
├── data/
│   ├── raw/            # downloaded source files (not tracked, see README inside)
│   └── processed/      # pipeline outputs (Parquet, not tracked)
├── src/                # Python pipeline, steps 01–06
├── R/                  # models and figures, step 07
├── notebooks/          # exploration
├── figures/            # final figures
└── docs/               # research design, codebook, literature review
```

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1 | `src/01_votes.py` | `votes_long`: one row per state × roll call |
| 2 | `src/02_match_resolutions.py` | `recurring_map`: the same resolution matched across sessions |
| 3 | `src/03_events.py` | `events`: P5 vote switches |
| 4 | `src/04_network.py` | `kappa`, `backbone`, `communities` per session |
| 5 | `src/05_ties.py` | `ties`: state × patron × year dependence measures |
| 6 | `src/06_panel.py` | `panel`: state × event analysis file |
| 7 | `R/07_models.R` | regression tables and figures |

## Tools

Python (pandas, igraph, leidenalg, scikit-learn, geopandas) · R (fixest, modelsummary, ggraph) · QGIS · Excel

## License

Code: MIT (see [`LICENSE`](LICENSE)). Data remain under the terms of their original providers.
