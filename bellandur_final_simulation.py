import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# 1. Site parameters & 20-year horizon (2026-2045)
nyears = 20
years = np.arange(2026, 2026 + nyears + 1)
nsamples = 100

b_base = 0.52
q = 2.0
m = 1.0
r_base = 1.0
p_init = 2.50
p_crit = 0.50

# Lognormal perturbation parameters
mean_ep = 0.03
var_ep = 1e-4
mu = np.log(mean_ep**2 / np.sqrt(mean_ep**2 + var_ep))
sigma = np.sqrt(np.log(1 + var_ep / (mean_ep**2)))

def run_stochastic_lake(a_val, b_val, r_val, n_ens=100):
    x_det = np.zeros(nyears + 1)
    x_det[0] = p_init
    for t in range(nyears):
        rec = r_val * (x_det[t]**q) / (m**q + x_det[t]**q)
        x_det[t + 1] = max(0.01, x_det[t] - b_val * x_det[t] + a_val + rec)

    x_stoch = np.zeros((nyears + 1, n_ens))
    x_stoch[0, :] = p_init
    for s in range(n_ens):
        eps = np.random.lognormal(mu, sigma, size=nyears)
        for t in range(nyears):
            rec = r_val * (x_stoch[t, s]**q) / (m**q + x_stoch[t, s]**q)
            x_stoch[t + 1, s] = max(0.01, x_stoch[t, s] - b_val * x_stoch[t, s] + a_val + rec + eps[t])
    return x_det, x_stoch

# Simulate 4 interventions
scenarios = [
    ("S1: Baseline (BAU)", 0.35, b_base, r_base, "red", "-o"),
    ("S2: Secondary STP Only", 0.07, b_base, r_base, "darkorange", "-s"),
    ("S3: STP + Wetlands", 0.03, 0.62, r_base, "royalblue", "-^"),
    ("S4: STP + Wetlands + Dredging", 0.04, 0.55, 0.30, "forestgreen", "-D"),
]

results = {}
for name, a_v, b_v, r_v, col, mk in scenarios:
    x_d, x_s = run_stochastic_lake(a_v, b_v, r_v, nsamples)
    rel = np.mean(x_s[1:, :] < p_crit) * 100.0
    final_med = np.median(x_s[-1, :])
    results[name] = (x_d, x_s, rel, final_med, col, mk)

# FIGURE 1: Stochastic 20-Year Trajectories & Reliability (100 Monsoon Runs)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8), dpi=300)

for name, (x_d, x_s, rel, final_med, col, mk) in results.items():
    p10 = np.percentile(x_s, 10, axis=1)
    p90 = np.percentile(x_s, 90, axis=1)
    ax1.fill_between(years, p10, p90, color=col, alpha=0.15)
    ax1.plot(years, x_d, mk, color=col, markersize=3.5, lw=1.8, label=f"{name}")

ax1.axhline(p_crit, color="black", linestyle="--", lw=1.3, label="Restoration Target (0.50 mg/L)")
ax1.set_xlabel("Year", fontsize=10)
ax1.set_ylabel("Lake Phosphorus Concentration, P [mg/L]", fontsize=10)
ax1.set_title("(a) 20-Year Trajectories (Deterministic & 10-90% Bands)", fontsize=10.5, fontweight="bold")
ax1.set_ylim(0, 3.0)
ax1.legend(loc="upper right", fontsize=8.2)
ax1.grid(True, alpha=0.3)

# Panel (b): Reliability (% of lake-years below 0.50 mg/L) - Fixed x-axis spacing
short_names = ["S1: BAU", "S2: STP Only", "S3: STP+Wet", "S4: Full+Dredge"]
reliabilities = [results[s[0]][2] for s in scenarios]
colors = [s[4] for s in scenarios]

bars = ax2.bar(short_names, reliabilities, color=colors, alpha=0.85, width=0.52, edgecolor="black")
for bar, val in zip(bars, reliabilities):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 2.0, f"{val:.1f}%", ha="center", fontweight="bold", fontsize=9.5)

ax2.set_ylabel("Reliability: % Years with P < 0.50 mg/L", fontsize=10)
ax2.set_title("(b) Restoration Reliability under Monsoon Variability", fontsize=10.5, fontweight="bold")
ax2.set_ylim(0, 105)
ax2.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("Figure1_Stochastic_Trajectories.png", dpi=300)
plt.close()

# FIGURE 2: Parameter Sensitivity (b vs r) & Cost-Effectiveness Trade-off
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8), dpi=300)

# Panel (a): 2D Sensitivity Heatmap of 2045 Phosphorus for S3/S4-level external load (a=0.04)
b_grid = np.linspace(0.40, 0.70, 50)
r_grid = np.linspace(0.20, 1.10, 50)
B_mesh, R_mesh = np.meshgrid(b_grid, r_grid)
P_end_grid = np.zeros_like(B_mesh)

for i in range(len(r_grid)):
    for j in range(len(b_grid)):
        x_tmp = p_init
        for _ in range(nyears):
            x_tmp = x_tmp - B_mesh[i, j]*x_tmp + 0.04 + R_mesh[i, j]*(x_tmp**2)/(1.0 + x_tmp**2)
        P_end_grid[i, j] = x_tmp

cp = ax1.contourf(B_mesh, R_mesh, P_end_grid, levels=15, cmap="RdYlGn_r")
cs = ax1.contour(B_mesh, R_mesh, P_end_grid, levels=[0.50], colors="black", linewidths=2, linestyles="--")
ax1.clabel(cs, fmt="Target P = 0.50 mg/L", fontsize=9)
fig.colorbar(cp, ax=ax1, label="Final 2045 Phosphorus [mg/L]")

ax1.scatter([0.52, 0.62, 0.55], [1.00, 1.00, 0.30], color="blue", s=60, zorder=5, edgecolor="white")
ax1.annotate("S2 (a=0.07)", (0.52, 1.00), textcoords="offset points", xytext=(-10, -14), fontsize=8.5, fontweight="bold")
ax1.annotate("S3 (Wetlands)", (0.62, 1.00), textcoords="offset points", xytext=(-35, -14), fontsize=8.5, fontweight="bold")
ax1.annotate("S4 (Dredging)", (0.55, 0.30), textcoords="offset points", xytext=(6, 4), fontsize=8.5, fontweight="bold")

ax1.set_xlabel("Effective Net Loss Rate, b [yr^-1]", fontsize=10)
ax1.set_ylabel("Max Internal Sediment Recycling, r [mg/L/yr]", fontsize=10)
ax1.set_title("(a) Sensitivity of 2045 Phosphorus to b and r (at a = 0.04)", fontsize=10.5, fontweight="bold")

# Panel (b): Capital + O&M Cost vs Final Phosphorus Reduction - Fixed label placement
est_costs = [150, 950, 1150, 1650]
p_reduction_pct = [(p_init - results[s[0]][3]) / p_init * 100.0 for s in scenarios]

for idx, (s, cost, red) in enumerate(zip(scenarios, est_costs, p_reduction_pct)):
    ax2.scatter(cost, red, color=s[4], s=120, marker=s[5][1], edgecolor="black", zorder=5, label=s[0])
    if idx == 3:
        offset_x, offset_y = -68, -16
    else:
        offset_x, offset_y = -15, 8
    ax2.annotate(f"Rs.{cost} Cr\n({red:.0f}% cut)", (cost, red), textcoords="offset points", xytext=(offset_x, offset_y), fontsize=8.5)

ax2.set_xlabel("Estimated 20-Year Infrastructure & O&M Cost [Rs. Crores]", fontsize=10)
ax2.set_ylabel("20-Year Lake Phosphorus Reduction [%]", fontsize=10)
ax2.set_title("(b) Cost vs. Phosphorus Reduction Trade-off", fontsize=10.5, fontweight="bold")
ax2.set_xlim(0, 1950)
ax2.set_ylim(0, 108)
ax2.grid(True, alpha=0.3)
ax2.legend(loc="lower right", fontsize=8)

plt.tight_layout()
plt.savefig("Figure2_Sensitivity_Cost_Tradeoff.png", dpi=300)
plt.close()
