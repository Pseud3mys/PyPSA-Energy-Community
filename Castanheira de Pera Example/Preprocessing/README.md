
# Data Preprocessing Module for the Optimization Model

This document describes the data preprocessing pipeline, designed to transform various raw data sources into a single, clean, and standardized time-series file ready for the energy optimization model.

## 1. Module Objective

The main goal is to produce a single CSV file, `model_timeseries.csv`, which contains all the necessary hourly data for the model. This pipeline ensures data consistency, cleanliness, and correct formatting, regardless of the original data sources.

## 2. File Structure

The preprocessing module is organized with a clear folder structure to separate raw data, processed data, and the scripts themselves.

```
Preprocessing/
├── 📂 raw_data/
│   ├── consumos_horario_codigo_postal.csv
│   ├── grid_price_portugal.csv
│   ├── HydroCastanheiraIST.csv
│   ├── ninja_pv_40.0047_-8.2091_corrected.csv
│   └── ninja_wind_40.0047_-8.2091_corrected.csv
├── process_consumption.py
├── process_grid_price.py
├── process_hydro.py
├── process_renewables.py
│
├── combine_inputs.py
├── plot_final_data.py
│
├── model_timeseries.csv (created by combine_inouts.py)
│
└── 📂 processed_data/
    └── (This directory is created automatically by the 'process_...py' scripts)


```

-   **`Preprocessing/raw_data/`**: Place **all raw data files** downloaded from their respective sources here.
    
-   **`Preprocessing/`**: Contains all the scripts for processing and combining the data.
    
-   **`Preprocessing/processed_data/`**: This directory is created automatically and holds the intermediate data files after each source has been cleaned.
    

The final output, `model_timeseries.csv`, will be generated and must be moved in the project's root directory, in the `PyPSA/data/` folder.

## 3. The Final Data File: `model_timeseries.csv`

This is the one and only file that the main optimization model (`optimiser_main.py`) will use. It must contain a complete hourly time-series for one year (8760 hours).

![image](data structure.png "Title")

**Note**: The column name for hydropower has been standardized to `hydro_inflow_kwh` to reflect that it represents an **incoming energy resource** (the energy contained in the hourly water volume), not a final power output.

## 4. Workflow

There are two ways to use this module: the automated process (recommended) or manual creation.

### Workflow 1: Automated Process (Recommended)

Follow these steps to generate the `model_timeseries.csv` file from the raw data. **Run all commands from the project's root directory.**

**Step 1: Prepare Raw Data**

-   Ensure all your source data files are placed inside the `Preprocessing/raw_data/` folder.
    

**Step 2: Run Individual Processing Scripts**

-   Each script reads a file from `raw_data/`, cleans it, and saves a clean `.csv` file to `Preprocessing/processed_data/`.
    

```
python Preprocessing/scripts/process_consumption.py
python Preprocessing/scripts/process_grid_price.py
python Preprocessing/scripts/process_hydro.py
python Preprocessing/scripts/process_renewables.py

```

**Step 3: Combine Processed Data**

-   This script reads all the files from `processed_data/`, merges them, and creates the final `model_timeseries.csv` file in the project's root directory.
    

```
python Preprocessing/scripts/combine_inputs.py

```

**Step 4 (Optional but Recommended): Verify Data**

-   This script generates plots of all time-series from the final file for visual inspection.
    

```
python Preprocessing/scripts/plot_final_data.py

```

At the end of this process, the `model_timeseries.csv` file is ready to be used by the main model.

### Workflow 2: Manual Creation

If you prefer not to use the processing scripts, you can create the `model_timeseries.csv` file manually (e.g., with Excel or Google Sheets).

To do this, you must **strictly follow the specifications** defined in Section 3:

1.  The file must be named `model_timeseries.csv`.
    
2.  It must be placed in the project's root directory.
    
3.  It must contain the exact required columns with the specified names and units.
    
4.  The `timestamp` column must be in `YYYY-MM-DD HH:MM:SS` format.
    
5.  The file must not contain any missing values and must cover 8760 hours.
