# Step 7: models and figures
# Input:  data/processed/panel.parquet
# Design: docs/research_design_tr.md, "Tahmin modeli ve hipotez testleri"

library(arrow)
library(fixest)
library(modelsummary)

panel <- read_parquet("data/processed/panel.parquet")

controls <- ~ close_kappa + v_prev + regime_gap + ideo_gap + leader_change +
  m_partners + pD_mean + pclose_mean + log_gdp + log_milex

# Main model: H1 (beta), H2 (gamma), H3 (delta)
# m_main <- feols(Y ~ D_index + E + D_index:S + .[controls]
#                 | event_id + un_region,
#                 cluster = ~ iso3 + event_id, data = panel)

# H2 robustness: event x region fixed effects
# m_evreg <- feols(Y ~ D_index + E + .[controls] | event_id^un_region,
#                  cluster = ~ iso3 + event_id, data = panel)

# Near-partner placebo: test gamma - gamma_near > 0
# m_near <- feols(Y ~ D_index + E + E_near + .[controls] | event_id + un_region,
#                 cluster = ~ iso3 + event_id, data = panel)

# Bramoullé IV
# m_iv <- feols(Y ~ D_index + .[controls] | event_id + un_region | E ~ Z_iv,
#               cluster = ~ iso3 + event_id, data = panel)

# Channel comparison: nested models M0-M3, within R2, dominance analysis (domir)

# TODO: tables with modelsummary(), coefficient plot with ggplot2
