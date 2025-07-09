import pandas as pd
import sys


def try_import():
    """
    Loads, validates, and prepares time-series data and grid prices from CSV files.

    Returns:
        tuple: A tuple containing:
            - data (pd.DataFrame): The main dataframe with consumption and capacity factors.
            - aligned_prices (pd.Series): The grid prices, aligned to the main dataframe's index.
    """
    # --- 1. Load Time-Series Data (Consumption & Capacity Factors) ---
    print("Loading data from 'calliope_ready_data.csv'...")
    try:
        data = pd.read_csv('calliope_ready_data.csv', index_col=0, parse_dates=True)
    except FileNotFoundError:
        print("\nERROR: The file 'calliope_ready_data.csv' was not found.", file=sys.stderr)
        print("Please ensure the file is in the same directory as the script.", file=sys.stderr)
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
    print("Loading grid prices from 'grid price pt.csv'...")
    try:
        # Load the price file, skipping the first 2 metadata rows.
        price_df = pd.read_csv('grid price pt.csv', sep=';', skiprows=2, decimal='.')

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
        print("\nERROR: The file 'grid price pt.csv' was not found.", file=sys.stderr)
        sys.exit(1)

    return data, aligned_prices