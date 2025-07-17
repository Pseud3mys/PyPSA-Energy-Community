# utils/data_loader.py

import pandas as pd
import os
import sys


def load_model_data(file_path='data/model_timeseries.csv'):
    """
    Loads the final, pre-processed timeseries data for the optimization model.

    This function expects a single, clean CSV file that has been generated
    by the data processing pipeline (e.g., combine_inputs.py).

    Args:
        file_path (str): The path to the final model data CSV file,
                         relative to the project root directory.

    Returns:
        pd.DataFrame: A single dataframe containing all necessary timeseries
                      data (consumption, capacity factors, hydro, prices).
    """
    print("--- Loading and Validating Model Input Data ---")

    # --- 1. Load the Single Data File ---
    if not os.path.exists(file_path):
        print(f"\nERROR: The model data file was not found at '{file_path}'.", file=sys.stderr)
        print("Please ensure the directory structure is correct and you have run the processing scripts.",
              file=sys.stderr)
        sys.exit(1)

    # Load the data, assuming the first column is the timestamp index
    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    print(f"Successfully loaded data from '{file_path}'.")

    # --- 2. Validate the Data Content ---

    # a) Check for required columns
    required_columns = [
        'wind_capacity_factor',
        'solar_capacity_factor',
        'consumption_kwh',
        'hydro_inflow_kwh',
        'grid_price_eur_per_mwh'
    ]

    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        print(f"\nERROR: The data file is missing the following required columns: {missing_cols}", file=sys.stderr)
        sys.exit(1)

    # b) Check for null (empty) values
    if data.isnull().sum().any():
        print("\nERROR: The data file contains missing values. Please clean the file before running the model.",
              file=sys.stderr)
        print("Missing values summary:")
        print(data.isnull().sum())
        sys.exit(1)

    # c) Check for duplicate timestamps
    if data.index.has_duplicates:
        print("\nWARNING: Duplicate timestamps detected in the data file. Removing them...", file=sys.stderr)
        data = data[~data.index.duplicated(keep='first')]

    print("Data validation successful: All required columns are present and no missing values found.")

    return data


if __name__ == '__main__':
    # This block allows you to test the script directly and robustly.
    # To make this runnable from anywhere, we construct an absolute path.
    print("--- Running data_loader.py as main script for testing ---")

    # Go in the correct folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    test_file_path = os.path.join(project_root, 'data', 'model_timeseries.csv')

    print(f"Constructed test path: {test_file_path}")

    # Call the function with the absolute path for this test run.
    model_data = load_model_data(file_path=test_file_path)

    print("\n--- Data Loader Test Successful ---")
    print("DataFrame Info:")
    model_data.info()
    print("\nFirst 5 rows of the loaded data:")
    print(model_data.head())