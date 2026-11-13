"""Step 4: co-voting network per session -> kappa, backbone, communities.

Outputs (data/processed/):
- kappa.parquet:       session, i, j, kappa_w, pi, n_shared
- backbone.parquet:    session, i, j, rank, kappa_w   (rank 1-20 kept: 1-10 partners, 11-20 near-partners)
- communities.parquet: session, iso3, comm, modularity

Weighted Cohen's kappa with linear weights w(a, b) = 1 - |a - b| on votes {0, 0.5, 1}:
    p_o = mean_r w(v_ir, v_jr)
    p_e = sum_a sum_b p_i(a) * p_j(b) * w(a, b)      (country-specific marginals)
    kappa = (p_o - p_e) / (1 - p_e)
Minimum 20 shared votes, otherwise NaN.

Backbone: each state's top-k partners by kappa, P5 excluded, k = 10 (sensitivity: 5, 15).
Communities: Leiden (modularity, resolution 1.0) on the symmetrized backbone,
100 seeds, keep the highest-modularity partition, report NMI across seeds.
"""

K = 10
MIN_SHARED = 20
N_SEEDS = 100
LEVELS = (0.0, 0.5, 1.0)


def weighted_kappa(vi, vj):
    """vi, vj: aligned arrays of votes on shared resolutions (no NaN)."""
    # TODO: implement formula above
    raise NotImplementedError


def main():
    # TODO: for each session: pivot votes_long, compute pairwise kappa (and Scott's pi)
    # TODO: rank partners, keep ranks 1-20
    # TODO: igraph + leidenalg communities
    raise NotImplementedError


if __name__ == "__main__":
    main()
