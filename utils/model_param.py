import pandas as pd

# =============================================================================
# --- 0. System and Technology Configuration Parameters ---
# =============================================================================

# --- General System Configuration ---
# Maximum total investment budget for all new assets (Solar, Wind, Biomass, Hydro).
CAPEX_BUDGET = 250000  # Budget in Euros (€)

# Target annual energy demand for the system. This is used to scale the consumption profile.
ANNUAL_ENERGY_DEMAND = 500  # MWh/year
# Castanheira de Pera's annual energy demand is around 8700 MWh.

# --- Solar Power Configuration ---
CAPEX_SOLAR_MW = 1100 * 1e3      # Investment cost per MWp (€/MWp) | Source: 1100 €/kW
LIFE_SOLAR = 30               # Economic lifetime in years
OPEX_SOLAR_MW_YEAR = 8 * 1e3          # Annual operational cost in euros/MW/year | Source: 8 €/kW/an
#
capital_cost_solar = CAPEX_SOLAR_MW / LIFE_SOLAR + OPEX_SOLAR_MW_YEAR  # Annualized capital cost (€/MWp/year)

# --- Wind Power Configuration ---
CAPEX_WIND_MW = 1300 * 1e3       # Investment cost per MWp (€/MWp) | Source: 1300 €/kW
LIFE_WIND = 25                # Economic lifetime in years
OPEX_WIND_MW_YEAR = 34 * 1e3          # Annual operational cost in euros/MW/year | Source: 34 €/kW/an
#
capital_cost_wind = CAPEX_WIND_MW / LIFE_WIND + OPEX_WIND_MW_YEAR # Annualized capital cost (€/MWp/year)

# --- Hydro Reservoir Configuration ---
# This section defines a pre-existing, fixed-capacity hydro plant.
IS_HYDRO_FIXED = True             # If True, the hydro plant's capacity is not optimized.
CAPEX_HYDRO_MW = 3800 * 1e3       # Investment cost per MWp (€/MWp) | Source: 3800 €/kW
LIFE_HYDRO = 50                   # Economic lifetime in years
OPEX_HYDRO_MW_YEAR = 70 * 1e3             # Annual operational cost in euros/MW/year | Source: 70 €/kW/an
RESERVOIR_CAPACITY_HYDRO = 5      # Reservoir storage capacity in hours of full power operation
#
capital_cost_hydro = CAPEX_HYDRO_MW / LIFE_HYDRO + OPEX_HYDRO_MW_YEAR # Annualized capital cost (€/MW/year)

# --- Biomass ORC (Organic Rankine Cycle) Configuration ---
CAPEX_BIOMASS_MW = 18000 * 1e3 # investment cost per MW (€/MW) | Source: 18000 €/kW
OPEX_BIOMASS_MW_YEAR = 600 * 1e3        # Annual operational cost in euros/MW/year | Source: 600 €/kW/an
LIFE_ORC_Biomass = 25           # Economic lifetime in years
# produce 4 time more heat than electricity...
# Annualized cost includes both capital cost and operational (salary) costs.
capital_cost_ORC_Biomass = (CAPEX_BIOMASS_MW / LIFE_ORC_Biomass) + OPEX_BIOMASS_MW_YEAR


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
GRID_INJECTION_LIMIT = 1.0       # As a percentage (%) of the system's maximum demand

# =============================================================================
# --- Function to Summarize Optimization Results ---
# =============================================================================
def print_parameters_summary():
    # --- Structuring data for display ---
    technologies = [
        {
            "Name": "Solar PV",
            "CAPEX (€/kW)": CAPEX_SOLAR_MW / 1000,
            "OPEX (€/kW/year)": OPEX_SOLAR_MW_YEAR / 1000,
            "Lifetime (years)": LIFE_SOLAR,
            "Notes": ""
        },
        {
            "Name": "Small Wind",
            "CAPEX (€/kW)": CAPEX_WIND_MW / 1000,
            "OPEX (€/kW/year)": OPEX_WIND_MW_YEAR / 1000,
            "Lifetime (years)": LIFE_WIND,
            "Notes": ""
        },
        {
            "Name": "Biomass ORC",
            "CAPEX (€/kW)": CAPEX_BIOMASS_MW / 1000,
            "OPEX (€/kW/year)": OPEX_BIOMASS_MW_YEAR / 1000,
            "Lifetime (years)": LIFE_ORC_Biomass,
            "Notes": ""
        },
        {
            "Name": "Micro-Hydro",
            "CAPEX (€/kW)": CAPEX_HYDRO_MW / 1000,
            "OPEX (€/kW/year)": OPEX_HYDRO_MW_YEAR / 1000,
            "Lifetime (years)": LIFE_HYDRO,
            "Notes": f"Reservoir: {RESERVOIR_CAPACITY_HYDRO}h | Fixed: {IS_HYDRO_FIXED}"
        }
    ]

    # --- Displaying the parameters ---
    print("\n" + "=" * 75)
    print("           Verification of All Simulation Parameters")
    print("=" * 75)

    print("\n--- General System & Grid Configuration ---")
    print(f"{'Total CAPEX Budget:':<35} {CAPEX_BUDGET:,.0f} €")
    print(f"{'Target Annual Energy Demand:':<35} {ANNUAL_ENERGY_DEMAND} MWh/year")
    print(f"{'Grid Injection Limit:':<35} {GRID_INJECTION_LIMIT:.0%}")

    print("\n--- V2G (Vehicle-to-Grid) Configuration ---")
    print(f"{'Number of Chargers:':<35} {number_of_chargers}")
    print(f"{'Max Power per Charger:':<35} {max_power_per_charger * 1000:.1f} kW")
    print(f"{'Total V2G Power:':<35} {power_electric_car * 1000:.2f} kW")
    print(f"{'Total V2G Capacity:':<35} {mean_electric_car_capacity * number_of_chargers * 1000:.2f} kWh")

    print("\n--- Technology Specific Parameters ---")
    header = f"{'Technology':<15} | {'CAPEX (€/kW)':<15} | {'OPEX (€/kW/year)':<18} | {'Lifetime (years)':<18} | {'Notes'}"
    separator = "-" * len(header)
    print(header)
    print(separator)

    for tech in technologies:
        row = (
            f"{tech['Name']:<15} | "
            f"{int(tech['CAPEX (€/kW)']):<15,} | "
            f"{int(tech['OPEX (€/kW/year)']):<18,} | "
            f"{str(tech['Lifetime (years)']):<18} | "
            f"{tech['Notes']}"
        )
        print(row)

    print(separator)
    print("\n")

def print_optimisation_result(n):
    """
    Prints a detailed yet compact summary of the optimized energy system in tables.
    Version 3: Details grid purchase and sale costs.
    """
    # ... (toute la section d'extraction et de calcul des données reste identique)
    # Solar
    p_nom_solar = n.generators.p_nom_opt.get('Solar', 0)
    e_prod_solar = n.generators_t.p.get('Solar', pd.Series([0])).sum()
    capex_solar = p_nom_solar * CAPEX_SOLAR_MW / 1e3
    lcoe_solar = (
                p_nom_solar * n.generators.capital_cost.get('Solar', 0) / e_prod_solar / 1e3) if e_prod_solar > 1 else 0

    # Wind
    p_nom_wind = n.generators.p_nom_opt.get('Wind', 0)
    e_prod_wind = n.generators_t.p.get('Wind', pd.Series([0])).sum()
    capex_wind = p_nom_wind * CAPEX_WIND_MW / 1e3
    lcoe_wind = (p_nom_wind * n.generators.capital_cost.get('Wind', 0) / e_prod_wind / 1e3) if e_prod_wind > 1 else 0

    # Biomass
    p_nom_biomass = n.generators.p_nom_opt.get('Biomass ORC', 0)
    e_prod_biomass = n.generators_t.p.get('Biomass ORC', pd.Series([0])).sum()
    capex_biomass = p_nom_biomass * CAPEX_BIOMASS_MW / 1e3
    lcoe_biomass = (p_nom_biomass * n.generators.capital_cost.get('Biomass ORC',
                                                                  0) / e_prod_biomass / 1e3) if e_prod_biomass > 1 else 0

    # Electric Car Battery
    car_battery_name = 'Electric Car Battery'
    p_nom_battery = n.storage_units.p_nom_opt.get(car_battery_name, 0)
    e_nom_battery = n.storage_units.max_hours.get(car_battery_name, 0) * p_nom_battery
    e_dispatch_battery = n.storage_units_t.p_dispatch.get(car_battery_name, pd.Series([0])).sum()
    capex_battery = p_nom_battery * n.storage_units.capital_cost.get(car_battery_name, 0) / 1e3
    lcos_battery = (p_nom_battery * n.storage_units.capital_cost.get(car_battery_name,
                                                                     0) / e_dispatch_battery / 1e3) if e_dispatch_battery > 1 else 0

    # Hydro
    hydro_name = 'Hydro Reservoir'
    p_nom_hydro = n.storage_units.p_nom_opt.get(hydro_name, 0)
    e_nom_hydro = n.storage_units.max_hours.get(hydro_name, 0) * p_nom_hydro
    e_dispatch_hydro = n.storage_units_t.p_dispatch.get(hydro_name, pd.Series([0])).sum()
    inflow_hydro = n.storage_units_t.inflow[hydro_name].sum()
    capex_hydro = p_nom_hydro * CAPEX_HYDRO_MW / 1e3
    lcos_hydro = (p_nom_hydro * n.storage_units.capital_cost.get(hydro_name,
                                                                 0) / e_dispatch_hydro / 1e3) if e_dispatch_hydro > 1 else 0

    # Grid Exchange
    demand_mwh = n.loads_t.p_set['Consumption'].sum()
    achat_mwh = -n.links_t.p1["Grid Import"].sum()
    vente_mwh = n.links_t.p0["Grid Export"].sum()
    cout_achat_k_eur = (-n.links_t.p1['Grid Import'] * n.links_t.marginal_cost['Grid Import']).sum() / 1e3
    revenu_vente_k_eur = (n.links_t.p0['Grid Export'] * n.links_t.marginal_cost['Grid Export']).sum() / 1e3

    # Financial Summary
    total_cost_k_eur = n.objective / 1e3
    benchmark_cost_k_eur = (n.links_t.marginal_cost['Grid Import'] * n.loads_t.p_set['Consumption']).sum() / 1e3
    total_investment_k_eur = capex_solar + capex_wind + capex_hydro + capex_biomass
    net_grid_cost_k_eur = abs(cout_achat_k_eur) - abs(revenu_vente_k_eur)

    # --- Printing Section (Version 4) ---
    print("\n" + "=" * 80)
    print("                OPTIMAL SYNTHESIS OF THE ENERGY SYSTEM")
    print("=" * 80)

    # Production Technologies Table
    print("\n--- Production Technologies ---")
    print(
        f"{'Technology':<18} | {'Installed Power':>16} | {'Total Investment':>18} | {'Annual Energy':>15} | {'Cost (LCOE)':>14}")
    print("-" * 80)
    print(
        f"{'Solar':<18} | {p_nom_solar:>12.2f} MW | {capex_solar:>14.2f} k€ | {e_prod_solar:>11.2f} MWh | {lcoe_solar:>9.4f} €/kWh")
    print(
        f"{'Wind':<18} | {p_nom_wind:>12.2f} MW | {capex_wind:>14.2f} k€ | {e_prod_wind:>11.2f} MWh | {lcoe_wind:>9.4f} €/kWh")
    print(
        f"{'Biomass ORC':<18} | {p_nom_biomass:>12.2f} MW | {capex_biomass:>14.2f} k€ | {e_prod_biomass:>11.2f} MWh | {lcoe_biomass:>9.4f} €/kWh")

    # Storage Technologies Table
    print("\n--- Storage Technologies ---")
    print(
        f"{'Technology':<18} | {'Installed Power':>16} | {'Storage Capacity':>18} | {'Annual Dispatch':>15} | {'Cost (LCOS)':>14}")
    print("-" * 80)
    print(
        f"{'Electric Car':<18} | {p_nom_battery:>12.2f} MW | {e_nom_battery:>14.2f} MWh | {e_dispatch_battery:>11.2f} MWh | {lcos_battery:>9.4f} €/kWh")
    print(
        f"{'Hydro':<18} | {p_nom_hydro:>12.2f} MW | {e_nom_hydro:>14.2f} MWh | {e_dispatch_hydro:>11.2f} MWh | {lcos_hydro:>9.4f} €/kWh")

    # System and Grid Summary Table
    print("\n--- System and Grid Operations ---")
    print(f"{'Metric':<35} | {'Value'}")
    print("-" * 55)
    print(f"{'Total Annual Consumption':<35} | {demand_mwh:>10.2f} MWh/year")
    print(f"{'Grid Energy Purchased':<35} | {achat_mwh:>10.2f} MWh/year")
    print(f"{'Total Purchase Cost':<35} | {cout_achat_k_eur:>10.2f} k€/year")
    print(f"{'Grid Energy Sold':<35} | {vente_mwh:>10.2f} MWh/year")
    print(f"{'Total Sales Revenue':<35} | {-abs(revenu_vente_k_eur):>10.2f} k€/year")
    print(f"{'Net Grid Cost (Purchase-Sale)':<35} | {net_grid_cost_k_eur:>10.2f} k€/year")

    # MODIFIED SECTION: Final Financial Summary
    print("\n--- Global Financial Summary ---")
    print(f"{'Metric':<35} | {'Value'}")
    print("-" * 55)
    print(f"{'Total Investment (S+W+H+B)':<35} | {total_investment_k_eur:>10.2f} k€")
    print(f"{'Benchmark Cost (Grid Only)':<35} | {benchmark_cost_k_eur:>10.2f} k€/year")
    print(f"{'Total Annualized Cost (Hybrid)':<35} | {total_cost_k_eur:>10.2f} k€/year\n")
