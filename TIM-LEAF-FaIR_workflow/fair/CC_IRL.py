# This is a script to set up and run the fair model v2.1.3 for Ireland based on the NZ CCC script

# This imports the tools that are needed to organise the data
import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
from fair import FAIR
from fair.interface import fill, initialise
from fair.io import read_properties
import fair
from data_transfer_from_TIM import exchange_data
# This sets up fair with the scenarios to be run; first scenario must be "base"
f = FAIR(ch4_method="Thornhill2021")

f.define_time(1750, 2300, 1)  # start, end, step

# base scenarios
base_scenario = "ssp126" # this defines the global background emissions
IRL_scenario = "S3" # BAU, TN, SGLA, SGHA & NZ; the script is run for each of Ireland's emissions scenario individually
IRL_scenarios = [("BAU", 'data/BAU_2506.vd'), ('S1','data/test_s1_uc_2906.vd'), ('S2', 'data/S2_2906.vd'), ('S3', 'data/S3_2906.vd')]
base_year = "2020" # this year defines how 'historical' and 'future' emissions are defined in the output
# need to change the name of this input file and then delete this remark
IRL_scenarios_file = 'data/IRL_scenarios_moriarty_output'+ IRL_scenario +'.csv'

# GWPs (IRL emissions data are in CO2-eq for individual gases, using AR5 GWPs)
GWP_CH4 = 28.
GWP_N2O = 265.
GWP_HFC134a = 1300. # HFCs are given in HFC-134a equivalents
GWP_CF4 = 6630.     # PFCs are given in CF4 equivalents
GWP_SF6 = 23500.

exchange_data(IRL_scenarios, IRL_scenarios_file)
print("Data exchange from TIM complete. Output saved to " + IRL_scenarios_file)

## Define scenarios; the first must be called "base", the others can have any descriptive name
scenarios = ["base",
             "IRLCO2", "IRLN2O", "IRLCH4", "IRLother", "IRLall",
             ("IRLCO2_" + base_year), ("IRLN2O_" + base_year),
             ("IRLCH4_" + base_year), ("IRLother_" + base_year),
             ("IRLall_" + base_year)]
f.define_scenarios(scenarios)

# set up configs and allocate memory (copied from fair documentation),
# using the most recent calibration set that excludes solar_trend and contrails
# which have been set to zero in the calibration file to use the existing wrapper.
df_configs = pd.read_csv('data/calibrated_constrained_parameters-v1.4.2.csv', index_col=0)
configs = df_configs.index
f.define_configs(configs)

species, properties = read_properties(filename='data/species_configs_properties_calibration1.2.0.csv')
f.define_species(species, properties)

f.allocate()

## Fill all scenarios with same "base" emissions (from rcmip)
# this is an addition to fair source code
# it is based on f.fill_from_rcmp, but fills all scenarios with the same "base_scenario" emissions
print(fair.__version__)
print(hasattr(f, "fill_scenarios_from_rcmip"))
f.fill_scenarios_from_rcmip(base_scenario)

## Set up forcings and configs for AR6 calibrated run
# copied from fair documentation and chrisroadmap files on GitHub
df_emis = pd.read_csv('data/rcmip-emissions-annual-means-v5-1-0.csv')
gfed_sectors = [
    "Emissions|NOx|MAGICC AFOLU|Agricultural Waste Burning",
    "Emissions|NOx|MAGICC AFOLU|Forest Burning",
    "Emissions|NOx|MAGICC AFOLU|Grassland Burning",
    "Emissions|NOx|MAGICC AFOLU|Peat Burning",
]
for scenario in scenarios:
    f.emissions.loc[dict(specie="NOx", scenario=scenario)] = (
        df_emis.loc[
            (df_emis["Scenario"] == base_scenario)
            & (df_emis["Region"] == "World")
            & (df_emis["Variable"].isin(gfed_sectors)),
            "1750":"2300",
        ]
        .interpolate(axis=1)
        .values.squeeze()
        .sum(axis=0)
        * 46.006
        / 30.006
        + df_emis.loc[
            (df_emis["Scenario"] == base_scenario)
            & (df_emis["Region"] == "World")
            & (df_emis["Variable"] == "Emissions|NOx|MAGICC AFOLU|Agriculture"),
            "1750":"2300",
        ]
        .interpolate(axis=1)
        .values.squeeze()
        + df_emis.loc[
            (df_emis["Scenario"] == base_scenario)
            & (df_emis["Region"] == "World")
            & (df_emis["Variable"] == "Emissions|NOx|MAGICC Fossil and Industrial"),
            "1750":"2300",
        ]
        .interpolate(axis=1)
        .values.squeeze()
    )[:550, None]
    
    # copied from fair documentation and chrisroadmap files on GitHub
df_solar = pd.read_csv('data/solar_erf_timebounds.csv', index_col="year")
df_volcanic = pd.read_csv('data/volcanic_ERF_1750-2101_timebounds.csv')
solar_forcing = np.zeros(551)
volcanic_forcing = np.zeros(551)
trend_shape = np.zeros(551)
volcanic_forcing[:352] = df_volcanic.erf.values
solar_forcing = df_solar["erf"].loc[1750:2300].values
trend_shape = np.ones(551)
trend_shape[:271] = np.linspace(0, 1, 271)

fill(
    f.forcing,
    volcanic_forcing[:, None, None] * df_configs["fscale_Volcanic"].values.squeeze(),
    specie="Volcanic",
)
fill(
    f.forcing,
    solar_forcing[:, None, None] * df_configs["fscale_solar_amplitude"].values.squeeze()
    + trend_shape[:, None, None] * df_configs["fscale_solar_trend"].values.squeeze(),
    specie="Solar",
)

# copied from fair documentation and chrisroadmap files on GitHub
fill(f.climate_configs["ocean_heat_capacity"], df_configs.loc[:, "clim_c1":"clim_c3"].values)
fill(
    f.climate_configs["ocean_heat_transfer"],
    df_configs.loc[:, "clim_kappa1":"clim_kappa3"].values,
)
fill(f.climate_configs["deep_ocean_efficacy"], df_configs["clim_epsilon"].values.squeeze())
fill(f.climate_configs["gamma_autocorrelation"], df_configs["clim_gamma"].values.squeeze())
fill(f.climate_configs["forcing_4co2"], df_configs["clim_F_4xCO2"])

# decide whether to do a stochastic or predetermined run
fill(f.climate_configs["stochastic_run"], True)
fill(f.climate_configs["seed"], df_configs["seed"])
fill(f.climate_configs["use_seed"], True)
fill(f.climate_configs["sigma_eta"], df_configs["clim_sigma_eta"].values.squeeze())
fill(f.climate_configs["sigma_xi"], df_configs["clim_sigma_xi"].values.squeeze())

f.fill_species_configs(filename='data/species_configs_properties_calibration1.2.0.csv')

# carbon cycle
fill(f.species_configs["iirf_0"], df_configs["cc_r0"].values.squeeze(), specie="CO2")
fill(f.species_configs["iirf_airborne"], df_configs["cc_rA"].values.squeeze(), specie="CO2")
fill(f.species_configs["iirf_uptake"], df_configs["cc_rU"].values.squeeze(), specie="CO2")
fill(f.species_configs["iirf_temperature"], df_configs["cc_rT"].values.squeeze(), specie="CO2")

# aerosol indirect
fill(f.species_configs["aci_scale"], df_configs["aci_beta"].values.squeeze())
fill(f.species_configs["aci_shape"], df_configs["aci_shape_so2"].values.squeeze(), specie="Sulfur")
fill(f.species_configs["aci_shape"], df_configs["aci_shape_bc"].values.squeeze(), specie="BC")
fill(f.species_configs["aci_shape"], df_configs["aci_shape_oc"].values.squeeze(), specie="OC")

# aerosol direct
for specie in [
    "BC",
    "CH4",
    "N2O",
    "NH3",
    "NOx",
    "OC",
    "Sulfur",
    "VOC",
    "Equivalent effective stratospheric chlorine"
]:
    fill(f.species_configs["erfari_radiative_efficiency"], df_configs[f"ari_{specie}"], specie=specie)

# forcing scaling
for specie in [
    "CO2",
    "CH4",
    "N2O",
    "Stratospheric water vapour",
    "Contrails",
    "Light absorbing particles on snow and ice",
    "Land use"
]:
    fill(f.species_configs["forcing_scale"], df_configs[f"fscale_{specie}"].values.squeeze(), specie=specie)
# the halogenated gases all take the same scale factor
for specie in [
    "CFC-11",
    "CFC-12",
    "CFC-113",
    "CFC-114",
    "CFC-115",
    "HCFC-22",
    "HCFC-141b",
    "HCFC-142b",
    "CCl4",
    "CHCl3",
    "CH2Cl2",
    "CH3Cl",
    "CH3CCl3",
    "CH3Br",
    "Halon-1211",
    "Halon-1301",
    "Halon-2402",
    "CF4",
    "C2F6",
    "C3F8",
    "c-C4F8",
    "C4F10",
    "C5F12",
    "C6F14",
    "C7F16",
    "C8F18",
    "NF3",
    "SF6",
    "SO2F2",
    "HFC-125",
    "HFC-134a",
    "HFC-143a",
    "HFC-152a",
    "HFC-227ea",
    "HFC-23",
    "HFC-236fa",
    "HFC-245fa",
    "HFC-32",
    "HFC-365mfc",
    "HFC-4310mee",
]:
    fill(f.species_configs["forcing_scale"], df_configs["fscale_minorGHG"].values.squeeze(), specie=specie)

# ozone
for specie in ["CH4", "N2O", "Equivalent effective stratospheric chlorine", "CO", "VOC", "NOx"]:
    fill(f.species_configs["ozone_radiative_efficiency"], df_configs[f"o3_{specie}"], specie=specie)

# initial value of CO2 concentration (but not baseline for forcing calculations)
fill(
    f.species_configs["baseline_concentration"],
    df_configs["cc_co2_concentration_1750"].values.squeeze(),
    specie="CO2"
)
## Create modified emissions for scenarios other than "base"
# read Ireland emissions file
df_IRL_emis = pd.read_csv(IRL_scenarios_file)

# modify emissions in each scenario by subtracting the Ireland emissions
# from global emissions scenarios with individual gases:
# biogenic CH4, CO2 FFI and AFOLU, N2O
f.emissions.loc[dict(specie="CH4", scenario="IRLCH4",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_CH4 * np.tile(
        df_IRL_emis[('CH4B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CO2 FFI", scenario="IRLCO2",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CO2 AFOLU", scenario="IRLCO2",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="N2O", scenario="IRLN2O",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_N2O * np.tile(
        df_IRL_emis[('N2O-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions

# scenario with all other gases: F-gases and non-biogenic methane
f.emissions.loc[dict(specie="HFC-134a", scenario="IRLother",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_HFC134a * np.tile(
        df_IRL_emis[('HFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CF4", scenario="IRLother",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_CF4 * np.tile(
        df_IRL_emis[('PFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="SF6", scenario="IRLother",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_SF6 * np.tile(
        df_IRL_emis[('SF6-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions

# fossil CH4 is all CH4 minus biogenic CH4; note input file uses same AR5 GWP
# for fossil and biogenic CH4
# for IRL analysis vast majority of CH4 is biogenic and I use the same data for the all CH4 (meaning fossil CH4 is 0)
# this is to be consistent with the Wheatley 2021 historical dataset...
f.emissions.loc[dict(specie="CH4", scenario="IRLother",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_CH4 * np.tile(
        df_IRL_emis[('CH4-' + IRL_scenario)] - df_IRL_emis[('CH4B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T

# given the marginal changes relative to global emissions, effects of individual gases
# should be additive but just to confirm, I also run a scenario "IRLall"
# where all gases are applied
f.emissions.loc[dict(specie="CO2 FFI", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CO2 AFOLU", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="N2O", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_N2O * np.tile(
        df_IRL_emis[('N2O-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CH4", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_CH4 * np.tile(
        df_IRL_emis[('CH4-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="HFC-134a", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_HFC134a * np.tile(
        df_IRL_emis[('HFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CF4", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_CF4 * np.tile(
        df_IRL_emis[('PFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="SF6", scenario="IRLall",
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_SF6 * np.tile(
        df_IRL_emis[('SF6-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions

# now we define scenarios where emissions stop after "base_year"
# this will tells us how much warming is due to 'historical' emissions (all emissions up to base_year), and
# how much warming is due to emissions after base_year
df_IRL_emis.loc[df_IRL_emis['Year'] > int(base_year), df_IRL_emis.columns[1:]] = 0.0

# scenarios with individual gases: biogenic CH4, CO2 FFI and AFOLU, N2O
f.emissions.loc[dict(specie="CH4", scenario=("IRLCH4_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_CH4 * np.tile(
        df_IRL_emis[('CH4B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CO2 FFI", scenario=("IRLCO2_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CO2 AFOLU", scenario=("IRLCO2_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="N2O", scenario=("IRLN2O_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_N2O * np.tile(
        df_IRL_emis[('N2O-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions

#scenario with all other gases: F-gases and non-biogenic methane
f.emissions.loc[dict(specie="HFC-134a", scenario=("IRLother_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_HFC134a * np.tile(
        df_IRL_emis[('HFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CF4", scenario=("IRLother_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_CF4 * np.tile(
        df_IRL_emis[('PFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="SF6", scenario=("IRLother_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_SF6 * np.tile(
        df_IRL_emis[('SF6-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CH4", scenario=("IRLother_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_CH4 * np.tile(
        df_IRL_emis[('CH4-' + IRL_scenario)] - df_IRL_emis[('CH4B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T

# scenario with all gases
f.emissions.loc[dict(specie="CO2 FFI", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CO2 AFOLU", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-6 * np.tile(
        df_IRL_emis[('CO2B-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="N2O", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_N2O * np.tile(
        df_IRL_emis[('N2O-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CH4", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1.0E-3/GWP_CH4 * np.tile(
        df_IRL_emis[('CH4-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="HFC-134a", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_HFC134a * np.tile(
        df_IRL_emis[('HFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="CF4", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_CF4 * np.tile(
        df_IRL_emis[('PFC-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions
f.emissions.loc[dict(specie="SF6", scenario=("IRLall_" + base_year),
        timepoints=slice(df_IRL_emis['Year'].iloc[0], df_IRL_emis['Year'].iloc[-1] + 1))] -= 1./GWP_SF6 * np.tile(
        df_IRL_emis[('SF6-' + IRL_scenario)], (f.emissions.shape[2], 1)).T # subtract IRL emissions from global emissions

## Run fair in parallel mode
# copied from fair documentation and chrisroadmap files on GitHub
initialise(f.concentration, f.species_configs["baseline_concentration"])
initialise(f.forcing, 0)
initialise(f.temperature, 0)
initialise(f.cumulative_emissions, 0)
initialise(f.airborne_emissions, 0)

f.run()

## Extract temperature results (with 1850-1900 offset) and save to csv file
# copied from fair documentation and chrisroadmap files on GitHub
weights_51yr = np.ones(52)
weights_51yr[0] = 0.5
weights_51yr[-1] = 0.5
T_offset = np.average(
                f.temperature.loc[
                    dict(scenario="base", timebounds=np.arange(1850, 1902), layer=0)
                ],
                weights=weights_51yr,
                axis=0
            )
# create the data array that will be written as output to a csv file
# output years
output_array = f.timebounds.T
output_header = "Year"
output_format = "%d"

# global warming for gobal emissions defined in the base_scenario
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] - T_offset, axis=1,)]
output_header += "," + base_scenario
output_format += ", %f"

for scenario in scenarios:
    # step through all other scenarios and save the difference with the base_scenario
    # so we get warming due to New Zealand emissions. Note we need to save the median
    # of the differences across all configs, not the difference of the medians
    # (as discussed with Chris via email)
    if scenario != "base":
        output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] -
                      f.temperature.loc[dict(scenario=scenario, layer=0)], axis=1,)]
        output_header += "," + scenario
        output_format += ", %f"
        
# calculate warming caused by emissions of individual gas from base_year - warming
# from full emissions minus historical
output_header += ", CH4_from_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario=("IRLCH4_" + base_year), layer=0)] -
                      f.temperature.loc[dict(scenario="IRLCH4", layer=0)], axis=1,)]
output_header += ", CO2_from_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario=("IRLCO2_" + base_year), layer=0)] -
                      f.temperature.loc[dict(scenario="IRLCO2", layer=0)], axis=1,)]
output_header += ", N2O_from_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario=("IRLN2O_" + base_year), layer=0)] -
                      f.temperature.loc[dict(scenario="IRLN2O", layer=0)], axis=1,)]
output_header += ", other_from_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                      f.temperature.loc[dict(scenario="IRLother", layer=0)], axis=1,)]
output_header += ", all_from_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario=("IRLall_" + base_year), layer=0)] -
                      f.temperature.loc[dict(scenario="IRLall", layer=0)], axis=1,)]

# calculate sum of warming from individual emissions and warming from 'future' emissions
# (a long list of different possible combinations to allow multiple ways of plotting results)

# warming from all CO2 and N2O emissions
output_header += ", CO2+N2O"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 2.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)], axis=1,)]

# warming from all emissions other than biogenic CH4
output_header += ", nonCH4"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLother", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)], axis=1,)]

# warming from all CO2 emissions plus historical N2O emissions
output_header += ", CO2+N2O_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 2.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLN2O_" + base_year), layer=0)], axis=1,)]

# warming from all CO2 and N2O emissions plus historical emissions of 'other' gases (F-gases and fossil CH4)
output_header += ", CO2+N2O+other_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)], axis=1,)]

# warming from all non-biogenic CH4 emissions plus historical biogenic CH4
output_header += ", nonCH4+CH4_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 4.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLother", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLCH4_" + base_year), layer=0)], axis=1,)]

# warming from all historical emissions plus future CO2 emissions
output_header += ", all_" + base_year + "+CO2"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 4.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLN2O_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLCH4_" + base_year), layer=0)], axis=1,)]

# warming from all historical emissions plus future CO2 and N2O emissions
output_header += ", all_" + base_year + "+CO2+N2O"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 4.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLCH4_" + base_year), layer=0)], axis=1,)]

# warming from all historical emissions plus all future emissions except biogenic CH4
output_header += ", all_" + base_year + "+nonCH4"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 4.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLother", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLCH4_" + base_year), layer=0)], axis=1,)]

# warming from hjistorical CO2 and historical N2O
output_header += ", CO2_" + base_year + "+N2O_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 2.0 -
                     f.temperature.loc[dict(scenario=("IRLCO2_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLN2O_" + base_year), layer=0)], axis=1,)]

# warming from all historical emissions other than biogenic CH4
output_header += ", nonCH4_" + base_year
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario=("IRLCO2_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLN2O_" + base_year), layer=0)], axis=1,)]

# warming from all historical emissions other than biogenic CH4 plus future N2O emissions
output_header += ", nonCH4_" + base_year + "+N2O"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario=("IRLCO2_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)], axis=1,)]

# warming from all historical emissions other than biogenic CH4 plus future N2O and 'other' (F-gas and fossil CH4) emissions
output_header += ", nonCH4_" + base_year + "+N2O+other"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario=("IRLCO2_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario="IRLother", layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)], axis=1,)]

# warming from all historical emissions other than biogenic CH4 plus future CO2
output_header += ", nonCH4_" + base_year + "+CO2"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLN2O_" + base_year), layer=0)], axis=1,)]

# warming from all historical emissions other than biogenic CH4 plus future CO2 and future N2O
output_header += ", nonCH4_" + base_year + "+CO2+N2O"
output_format += ", %f"
output_array = np.c_[output_array, np.median(f.temperature.loc[dict(scenario="base", layer=0)] * 3.0 -
                     f.temperature.loc[dict(scenario="IRLCO2", layer=0)] -
                     f.temperature.loc[dict(scenario=("IRLother_" + base_year), layer=0)] -
                     f.temperature.loc[dict(scenario="IRLN2O", layer=0)], axis=1,)]
            
# save data arrary as CSV file, with global background scenario, New Zealand scenario and base_year in file name
np.savetxt('IRL_' + base_scenario + '_' + IRL_scenario + base_year + '.csv',
            output_array,
            header = output_header,
            fmt = output_format,
            delimiter = ','
          )
'IRL_' + base_scenario + '_' + IRL_scenario + base_year + '.csv'
# 'IRL_ssp126_ERP21990.csv'
