"""Step 5: vertical ties -> ties (state x patron x year).

Output: data/processed/ties.parquet
Columns: iso3, patron, year, D_pact, D_dca, D_arms_main, D_arms_share, D_exp, D_imp, D_aid, D_index

- D_pact:       ATOP defense pact (2019-2025: carry the 2018 value forward)
- D_dca:        any DCA with the patron, 1980-2010 (Kinne DCAD)
- D_arms_main:  patron is the largest supplier of the state's arms imports (TIV), window t-5..t-1
- D_arms_share: patron's share of TIV in the same window
- D_exp/D_imp:  patron's share of the state's exports / imports (IMF IMTS)
- D_aid:        aid from the patron / state GNI (OECD CRS; AidData for China; missing for Russia)
- D_index:      mean of the z-scored components
"""


def main():
    # TODO: load each source, convert country codes to ISO3 (COW codes for ATOP/DCAD)
    # TODO: build the five patron columns per state-year
    # TODO: z-score and average into D_index
    raise NotImplementedError


if __name__ == "__main__":
    main()
