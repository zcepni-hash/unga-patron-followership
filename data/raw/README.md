# Raw data sources

Raw files are not tracked in Git (see `.gitignore`). Download each source into this folder under the file name shown, so the pipeline can find it.

| Source | What we use | Coverage | Where to get it | Save as |
|---|---|---|---|---|
| UN Digital Library voting data | All recorded UNGA votes | 2000–2026 | digitallibrary.un.org (General Assembly voting data) | `un_votes.csv` |
| Voeten et al., UNGA Voting Data | Cross-check of votes; BSV ideal points | 1946–2025 | Harvard Dataverse | `voeten_votes.csv`, `voeten_idealpoints.csv` |
| UNGA-DM (Fjelstul, Hug & Kilby) | Resolutions adopted without a vote | to 2023 | unvotes.unige.ch | `ungadm_decisions.xlsx` |
| US State Dept., Voting Practices in the UN | "Important votes" list per year | 2001–2025 | state.gov (annual reports) | `us_important_votes.csv` (hand-coded) |
| ATOP v5.1 | Defense pacts | 1815–2018 | atopdata.org | `atop_ddyr.csv` |
| DCAD (Kinne) | Defense cooperation agreements | 1980–2010 | correlatesofwar.org | `dcad_dyadic.csv` |
| SIPRI Arms Transfers Database | Major arms deliveries (TIV) | 1950–2025 | sipri.org | `sipri_trade_register.csv` |
| IMF IMTS (formerly DOTS) | Bilateral exports and imports | 1948–present | data.imf.org | `imf_imts.csv` |
| OECD CRS | Aid from the US, France, UK | 1973–present | stats.oecd.org | `oecd_crs.csv` |
| AidData | Chinese development finance | to 2021 | aiddata.org | `aiddata_china.csv` |
| V-Dem v16 | Electoral democracy index; executive changes | to 2025 | v-dem.net | `vdem_v16.csv` |
| World Bank WDI | GDP | 1960–present | data.worldbank.org | `wdi_gdp.csv` |
| SIPRI Milex | Military expenditure | 1949–2025 | sipri.org | `sipri_milex.csv` |
| Häge FPSIM v2 | κ and π for validation | 1946–2015 | Harvard Dataverse or R `peacesciencer` | `fpsim_v2.csv` |

## Notes

- Check each provider's terms before sharing any derived data. SIPRI and some others restrict redistribution.
- Record the download date of each file in the table below. Versions change, and results must be reproducible.

| File | Downloaded on | Version |
|---|---|---|
| | | |
