# scripts/process_consumption.py

import pandas as pd
import os
import sys

def process_consumption_data():
    """
    Loads raw hourly consumption data, cleans it, fills a known gap in the month
    of October by replicating September's data, and saves it as a processed CSV file.
    """
    # Define file paths
    raw_path = os.path.join('raw_data', 'consumos_horario_codigo_postal.csv')
    processed_path = os.path.join('processed_data', 'processed_consumption.csv')

    print("--- Processing Consumption Data ---")

    # Create the processed_data directory if it doesn't exist
    os.makedirs('processed_data', exist_ok=True)

    try:
        # The raw data file uses a semicolon as a separator
        df_consumption = pd.read_csv(raw_path, sep=';')
        print(f"Successfully loaded raw data from '{raw_path}'.")

    except FileNotFoundError:
        print(f"ERROR: Raw consumption data file not found at '{raw_path}'.", file=sys.stderr)
        sys.exit(1)

    # --- Data Cleaning and Formatting ---

    # 1. Convert 'Date/Time' column to datetime objects.
    # Reading as UTC and then removing timezone is a safe way to standardize.
    df_consumption['timestamp'] = pd.to_datetime(df_consumption['Date/Time'], utc=True)
    df_consumption.set_index('timestamp', inplace=True)
    df_consumption.index = df_consumption.index.tz_localize(None) # Remove timezone info

    # 2. Select and rename the required column to a standard name
    df_consumption = df_consumption[['Active Energy (kWh)']]
    df_consumption.rename(columns={'Active Energy (kWh)': 'consumption_kwh'}, inplace=True)

    # 3. Fill the missing October data by replicating September's data.
    # This is a specific cleaning step required for this particular dataset.
    if 10 not in df_consumption.index.month:
        print("October data is missing. Replicating from September...")
        # Create a copy of September's data
        df_october = df_consumption[df_consumption.index.month == 9].copy()
        # Remap the index of the copied data to October
        df_october.index = df_october.index.map(lambda t: t.replace(month=10))
        # Concatenate the original data with the new October data
        df_complete = pd.concat([df_consumption, df_october])
        print("October data filled successfully.")
    else:
        df_complete = df_consumption

    # 4. Sort the index to ensure the data is in chronological order.
    df_complete.sort_index(inplace=True)

    # --- Save Processed Data ---
    df_complete.to_csv(processed_path)
    print(f"\nSuccessfully processed and saved consumption data to '{processed_path}'.")
    print("Preview of processed consumption data:")
    print(df_complete.head())


if __name__ == '__main__':
    process_consumption_data()