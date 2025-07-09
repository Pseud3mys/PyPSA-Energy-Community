import pandas as pd
import sys
import os

def try_import():
    """
    Loads, validates, and prepares time-series data and grid prices from CSV files.

    Assumes the script is run from the project root directory.

    Returns:
        tuple: A tuple containing:
            - data (pd.DataFrame): The main dataframe with consumption and capacity factors.
            - aligned_prices (pd.Series): The grid prices, aligned to the main dataframe's index.
    """
    # --- Define File Paths (relative to the project root) ---
    # The script is expected to be run from the root, so paths are relative to it.
    time_series_path = os.path.join('data', 'calliope_ready_data.csv')
    grid_price_path = os.path.join('data', 'grid price pt.csv')

    # --- 1. Load Time-Series Data (Consumption & Capacity Factors) ---
    print(f"Loading data from '{time_series_path}'...")
    try:
        data = pd.read_csv(time_series_path, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"\nERROR: The file '{time_series_path}' was not found.", file=sys.stderr)
        print("Please ensure the 'data' directory with the required CSV files exists at the project root.", file=sys.stderr)
        sys.exit(1)

    # --- 2. Validate and Clean Time-Series Data ---
    # Check for and remove any duplicate timestamps in the index.
    if data.index.has_duplicates:
        duplicates_count = data.index.duplicated().sum()
        print(f"Warning: {duplicates_count} duplicate timestamp(s) detected in your data file.")
        print("Removing duplicates, keeping the first occurrence...")
        data = data[~data.index.duplicated(keep='first')]
        print("Duplicates removed.")

    # Ensure all required columns are present in the dataframe.
    required_columns = ['wind_capacity_factor', 'solar_capacity_factor', 'consumption_kwh']
    if not all(col in data.columns for col in required_columns):
        print(f"\nERROR: The CSV file must contain the following columns: {required_columns}", file=sys.stderr)
        sys.exit(1)

    # --- 3. Load and Prepare Grid Price Data ---
    print(f"Loading grid prices from '{grid_price_path}'...")
    try:
        # Load the price file, skipping the first 2 metadata rows.
        price_df = pd.read_csv(grid_price_path, sep=';', skiprows=2, decimal='.')

        # Combine 'Data' (Date) and 'Hora' (Hour) into a single datetime column.
        # We subtract 1 from the hour because the source format is 1-24, while pandas expects 0-23.
        price_df['datetime'] = pd.to_datetime(price_df['Data'], dayfirst=True) + pd.to_timedelta(price_df['Hora'] - 1,
                                                                                                 unit='h')
        price_df.set_index('datetime', inplace=True)

        # IMPORTANT: Handle any duplicates in the price file's index.
        if price_df.index.has_duplicates:
            duplicates_count = price_df.index.duplicated().sum()
            print(f"Warning: {duplicates_count} duplicate timestamp(s) detected in the price file.")
            print("Removing duplicates, keeping the first occurrence...")
            price_df = price_df[~price_df.index.duplicated(keep='first')]
            print("Price data duplicates removed.")

        # Keep only the price column and rename it for clarity.
        grid_prices = price_df['Portugal'].rename('grid_price_eur_per_mwh')

        # --- 4. Align Price Data with Main Data ---
        # Align the price index with the main data index, filling any missing values.
        aligned_prices = grid_prices.reindex(data.index, method='ffill').fillna(method='bfill')
        print("Grid prices loaded and aligned successfully.")

    except FileNotFoundError:
        print(f"\nERROR: The file '{grid_price_path}' was not found.", file=sys.stderr)
        print("Please ensure the 'data' directory with the required CSV files exists at the project root.", file=sys.stderr)
        sys.exit(1)

    return data, aligned_prices
