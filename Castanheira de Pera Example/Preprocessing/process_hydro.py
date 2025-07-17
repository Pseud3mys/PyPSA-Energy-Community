# scripts/process_hydro.py

import pandas as pd
import numpy as np
import os
import sys


# 3. Define turbine performance curve for power calculation
def calculate_power_from_flow(flow_lps):
    """Calculates power (kW) from flow (l/s) using linear interpolation."""
    # Performance curve points (Flow in m³/s vs. Power in kW)
    q_points_m3s = [0, 0.79, 0.97, 1.14, 1.27]
    p_points_kw = [0, 15.0, 23.0, 28.6, 29.8]
    q_min_m3s, q_max_m3s = 0.79, 1.27  # Turbine operating limits

    flow_m3s = flow_lps / 1000.0

    # Power is zero if flow is outside the turbine's operating range
    if not (q_min_m3s <= flow_m3s <= q_max_m3s):
        return 0.0

    return np.interp(flow_m3s, q_points_m3s, p_points_kw)

def process_hydro_data():
    """
    Loads raw hydrographic flow data, selects a representative year,
    calculates the corresponding power output in kW based on a predefined
    turbine performance curve, and saves it as a processed CSV file.
    """
    # Define file paths
    raw_path = os.path.join('raw_data', 'HydroCastanheiraIST.csv')
    processed_path = os.path.join('processed_data', 'processed_hydro.csv')

    print("--- Processing Hydro Power Data ---")

    # Create the processed_data directory if it doesn't exist
    os.makedirs('processed_data', exist_ok=True)

    try:
        # Load raw data with semicolon separator and comma as decimal point
        df_hydro = pd.read_csv(raw_path, sep=';', decimal=',')
        print(f"Successfully loaded raw data from '{raw_path}'.")

    except FileNotFoundError:
        print(f"ERROR: Raw data file not found at '{raw_path}'.", file=sys.stderr)
        sys.exit(1)

    # --- Data Cleaning and Calculation ---

    # 1. Convert 'Time' column to datetime objects, coercing errors
    df_hydro['Time'] = pd.to_datetime(df_hydro['Time'], errors='coerce')
    df_hydro.dropna(subset=['Time'], inplace=True)  # Drop rows where conversion failed

    # 2. Select a representative hydrological year (October to September)
    start_date = '1994-10-01'
    end_date = '1995-09-30'
    mask = (df_hydro['Time'] >= start_date) & (df_hydro['Time'] <= end_date)
    df_hydro = df_hydro.loc[mask].copy()
    df_hydro.set_index('Time', inplace=True)

    # 4. Apply the function to create the power column
    df_hydro['hydro_inflow_kwh'] = df_hydro['Q (l/s)'].apply(calculate_power_from_flow)

    # 5. Create final DataFrame with only the required column
    df_final = df_hydro[['hydro_inflow_kwh']]
    df_final.sort_index(inplace=True)

    # --- Save Processed Data ---
    df_final.to_csv(processed_path)
    print(f"Successfully processed and saved data to '{processed_path}'.\n")
    print("Preview of processed hydro data:")
    print(df_final.head())


if __name__ == '__main__':
    process_hydro_data()