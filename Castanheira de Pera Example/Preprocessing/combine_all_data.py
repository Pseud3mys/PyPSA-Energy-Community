# scripts/combine_inputs.py

import pandas as pd
import os
import sys


def combine_processed_data():
    """
    Loads all individual processed timeseries data (renewables, consumption, hydro, price),
    normalizes their timestamps to a single representative year, combines them into a single
    DataFrame, cleans it (handles missing values), and saves the final model-ready CSV.
    """
    print("--- Combining All Processed Data Sources ---")

    # The non-leap year to use for the final time series
    REPRESENTATIVE_YEAR = 2019

    # Define paths to the processed data files
    processed_dir = 'processed_data'
    paths = {
        'renewables': os.path.join(processed_dir, 'processed_renewables.csv'),
        'consumption': os.path.join(processed_dir, 'processed_consumption.csv'),
        'hydro': os.path.join(processed_dir, 'processed_hydro.csv'),
        'price': os.path.join(processed_dir, 'processed_grid_price.csv')
    }

    # --- Load All Processed Files ---
    dataframes = {}
    for name, path in paths.items():
        try:
            # Load the data, using the first column as the datetime index
            dataframes[name] = pd.read_csv(path, index_col=0, parse_dates=True)
            print(f"Successfully loaded '{path}'.")
        except FileNotFoundError:
            print(f"ERROR: Processed file not found at '{path}'.", file=sys.stderr)
            print(f"Please run the corresponding processing script for '{name}' first.", file=sys.stderr)
            sys.exit(1)

    # --- Normalize Timestamps to Representative Year ---
    print(f"\nNormalizing all data to the representative year {REPRESENTATIVE_YEAR}...")
    for name, df in dataframes.items():
        # This mapping replaces the year of each timestamp with the representative year
        df.index = df.index.map(lambda t: t.replace(year=REPRESENTATIVE_YEAR))
        # Handle potential duplicates created by normalization (e.g., from leap years)
        df = df[~df.index.duplicated(keep='first')]
        dataframes[name] = df

    # --- Combine into a Single DataFrame ---
    # `pd.concat` with axis=1 merges dataframes side-by-side based on their index
    combined_df = pd.concat(dataframes.values(), axis=1)

    # --- Clean the Final DataFrame ---

    # 1. Create a full, continuous hourly index for the entire year
    # This ensures the final dataframe has exactly 8760 hours without gaps.
    full_index = pd.date_range(
        start=f'{REPRESENTATIVE_YEAR}-01-01 00:00:00',
        end=f'{REPRESENTATIVE_YEAR}-12-31 23:00:00',
        freq='h'
    )
    combined_df = combined_df.reindex(full_index)

    print("\nChecking for missing values BEFORE cleaning:")
    print(combined_df.isnull().sum())

    # 2. Interpolate missing values
    # 'time' method is good for timeseries. Then ffill/bfill for any remaining NaNs.
    combined_df.interpolate(method='time', inplace=True)
    combined_df.ffill(inplace=True)  # Fill any remaining at the start
    combined_df.bfill(inplace=True)  # Fill any remaining at the end

    print("\nChecking for missing values AFTER cleaning:")
    print(combined_df.isnull().sum())

    # --- Save Final Model-Ready Data ---
    output_path = 'model_timeseries.csv'
    combined_df.index.name = 'timestamp'  # Set the name for the index column
    combined_df.to_csv(output_path)

    print(f"\nSUCCESS: Final combined data saved to '{output_path}'.")


if __name__ == '__main__':
    combine_processed_data()
