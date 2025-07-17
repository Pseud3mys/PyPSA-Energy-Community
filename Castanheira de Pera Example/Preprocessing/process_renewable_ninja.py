# scripts/process_renewables.py

import pandas as pd
import os
import sys

def process_renewable_data():
    """
    Loads raw wind and solar capacity factor data from Renewables.ninja files,
    cleans and combines them into a single dataframe, and saves it as a
    processed CSV file.
    """
    # Define file paths
    # Assumes raw data is in a sibling 'raw_data' directory
    raw_wind_path = os.path.join('raw_data', 'ninja_wind_40.0047_-8.2091_corrected.csv')
    raw_solar_path = os.path.join('raw_data', 'ninja_pv_40.0047_-8.2091_corrected.csv')
    processed_path = os.path.join('processed_data', 'processed_renewables.csv')

    print("--- Processing Renewable Energy Data (Wind & Solar) ---")

    # Create the processed_data directory if it doesn't exist
    os.makedirs('processed_data', exist_ok=True)

    # --- Load Wind Data ---
    try:
        # Renewables.ninja files have 3 metadata header lines to skip
        df_wind = pd.read_csv(raw_wind_path, skiprows=3)
        print(f"Successfully loaded raw data from '{raw_wind_path}'.")
        # Rename the 'electricity' column for clarity and consistency
        df_wind.rename(columns={'electricity': 'wind_capacity_factor'}, inplace=True)
        # Convert 'time' column to datetime objects and set it as the index
        df_wind['time'] = pd.to_datetime(df_wind['time'])
        df_wind.set_index('time', inplace=True)
        # Keep only the necessary column
        df_wind = df_wind[['wind_capacity_factor']]

    except FileNotFoundError:
        print(f"ERROR: Raw wind data file not found at '{raw_wind_path}'.", file=sys.stderr)
        sys.exit(1)

    # --- Load Solar Data ---
    try:
        # Skip the 3-line header
        df_solar = pd.read_csv(raw_solar_path, skiprows=3)
        print(f"Successfully loaded raw data from '{raw_solar_path}'.")
        # Rename the 'electricity' column
        df_solar.rename(columns={'electricity': 'solar_capacity_factor'}, inplace=True)
        # Convert 'time' column to datetime objects and set it as the index
        df_solar['time'] = pd.to_datetime(df_solar['time'])
        df_solar.set_index('time', inplace=True)
        # Keep only the necessary column
        df_solar = df_solar[['solar_capacity_factor']]

    except FileNotFoundError:
        print(f"ERROR: Raw solar data file not found at '{raw_solar_path}'.", file=sys.stderr)
        sys.exit(1)

    # --- Combine and Save ---

    # Join the two dataframes. An 'outer' join keeps all data from both files.
    df_renewables = df_wind.join(df_solar, how='outer')

    df_renewables.to_csv(processed_path)
    print(f"\nSuccessfully combined and saved renewable data to '{processed_path}'.")
    print("Preview of processed renewables data:")
    print(df_renewables.head())


if __name__ == '__main__':
    process_renewable_data()