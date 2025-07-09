
# Hybrid Renewable Energy System Optimization for Castanheira de Pera

## Project Overview

This project presents a comprehensive modeling and optimization of a hybrid renewable energy system for the community of **Castanheira de Pera, Portugal**. The primary objective is to determine the optimal mix of renewable energy sources—specifically **Solar PV** and **Wind Power**—to complement a pre-existing 30kW hydroelectric turbine. The model aims to meet the local energy demand while minimizing the total cost of the system, considering both capital expenditures (CAPEX) and operational costs.

The optimization is performed using the open-source Python library **PyPSA (Python for Power System Analysis)**. This tool allows for a detailed, time-series-based simulation of the energy system over a full year (2019) with an hourly resolution. The model also explores the potential of integrating a **Biomass Organic Rankine Cycle (ORC) plant** and leveraging **Vehicle-to-Grid (V2G)** technology from local electric vehicles as a form of battery storage.

This work was developed as part of an internship related to the European program [HY4RES](https://hy4res.eu/fr/ "null").

## Key Features

-   **Multi-Technology Optimization**: Determines the optimal installed capacity for Solar PV, Wind, and Biomass ORC generators.
    
-   **Techno-Economic Analysis**: The optimization is based on minimizing the total annualized cost of the system, taking into account the capital costs, lifetimes, and operational costs of each technology.
    
-   **Time-Series Simulation**: Utilizes hourly data for a full year (2019) for electricity demand, solar and wind availability, and grid prices, ensuring a realistic assessment.
    
-   **Hydro and V2G Storage Modeling**: Includes a detailed model for a hydro reservoir with a fixed 30kW turbine and models local electric vehicles as a distributed battery storage system.
    
-   **Grid Interaction**: The system can both purchase electricity from and sell surplus energy back to the Portuguese national grid, with defined limits on grid injection.
    
-   **Data-Driven Approach**: The model is built upon real-world data for energy consumption in Castanheira de Pera, renewable potentials from Renewables.ninja, and Portuguese grid prices.
    
-   **Comprehensive Results & Visualization**: The main script outputs a detailed summary of the optimized system, including costs, capacities, and energy production, along with a suite of plots for in-depth analysis.
    

## Repository Structure

```
.
├── optimiser main.py                # Main script to run the PyPSA optimization
├── utils/
│   ├── data_loader.py               # Module for loading and preparing data
│   ├── model_param.py               # Module containing all system parameters and costs
│   └── model_ploting.py             # Module for generating plots and visualizations
├── data/
│   ├── calliope_ready_data.csv      # Hourly time-series data for 2019 (consumption, wind/solar factors)
│   ├── grid price pt.csv            # Hourly Portuguese grid electricity prices for 2019 (€/MWh)
│   ├── data Castanheira de Pera - Feuille 1 (1).pdf  # Supporting data about the municipality
│   └── Brouillon rapport de stage..pdf # Draft internship report with project context (in French)
└── README.md                        # This file

```

## Installation & Dependencies

To run this project, you need a Python environment with the following libraries installed.

-   **pypsa**: The core library for power system analysis.
    
-   **pandas**: For data manipulation and analysis.
    
-   **matplotlib**: For plotting the results.
    

You can install these dependencies using `pip`:

```
pip install pypsa pandas matplotlib

```

You will also need a solver for the optimization. The `HiGHS` solver is a good open-source option that is easy to install:

```
pip install highspy

```

## How to Run

1.  **Ensure** all files are in the correct **directory structure** as outlined above. The `utils` and `data` folders should be in the same directory as `optimiser main.py`.
    
2.  **Run the main script** from your terminal:
    
    ```
    python "optimiser main.py"
    
    ```
    
3.  The script will:
    
    -   Load and process the data from the CSV files.
        
    -   Build the PyPSA energy network model based on the parameters in `model_param.py`.
        
    -   Run the optimization to find the least-cost system configuration.
        
    -   Print a detailed summary of the optimal system to the console.
        
    -   Generate and display several plots visualizing the results, including energy balance charts and cost breakdowns.
        

## Configuration

All key parameters of the energy system can be adjusted in the `utils/model_param.py` file. This includes:

-   `CAPEX_BUDGET`: The maximum total investment for new assets.
    
-   `ANNUAL_ENERGY_DEMAND`: The target annual energy demand to be met.
    
-   Techno-economic parameters for each technology (e.g., `CAPEX_SOLAR`, `LIFE_WIND`).
    
-   Hydro reservoir and V2G battery settings.
    
-   `GRID_INJECTION_LIMIT`: The maximum power that can be sold to the grid.
    

By modifying these parameters, you can explore different scenarios and constraints for the energy system.
