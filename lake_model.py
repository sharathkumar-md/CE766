import numpy as np
import matplotlib.pyplot as plt

# simulation timeframe
nyears = 20
years = np.arange(2026, 2026 + nyears + 1)

# site geometry and parameters from IISc ETR 116
area_ha = 380.0
depth_m = 2.0
volume_m3 = area_ha * 1e4 * depth_m
inflow_mld = 500.0
hrt_days = volume_m3 / (inflow_mld * 1e3)

# calibrated model parameters
b_base = 0.52
q = 2.0
m = 1.0
r_base = 1.0
p_init = 2.50
p_crit = 0.50

def run_lake_model(anth, b, r, q_val=2.0, m_val=1.0, x0=2.50, steps=20):
    x = np.zeros(steps + 1)
    x[0] = x0
    for t in range(steps):
        recycling = r * (x[t] ** q_val) / (m_val ** q_val + x[t] ** q_val)
        x[t + 1] = x[t] - b * x[t] + anth[t] + recycling
    return x

# scenario 1: business as usual
a_s1 = np.full(nyears, 0.35)
x_s1 = run_lake_model(a_s1, b=b_base, r=r_base)

# scenario 2: stp expansion only
a_s2 = np.full(nyears, 0.07)
x_s2 = run_lake_model(a_s2, b=b_base, r=r_base)

# scenario 3: stp + constructed wetlands
a_s3 = np.full(nyears, 0.03)
x_s3 = run_lake_model(a_s3, b=0.62, r=r_base)

# scenario 4: comprehensive restoration (stp + wetlands + dredging)
a_s4 = np.full(nyears, 0.04)
x_s4 = run_lake_model(a_s4, b=0.55, r=0.30)

# plotting results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=300)

p_grid = np.linspace(0, 3.0, 300)
natural_loss = b_base * p_grid
input_s2 = 0.07 + r_base * (p_grid**q) / (m**q + p_grid**q)
input_s4 = 0.04 + 0.30 * (p_grid**q) / (m**q + p_grid**q)

ax1.plot(p_grid, natural_loss, 'k--', lw=2, label='Natural removal (b*P)')
ax1.plot(p_grid, input_s2, 'r-', lw=2, label='Total P input: S2 (STP only)')
ax1.plot(p_grid, input_s4, 'g-', lw=2, label='Total P input: S4 (STP + dredging)')
ax1.axvline(p_crit, color='gray', linestyle=':', label='Target threshold (0.5 mg/L)')
ax1.set_xlabel('Lake Phosphorus Concentration, P [mg/L]')
ax1.set_ylabel('Annual Phosphorus Flux [mg/L/yr]')
ax1.set_title('(a) Equilibrium Flux & Hysteresis Trap')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)

ax2.plot(years, x_s1, 'r-o', markersize=4, lw=1.8, label='S1: Baseline (a=0.35, r=1.0)')
ax2.plot(years, x_s2, color='darkorange', marker='s', markersize=4, lw=1.8, label='S2: STP only (a=0.07, r=1.0)')
ax2.plot(years, x_s3, 'b-^', markersize=4, lw=1.8, label='S3: STP + Wetlands (a=0.03, b=0.62)')
ax2.plot(years, x_s4, 'g-D', markersize=4, lw=1.8, label='S4: STP + Wetlands + Dredging (a=0.04, r=0.30)')
ax2.axhline(p_crit, color='gray', linestyle=':', lw=1.5, label='Target threshold (0.5 mg/L)')

ax2.set_xlabel('Year')
ax2.set_ylabel('Lake Phosphorus Concentration, P [mg/L]')
ax2.set_title('(b) 20-Year Concentration Trajectory')
ax2.set_ylim(0, 3.0)
ax2.legend(loc='upper right', fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Bellandur_Preliminary_Results.png', dpi=300)
plt.show()
