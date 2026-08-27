import pandas as pd
import numpy as np


ls_CO2b_p1 = [
    "EMI-FOR-NET",
    "EMI-GLB-GAIN",
    "EMI-GLB-LOSS",
    "EMI-GDW-NET",
    "EMI-GLI-NET",
    "EMI-GSO-NET",
    "EMI-WLB-GAIN",
    "EMI-WLB-LOSS",
    "EMI-WDW-NET",
    "EMI-WLI-NET",
    "EMI-WSO-NET",
    "EMI-FOR-DRAIN-CO2",
    "EMI-WET-DRAIN-CO2",
    "EMI-GRA-DRAIN-CO2",
    "EMI_HWP_C",
    "EMI-CLB-GAIN",
    "EMI-CLB-LOSS",
    "EMI-CSO-NET"
]

year2017 = 11675412.48

HWP_MUL = 44
HWP_DIV = 12000
N2O_MUL = 265
CH4_MUL = 28
MIN_YEAR = 2018
COMPONENT_ORDER = ['CO2', 'CH4', 'N2O', 'HFC', 'PFC', 'SF6', 'CO2B', 'CH4B']

def read_veda_vd(filepath):
    columns = None
    data_start_line = 0

    with open(filepath, "r", encoding="latin-1") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        # Only take real Dimensions line
        if line.startswith("*") and "Dimensions-" in line and "ParentDimensions" not in line:
            columns = line.split("Dimensions-")[1].strip().split(";")

        # Detect data start
        if line.startswith('"'):
            data_start_line = i
            break

    if columns is None:
        raise ValueError("Could not find correct Dimensions line.")


    df = pd.read_csv(
        filepath,
        skiprows=data_start_line,
        names=columns,
        sep=",",
        quotechar='"',
        encoding="latin-1",
        low_memory=False
    )

    return df

def update_data_CO2b(filename):
  df = read_veda_vd(filename)
  df = df.rename(columns={"Period": "Year"}) # Added this line
  df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
  df['Year'] = df['Year'].astype('Int64')
  df_HWP_Sto = df[(df['Attribute']=='VAR_Act') & ((df['Process'] == 'HWP_CO2storage'))]
  
  df_HWP_Sto = df_HWP_Sto.sort_values(by='Year').copy()

  # Get the 'PV' values as a list, including year2017 at the beginning
  pv_values = [year2017] + df_HWP_Sto['PV'].tolist()

  # Calculate the difference between current and previous year
  df_HWP_Sto['PV_diff'] = [(pv_values[i] - pv_values[i-1]) for i in range(1, len(pv_values))]
  df_HWP_Sto["PV_diff"] *=HWP_MUL
  df_HWP_Sto["PV_diff"] /= HWP_DIV
  df_HWP_Sto['PV_diff'] *=(-1)

  return df_HWP_Sto[['Year','PV_diff']]


def data_preparation(df):
    df = df[(df['Attribute']=='VAR_FOut')]
    mask_CH4 = (df["Commodity"].str.contains("EMI-GRA-DRAIN-CH4", na=False)|
                df["Commodity"].str.contains("EMI-WET-DRAIN-CH4", na=False)|
                df["Commodity"].str.contains("EMI-FOR-DRAIN-CH4", na=False)|
                df["Commodity"].str.contains("AGRLIVCH4", na=False))
    df.loc[mask_CH4,'PV'] *= CH4_MUL
    df.loc[df["Commodity"].str.contains("N2O", na=False),'PV'] *= N2O_MUL
    df = df.rename(columns={"Period": "Year"})
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64') # Ensure Year is numeric
    df.loc[(df["Commodity"] == "EMI_HWP_C"),'PV'] *= HWP_MUL
    df.loc[(df["Commodity"] == "EMI_HWP_C"),'PV'] /= HWP_DIV
    return df


def defined_mask(df):

    mask_CO2 = (df["Commodity"].str.contains("AGRCO2N", na=False) |
                df["Commodity"].str.contains("INDCO2N", na=False) |
                df["Commodity"].str.contains("INDCO2P", na=False)|
                df["Commodity"].str.contains("PWRCO2N", na=False)|
                df["Commodity"].str.contains("RSDCO2", na=False)|
                df["Commodity"].str.contains("SRVCO2N", na=False)|
                df["Commodity"].str.contains("TRACO2N", na=False)|
                df["Commodity"].str.contains("SUPCO2N", na=False)
                )

    mask_CH4 = (df["Commodity"].str.contains("EMI-GRA-DRAIN-CH4", na=False)|
                df["Commodity"].str.contains("EMI-WET-DRAIN-CH4", na=False)|
                df["Commodity"].str.contains("EMI-FOR-DRAIN-CH4", na=False)|
                df["Commodity"].str.contains("AGRLIVCH4", na=False)

            )

    mask_N2O = (df["Commodity"].str.contains("N2O", na=False)
    )

    mask_CO2b = (
        (df["Commodity"].isin(ls_CO2b_p1))
            
    )

    mask = [("CO2", mask_CO2), ("CH4", mask_CH4), ("N2O", mask_N2O), ("CO2B", mask_CO2b)]
    return mask


def extract_data(scenarios):
    df_out  = pd.DataFrame()
    for scenario_name, filename in scenarios:
        df_original = read_veda_vd(filename) # Read original data once
        df = df_original.copy() # Work on a copy for processing
       
        df_processed = data_preparation(df_original.copy()) # Process a copy for other masks
        df_processed = df_processed[df_processed['Year'] >= MIN_YEAR] # Filter for years >= MIN_YEAR
        mask = defined_mask(df_processed)
        for mask_name, mask_value in mask:
            df_filtered  = df_processed[mask_value]
            df_out[mask_name + "-" + scenario_name] = df_filtered.groupby('Year')['PV'].sum()

        # Get the HWP_CO2storage PV_diff data separately and add it to CO2b
        co2b_hwp_data = update_data_CO2b(filename) # Call update_data_CO2b with filename
        co2b_hwp_data = co2b_hwp_data.set_index('Year') # Set 'Year' as index for alignment

        # Ensure 'CO2b' column exists before adding, or use .add with fill_value
        if 'CO2B'+"-"+scenario_name not in df_out.columns:
            df_out['CO2B'+"-"+scenario_name] = pd.Series(dtype='float64') # Initialize if not present
        df_out['CO2B'+"-"+scenario_name] = df_out['CO2B'+"-"+scenario_name].add(co2b_hwp_data['PV_diff'], fill_value=0)
        df_out['HFC'+"-"+scenario_name] = 0
        df_out['PFC'+"-"+scenario_name] = 0
        df_out['SF6'+"-"+scenario_name] = 0
        df_out['CH4B'+'-'+ scenario_name] = df_out['CH4'+ '-' + scenario_name]
    return df_out


def fill_missing_years_constant(df):
    # Reset index to make 'Year' a column for easier manipulation
    df_temp = df.reset_index()

    # Convert 'Year' column to numeric
    df_temp['Year'] = pd.to_numeric(df_temp['Year'])

    # Get the min and max year from the data
    min_year = df_temp['Year'].min()
    max_year = df_temp['Year'].max()

    # Create a full range of years
    all_years = pd.DataFrame({'Year': range(min_year, max_year + 1)})

    # Merge the full year range with the original data
    # This will introduce NaNs for years not present in the original df
    df_filled = pd.merge(all_years, df_temp, on='Year', how='left')

    # Set 'Year' as the index and then forward fill the missing values
    df_filled = df_filled.set_index('Year').ffill()

    return df_filled



def exchange_data(scenario_info, IRL_scenarios_file):
    
    df_out = extract_data(scenario_info)

    # Get unique scenario names from existing columns
    # Example: 'CO2-BAU' -> 'BAU'
    scenarios = sorted(list(set([col.split('-')[1] for col in df_out.columns])))

    component_order = COMPONENT_ORDER

    # Create the new ordered list of columns
    new_columns_order = []
    for scenario in scenarios:
        for component in component_order:
            col_name = f"{component}-{scenario}"
            # Only add if the column actually exists in df_out
            if col_name in df_out.columns:
                new_columns_order.append(col_name)

    # Reindex the DataFrame with the new column order
    df_out = df_out[new_columns_order]

    df_constant_filled = fill_missing_years_constant(df_out)
    
     # Only transfer TIM-LEAF scenario data from 2020 onwards
    df_constant_filled = df_constant_filled[
    df_constant_filled.index >= 2020
    ]
    df_initial = pd.read_csv('data/IRL_histWheatley2021_1750-2019.csv')
    
    # Set 'Year' as index for df_initial for easy alignment with df_constant_filled
    df_initial = df_initial.set_index('Year')
    
    # Update df_initial with TIM-LEAF scenario values from 2020 onwards.
    # Historical values in df_initial are retained for years before 2020.
     # The .update() method aligns on Year and column names and replaces
    # the corresponding values with the processed TIM-LEAF scenario data.
    df_initial.update(df_constant_filled)
    

    # # Reset 'Year' back to a column if it was originally a column in df_initial
    # df_initial = df_initial.reset_index()
    year_2070_values = df_initial.loc[2070]

    # Identify years after 2070
    years_after_2070_mask = df_initial.index > 2070

    # Apply the 2070 values to all columns for years after 2070
    # Iterate through columns to assign values, excluding the 'Year' index itself
    for col in df_initial.columns:
        if col != 'Year': # Ensure we don't try to assign to the Year index if it were a column
            df_initial.loc[years_after_2070_mask, col] = year_2070_values[col]
    
    df_initial.to_csv(IRL_scenarios_file)
    return df_initial

