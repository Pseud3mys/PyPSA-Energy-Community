import pypsa
import sys
import pandas as pd
from utils.model_ploting import *
from utils.data_loader import load_model_data
from utils.model_param import *

# =============================================================================
# --- 1. Data Loading and Preparation ---
# =============================================================================
# Load consumption, renewable profiles, and electricity prices
data = load_model_data()

# Define the annual energy demand in mWh
data['consumption_mwh'] = (data['consumption_kwh'] / 1000)
# autoscale the consumption to the annual demand
auto_factor = ANNUAL_ENERGY_DEMAND / data['consumption_mwh'].sum()
data['consumption_mwh'] = auto_factor * data['consumption_mwh']

#some debug and Info.
print("\n\nAnnual Energy Demand in Castanheira de Pera (MWh):", round(data['consumption_kwh'].sum()/1000,2))
print("Scaled Annual Energy Demand (MWh):", round(data['consumption_mwh'].sum(),2))
print("Scaling factor applied to consumption (%):", round(auto_factor*100, 2))
print("\n\n")

print_parameters_summary()


# multiply wind power capacity factor (good zone)
WIND_CAPACITY_FACTOR = 0.97  # moyenne à 30%
data['wind_capacity_factor'] = WIND_CAPACITY_FACTOR*data['wind_capacity_factor']

# =============================================================================
# --- 2. PyPSA Network Setup ---
# =============================================================================
print("Building the PyPSA network...")
n = pypsa.Network()
n.set_snapshots(data.index)

# Add the local electrical bus (node)
n.add("Bus", "Castanheira de Pera")

# Add the load (consumption) to the bus
n.add("Load", "Consumption",
      bus="Castanheira de Pera",
      p_set=data['consumption_mwh'])

# =============================================================================
# --- 3. Adding System Components (Generators, Storage, Grid) ---
# =============================================================================

## ------------------ Renewable Generation ------------------
# Wind (capacity to be optimized)
n.add("Generator", "Wind",
      bus="Castanheira de Pera",
      p_nom_extendable=True,
      capital_cost=capital_cost_wind,
      marginal_cost=0,
      p_max_pu=data['wind_capacity_factor'])

# Solar (capacity to be optimized)
n.add("Generator", "Solar",
      bus="Castanheira de Pera",
      p_nom_extendable=True,
      capital_cost=capital_cost_solar,
      marginal_cost=0,
      p_max_pu=data['solar_capacity_factor'])

# Biomass ORC (capacity to be optimized)
# produce 4 time more heat than electricity...
# this model assume we sell the heat as a by-product to take it into account.
# Assume we sell heat (natural gas price) at 55% the price of the electricity
# Assume also 80% efficiency for the ORC heat system. (heat distribution efficiency)
# 0.8 * 4 * 0.6 = 1.92
n.add("Generator", "Biomass ORC",
      bus="Castanheira de Pera",
      p_nom_extendable=True,
      capital_cost=capital_cost_ORC_Biomass,
      marginal_cost=- 4 * 0.55 * data["grid_price_eur_per_mwh"]) # Negative cost can represent revenue from by-products like heat

## ------------------ Storage Units ------------------
# Hydro Reservoir (modeled as a StorageUnit)
n.add("StorageUnit", "Hydro Reservoir",
      bus="Castanheira de Pera",
      p_nom=30 / 1000,                # 30kW if fixed power capacity
      p_nom_extendable=not IS_HYDRO_FIXED, # Capacity is fixed if IS_HYDRO_FIXED is True
      capital_cost=capital_cost_hydro,
      marginal_cost=0,                # Assumed low operational cost
      p_min_pu=-PUMPING_HYDRO,                     # 0 = Cannot consume power (no pumping)
      inflow=data['hydro_inflow_kwh'] / 1000, # Natural recharge from river/rain
      max_hours=RESERVOIR_CAPACITY_HYDRO, # Reservoir size in hours at full power
      cyclic_state_of_charge=True)    # Ensure reservoir level is same at year end

# Electric Car Battery (Vehicle-to-Grid)
n.add("StorageUnit", "Electric Car Battery",
      bus="Castanheira de Pera",
      p_nom=power_electric_car,       # Total power of the chargers
      p_nom_extendable=False,         # Not optimized, considered as existing infrastructure
      capital_cost=0,                 # Assumed to be already installed
      marginal_cost=0,                # Negligible operating cost
      max_hours=battery_capacity_electric_car_hours) # Storage capacity in hours at p_nom


## ------------------ Grid Connection ------------------
# Create a bus to represent the external grid (infinite source/sink)
n.add("Bus", "Grid")

# Link for PURCHASING (Importing) electricity
# Flow from "Grid" to "Castanheira de Pera"
n.add("Link", "Grid Import",
      bus0="Grid",
      bus1="Castanheira de Pera",
      p_nom=1e9,  # Infinite import capacity
      p_min_pu=0,
      marginal_cost=data['grid_price_eur_per_mwh'])  # Purchase price in €/MWh

# Link for SELLING (Exporting) electricity
# Flow from "Castanheira de Pera" to "Grid"
n.add("Link", "Grid Export",
      bus0="Castanheira de Pera",
      bus1="Grid",
      p_nom=GRID_INJECTION_LIMIT * max(data['consumption_mwh']),
      p_min_pu=0,
      marginal_cost=-0.9 * data['grid_price_eur_per_mwh']) # Negative cost represents revenue

# Add a "slack" generator to the grid bus to balance the whole system
n.add("Generator",
      "Grid Slack Source",
      bus="Grid",
      control='Slack',
      p_nom=1e9,   # Infinite capacity
      p_min_pu=-1, # Can both generate and consume energy
      marginal_cost=0)

# =============================================================================
# --- 4. Model Creation and Adding Cost Constraint ---
# =============================================================================
print("Creating the Linopy optimization model...")
m = n.optimize.create_model()

# --- Add a global CAPEX budget constraint for all new investments ---
print(f"Adding the global CAPEX budget constraint: {CAPEX_BUDGET:,.0f} €")

# 1. Initialize the left-hand side (LHS) of the constraint expression.
total_capex_lhs = 0

# 2. Add the investment costs of extendable generators (Solar, Wind, Biomass).
gen_p_nom_vars = m.variables['Generator-p_nom']
total_capex_lhs += gen_p_nom_vars.loc['Wind'] * CAPEX_WIND_MW
total_capex_lhs += gen_p_nom_vars.loc['Solar'] * CAPEX_SOLAR_MW
total_capex_lhs += gen_p_nom_vars.loc['Biomass ORC'] * CAPEX_BIOMASS_MW

# 3. Add the hydro investment cost.
if not IS_HYDRO_FIXED and 'StorageUnit-p_nom' in m.variables:
    # CASE 1: Hydro capacity is optimized (p_nom_extendable=True).
    su_p_nom_vars = m.variables['StorageUnit-p_nom']
    variable_hydro_cost = su_p_nom_vars.loc['Hydro Reservoir'] * CAPEX_HYDRO_MW
    total_capex_lhs += variable_hydro_cost
else:
    # CASE 2: Hydro capacity is FIXED. Its cost is a constant.
    hydro_capacity_mw = n.storage_units.at['Hydro Reservoir', 'p_nom']
    fixed_hydro_cost = hydro_capacity_mw * CAPEX_HYDRO_MW
    total_capex_lhs += fixed_hydro_cost

# 4. Add the final global budget constraint to the model.
m.add_constraints(total_capex_lhs, "<=", CAPEX_BUDGET, name="Global_CAPEX_budget_limit")

# =============================================================================
# --- 5. Running the Optimization ---
# =============================================================================
print("Running the optimization with the budget constraint...")
status, condition = n.optimize.solve_model(solver_name="highs")

print(f"\nOptimization Status: {status}, Condition: {condition}")
if status != 'ok':
    print("Optimization failed. Please check the model and data.", file=sys.stderr)
else:
    print("Optimization successful.")

# =============================================================================
# --- 6. Results and Visualization ---
# =============================================================================
    # Display a summary of the optimal system configuration
    print("\n\n")
    print_optimisation_result(n)
    print("\n\n")


    # Plot for a week in Winter
    start_date_winter = pd.Timestamp('2019-03-11')
    end_date_winter = pd.Timestamp('2019-03-23')
    plot_energy_balance(n, start_date_winter, end_date_winter, plot_market_price=False)
    #plot_storage_operation(n, "Hydro Reservoir", start_date_winter, end_date_winter)
    #plot_storage_operation(n, "Electric Car Battery", start_date_winter, end_date_winter)

    # Plot for a week in Summer
    start_date_summer = pd.Timestamp('2019-06-01')
    end_date_summer = pd.Timestamp('2019-06-14')
    #plot_energy_balance(n, start_date_summer, end_date_summer, plot_market_price=False)
    #plot_storage_operation(n, "Hydro Reservoir", start_date_summer, end_date_summer)
