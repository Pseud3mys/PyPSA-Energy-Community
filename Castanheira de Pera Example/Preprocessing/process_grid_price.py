# scripts/process_grid_price.py

import pandas as pd
import os
import sys


def process_price_data():
    """
    Loads raw grid price data for Portugal, cleans it, standardizes the timestamp,
    and saves it as a processed CSV file.
    """
    # Define file paths
    # Assumes raw data is in a sibling 'raw_data' directory
    raw_path = os.path.join('raw_data', 'grid_price_portugal.csv')
    processed_path = os.path.join('processed_data', 'processed_grid_price.csv')

    print("--- Processing Grid Price Data ---")

    # Create the processed_data directory if it doesn't exist
    os.makedirs('processed_data', exist_ok=True)

    try:
        # Load the raw CSV file, skipping the first 2 metadata rows.
        # The separator is a semicolon.
        price_df = pd.read_csv(raw_path, sep=';', skiprows=2)
        print(f"Successfully loaded raw data from '{raw_path}'.")

    except FileNotFoundError:
        print(f"ERROR: Raw data file not found at '{raw_path}'.", file=sys.stderr)
        print("Please ensure the file exists and the path is correct.", file=sys.stderr)
        sys.exit(1)

    # --- Data Cleaning and Formatting ---

    # 1. Create a proper datetime 'timestamp' column.
    # The source 'Hora' (hour) is in 1-24 format. We subtract 1 to convert it to
    # the 0-23 format that pandas' to_timedelta expects.
    # 'dayfirst=True' is crucial for parsing dates like '01/01/2019'.
    price_df['timestamp'] = pd.to_datetime(price_df['Data'], dayfirst=True) + \
                            pd.to_timedelta(price_df['Hora'] - 1, unit='h')

    # 2. Set the new 'timestamp' column as the index.
    price_df.set_index('timestamp', inplace=True)

    # 3. Select and rename the relevant column for clarity.
    price_df = price_df[['Portugal']].rename(columns={'Portugal': 'grid_price_eur_per_mwh'})

    # 4. Ensure the data is sorted by time
    price_df.sort_index(inplace=True)

    # --- Save Processed Data ---
    price_df.to_csv(processed_path)
    print(f"Successfully processed and saved data to '{processed_path}'.\n")
    print("Preview of processed price data:")
    print(price_df.head())


if __name__ == '__main__':
    process_price_data()