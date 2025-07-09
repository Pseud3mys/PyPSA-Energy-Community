import pandas as pd

# =============================================================================
# --- 0. System and Technology Configuration Parameters ---
# =============================================================================

# --- General System Configuration ---
# Maximum total investment budget for all new assets (Solar, Wind, Biomass, Hydro).
CAPEX_BUDGET = 250000  # Budget in Euros (€)

# Target annual energy demand for the system. This is used to scale the consumption profile.
ANNUAL_ENERGY_DEMAND = 250  # MWh/year
# Castanheira de Pera's annual energy demand is around 870 MWh.

# --- Solar Power Configuration ---
CAPEX_SOLAR = 500 * 1e3      # Investment cost per MWp (€/MWp)
LIFE_SOLAR = 25              # Economic lifetime in years
capital_cost_solar = CAPEX_SOLAR / LIFE_SOLAR  # Annualized capital cost (€/MWp/year)

# --- Wind Power Configuration ---
CAPEX_WIND = 1100 * 1e3      # Investment cost per MWp (€/MWp)
LIFE_WIND = 20               # Economic lifetime in years
capital_cost_wind = CAPEX_WIND / LIFE_WIND  # Annualized capital cost (€/MWp/year)

# --- Biomass ORC (Organic Rankine Cycle) Configuration ---
CAPEX_ORC_BIOMASS = 400000 / 50 * 1e3  # investment cost per MW (€/MW)
salary_get_waste = 22000              # Annual salary for fuel collection and treatment (€/year)
LIFE_ORC_Biomass = 20                 # Economic lifetime in years
# produce 4 time more heat than electricity...

# Annualized cost includes both capital cost and operational (salary) costs.
capital_cost_ORC_Biomass = (CAPEX_ORC_BIOMASS / LIFE_ORC_Biomass) + salary_get_waste

# --- Hydro Reservoir Configuration ---
# This section defines a pre-existing, fixed-capacity hydro plant.
IS_HYDRO_FIXED = True            # If True, the hydro plant's capacity is not optimized.
Cout_turbine_30kw = 120000       # Total cost of the existing 30 kW turbine (€)
INSTALLED_POWER_HYDRO = 30 / 1000 # Installed power capacity in MW
CAPEX_HYDRO = Cout_turbine_30kw / INSTALLED_POWER_HYDRO  # Effective investment cost per MWp (€/MWp)
LIFE_HYDRO = 40                  # Economic lifetime in years
RESERVOIR_CAPACITY_HYDRO = 5     # Reservoir storage capacity in hours of full power operation
capital_cost_hydro = CAPEX_HYDRO / LIFE_HYDRO  # Annualized capital cost (€/MW/year)

# --- Electric Car (V2G - Vehicle-to-Grid) Configuration ---
# Assumes electric cars can act as battery storage to help balance the grid.
mean_electric_car_capacity = 80 * 1e-3  # Average battery capacity of one electric car (MWh)
number_of_chargers = 2                  # Number of available V2G chargers
max_power_per_charger = 22 * 1e-3       # Maximum charging/discharging power per charger (MW)
# Total power capacity of all V2G chargers.
power_electric_car = number_of_chargers * max_power_per_charger  # Total power (MW)
# Total storage capacity in hours at maximum power.
battery_capacity_electric_car_hours = (number_of_chargers * mean_electric_car_capacity) / power_electric_car


# --- Grid Interaction Configuration ---
# Sets the maximum power that can be sold back to the grid.
GRID_INJECTION_LIMIT = 0.7       # As a percentage (%) of the system's maximum demand

# =============================================================================
# --- Function to Summarize Optimization Results ---
# =============================================================================
def sim_recap(n):
    """
    Prints a detailed summary of the optimized energy system, including costs,
    capacities, and energy production for each technology.
    """
    print("\n" + "=" * 60)
    print("      OPTIMAL SYNTHESIS OF THE ENERGY SYSTEM")
    print("=" * 60)
    print("\nAnalysis of production and storage technologies:\n")

    # -- Solar Results --
    # Retrieve optimized values, using .get() to avoid errors if the asset is not in the model.
    p_nom_solar = n.generators.p_nom_opt.get('Solar', 0)
    e_prod_solar = n.generators_t.p.get('Solar', pd.Series([0])).sum()
    capex_total_solar = p_nom_solar * CAPEX_SOLAR / 1e3  # Total investment in k€
    # Calculate Levelized Cost of Energy (LCOE) for solar.
    ann_cost_solar = p_nom_solar * n.generators.capital_cost.get('Solar', 0)
    lcoe_solar = (ann_cost_solar / e_prod_solar / 1e3) if e_prod_solar > 1 else 0
    print("--- Solar ---")
    print(f"  {'Installed Power':<28}: {p_nom_solar:>8.2f} MW")
    print(f"  {'Total Investment':<28}: {capex_total_solar:>8.2f} k€")
    print(f"  {'Annual Energy Produced':<28}: {e_prod_solar:>8.2f} MWh")
    print(f"  {'Production Cost (LCOE)':<28}: {lcoe_solar:>8.4f} €/kWh\n")

    # -- Wind Results --
    p_nom_wind = n.generators.p_nom_opt.get('Wind', 0)
    e_prod_wind = n.generators_t.p.get('Wind', pd.Series([0])).sum()
    capex_total_wind = p_nom_wind * CAPEX_WIND / 1e3  # Total investment in k€
    # Calculate LCOE for wind.
    ann_cost_wind = p_nom_wind * n.generators.capital_cost.get('Wind', 0)
    lcoe_wind = (ann_cost_wind / e_prod_wind / 1e3) if e_prod_wind > 1 else 0
    print("--- Wind ---")
    print(f"  {'Installed Power':<28}: {p_nom_wind:>8.2f} MW")
    print(f"  {'Total Investment':<28}: {capex_total_wind:>8.2f} k€")
    print(f"  {'Annual Energy Produced':<28}: {e_prod_wind:>8.2f} MWh")
    print(f"  {'Production Cost (LCOE)':<28}: {lcoe_wind:>8.4f} €/kWh\n")

    # -- Biomass ORC Results --
    p_nom_biomass = n.generators.p_nom_opt.get('Biomass ORC', 0)
    e_prod_biomass = n.generators_t.p.get('Biomass ORC', pd.Series([0])).sum()
    capex_total_biomass = p_nom_biomass * CAPEX_ORC_BIOMASS / 1e3  # Total investment in k€
    # Calculate LCOE for biomass.
    ann_cost_biomass = p_nom_biomass * n.generators.capital_cost.get('Biomass ORC', 0)
    lcoe_biomass = (ann_cost_biomass / e_prod_biomass / 1e3) if e_prod_biomass > 1 else 0
    print("--- Biomass ORC ---")
    print(f"  {'Installed Power':<28}: {p_nom_biomass:>8.2f} MW")
    print(f"  {'Total Investment':<28}: {capex_total_biomass:>8.2f} k€")
    print(f"  {'Annual Energy Produced':<28}: {e_prod_biomass:>8.2f} MWh")
    print(f"  {'Production Cost (LCOE)':<28}: {lcoe_biomass:>8.4f} €/kWh\n")

    # -- Electric Car Battery (V2G) Results --
    car_battery_name = 'Electric Car Battery'
    p_nom_battery = n.storage_units.p_nom_opt.get(car_battery_name, 0)
    e_nom_battery = n.storage_units.max_hours.get(car_battery_name, 0) * p_nom_battery
    e_dispatch_battery = n.storage_units_t.p_dispatch.get(car_battery_name, pd.Series([0])).sum()
    # Calculate total investment based on optimized power.
    capex_total_battery = p_nom_battery * n.storage_units.capital_cost.get(car_battery_name, 0) / 1e3
    # Calculate the Levelized Cost of Storage (LCOS).
    ann_cost_battery = p_nom_battery * n.storage_units.capital_cost.get(car_battery_name, 0)
    lcoe_battery = (ann_cost_battery / e_dispatch_battery / 1e3) if e_dispatch_battery > 1 else 0
    print("--- Electric Car Battery ---")
    print(f"  {'Installed Power':<32}: {p_nom_battery:>8.2f} MW")
    print(f"  {'Storage Capacity':<32}: {e_nom_battery:>8.2f} MWh")
    print(f"  {'Total Investment':<32}: {capex_total_battery:>8.2f} k€")
    print(f"  {'Annual Energy Dispatched':<32}: {e_dispatch_battery:>8.2f} MWh")
    print(f"  {'Storage/Dispatch Cost (LCOS)':<32}: {lcoe_battery:>8.4f} €/kWh\n")

    # -- Hydro Results --
    hydro_name = 'Hydro Reservoir'
    p_nom_hydro = n.storage_units.p_nom_opt.get(hydro_name, 0)
    e_nom_hydro = n.storage_units.max_hours.get(hydro_name, 0) * p_nom_hydro
    e_dispatch_hydro = n.storage_units_t.p_dispatch.get(hydro_name, pd.Series([0])).sum()
    # Calculate total investment based on optimized capacity.
    capex_total_hydro = p_nom_hydro * CAPEX_HYDRO / 1e3
    # Calculate the Levelized Cost of Storage (LCOS) for hydro.
    ann_cost_hydro = p_nom_hydro * n.storage_units.capital_cost.get(hydro_name, 0)
    lcoe_hydro = (ann_cost_hydro / e_dispatch_hydro / 1e3) if e_dispatch_hydro > 1 else 0
    print("--- Hydro (Reservoir + Turbine) ---")
    print(f"  {'Installed Power':<32}: {p_nom_hydro:>8.2f} MW")
    print(f"  {'Storage Capacity':<32}: {e_nom_hydro:>8.2f} MWh")
    print(f"  {'Total Investment':<32}: {capex_total_hydro:>8.2f} k€")
    print(f"  {'Annual Energy Dispatched':<32}: {e_dispatch_hydro:>8.2f} MWh")
    print(f"  {'Annual Inflow Energy':<32}: {n.storage_units_t.inflow[hydro_name].sum():>8.2f} MWh")
    print(f"  {'Storage/Dispatch Cost (LCOS)':<32}: {lcoe_hydro:>8.4f} €/kWh\n")

    # -- Grid Exchange Calculations --
    demand_mwh = n.loads_t.p_set['Consumption'].sum()
    achat_mwh = -n.links_t.p1["Grid Import"].sum()  # Energy purchased from the grid
    vente_mwh = n.links_t.p0["Grid Export"].sum()  # Energy sold to the grid
    cout_achat_k_eur = (-n.links_t.p1['Grid Import'] * n.links_t.marginal_cost['Grid Import']).sum() / 1e3
    revenu_vente_k_eur = (n.links_t.p0['Grid Export'] * n.links_t.marginal_cost['Grid Export']).sum() / 1e3
    print("--- Grid Purchases ---")
    print(f"  {'Total Energy Purchased':<28}: {achat_mwh:>8.2f} MWh/year")
    print(f"  {'Total Purchase Cost':<28}: {cout_achat_k_eur:>8.2f} k€/year\n")
    print("--- Grid Sales ---")
    print(f"  {'Total Energy Sold':<28}: {vente_mwh:>8.2f} MWh/year")
    print(f"  {'Total Sales Revenue':<28}: {-abs(revenu_vente_k_eur):>8.2f} k€/year\n")

    # -- System-Wide Financial Summary --
    total_cost_k_eur = n.objective / 1e3
    # Benchmark: Cost if all energy was purchased from the grid without a local system.
    cout_achat_k_eur_sans_hybride = (n.links_t.marginal_cost['Grid Import'] * n.loads_t.p_set['Consumption']).sum() / 1e3
    total_investement_k_eur = capex_total_solar + capex_total_wind + capex_total_hydro
    print("--- Overall System Recap ---")
    print(f"  {'Benchmark Cost (Grid Only)':<35}: {cout_achat_k_eur_sans_hybride:>8.2f} k€/year")
    print(f"  {'Total Annualized Cost (Hybrid)':<35}: {total_cost_k_eur:>8.2f} k€/year")
    print(f"  {'Total Investment (S+W+H)':<35}: {total_investement_k_eur:>8.2f} k€")
    print(f"  {'Net Grid Cost (Purchase-Sale)':<35}: {abs(cout_achat_k_eur) - abs(revenu_vente_k_eur):>8.2f} k€/year")
    print(f"  {'Total Annual Consumption':<35}: {demand_mwh:>8.2f} MWh/year\n")
