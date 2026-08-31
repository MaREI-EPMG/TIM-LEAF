# Installing and using fair with TIM-LEAF
## Origins and purpose

FaIR v2.1.3 ([Leach et al., 2021](https://doi.org/10.5194/gmd-14-3007-2021); [Smith, 2023](https://github.com/OMS-NetZero/FAIR/releases), [2024a](https://doi.org/10.5281/zenodo.10566813)) has been incorporated as a module in the TIM-LEAF framework.

The approach of the Climate Change Commission (CCC) in New Zealand was replicated to assess the warming impact of national greenhouse gas emissions pathways ([Climate Change Commission, 2024b](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Technical-Annex-Final-reports-on-the-fourth-emissions-budget-and-2050-target-review-Dec-2024.pdf), [2024a](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Input-data-files-for-temperature-modelling-final-2050-target-advice.zip); [Smith, 2024b](https://doi.org/10.5281/zenodo.13142999); [Smith et al., 2021](https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_Chapter07_SM.pdf)).

This approach uses a modified locally compiled version of the fair v2.1.3 (`fair.py`) source code so that global baseline emissions scenarios can represent a country level contribution, in this case Ireland’s contribution ([Climate Change Commission, 2024b](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Technical-Annex-Final-reports-on-the-fourth-emissions-budget-and-2050-target-review-Dec-2024.pdf)). The modified `fair.py` has two additional functions  
(i.e. def fill_scenarios_from_rcmip(self, RCMIPscenario) and def fill_scenario_from_rcmip(self, scenario,RCMIPscenario)), otherwise it is the same as the original.

The first function fills all scenarios that fair will run with the same global reduced complexity model intercomparison project (RCMIP) emissions scenario, in this case Shared Socioeconomic Pathway (SSP) 1-2.6 ([Nicholls et al., 2020](https://doi.org/10.5281/zenodo.4589756)).

The second function fills a specified fair scenario with a given emissions scenario.

This allows (1) the warming that would have happened without Ireland’s emissions and (2) the difference between the global baseline and the global baseline without Ireland’s emissions, which can be interpreted as the warming caused by Ireland’s emissions’, to be calculated ([Climate Change Commission, 2024b](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Technical-Annex-Final-reports-on-the-fourth-emissions-budget-and-2050-target-review-Dec-2024.pdf)).

## Instructions to compile fair with a modified fair.py file

Needs *python* and *pip* installed.

This modelling is based on fair v2.1.3. The latest version is [fair v2.2.4](https://docs.fairmodel.net/en/latest/). There is no change to the physical climate outcome in any way between these two versions as this depends on the calibration dataset.

The fair v2.1.3 source code was modified to

1. make it easier to read in a global baseline emissions scenario and

2. reflect a country-level contribution (this is no longer necessary as later versions of fair  read in emissions in a different way)

To run this version fair will need to be compiled locally with a modified `fair.py` rather than the standard version that come via  
python pip.

To do this:

1. download [fair v2.1.3 source code](https://github.com/OMS-NetZero/FAIR/releases) under November 23 2023 fair v2.1.3

2. replace `fair.py` (in `/FAIR-2.1.3/src/fair/fair.py`) with this version [`fair.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/fair.py)(originally sourced from the CCC in New Zealand).

3. run setup using:

```bash
pip install -e .
```

The fair.py file is the same as the original, but with two  
added functions:

```python
def fill_scenarios_from_rcmip(self, RCMIPscenario)
def fill_scenario_from_rcmip(self, scenario, RCMIPscenario)
```

The first function fills all scenarios that fair will run with the same global RCMIP emissions scenario. The second function fills a specified fair scenario with a given RCMIP emissions scenario.

## Instructions to run fair for country-level GHG emissions pathways

The Python script [`countrylevel_IRL.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/countrylevel_IRL.py) used to run this analysis for Ireland, is based on a [Jupyter Notebook script](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Input-data-files-for-temperature-modelling-final-2050-target-advice.zip) from the CCC ([Climate Change Commission, 2024a](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Input-data-files-for-temperature-modelling-final-2050-target-advice.zip), [2024b](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Technical-Annex-Final-reports-on-the-fourth-emissions-budget-and-2050-target-review-Dec-2024.pdf)). 

It uses the first of the two added functions and then subtracts the values of Ireland’s emissions (e.g. CO₂, N₂O and CH₄) from global emissions to calculate the warming that would have happened without Ireland’s emissions and the difference between the global baseline and the global baseline minus Ireland’s emissions, is then interpreted as 'the warming caused by Ireland’s emissions'.

The original script was reviewed by Chis Smith for the New Zealand CCC.

**Ireland-specific modification:**

The `countrylevel_IRL.py` was minimally modified as follows: 

1. A scenario selection variable, IRL_scenario, was introduced to specify which Irish scenario is being anaylysed. For example, setting it to IRL_scenario = "S3" means that the model will run the S3 emissions scenario. Each scenario is run one at a time, so the user specifies the required scenario by changing the value of IRL_scenario.

2. A list called IRL_scenarios was also added to link each scenario with the path of its corresponding input data file:

``` python
IRL_scenarios = [("BAU", "data/BAU.vd"), ("S1", "data/S1.vd"), ("S2", "data/S2.vd"), ("S3", "data/S3.vd")]
```

To add new scenarios, the new scenario data must be provided in the same format and structure as the existing data, and the new scenario must then be added to the IRL_scenarios list, including the name and path to its data file.

3. To transfer the Ireland scenario data generated by the TIMLEAF data-transfer script into the corresponding emission template file (IRL_histWheatley2021_Scenario.csv), we use the function 

```python
exchange_data(IRL_scenarios, IRL_scenarios_file)
```

## Inputs
Input files for calibration and global emissions can be found [here](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/fair/input).

### Calibration
It is important to use the same input files for climate calibration and species properties calibration
-	file v1.4.2; calibrated_constrained_parameters-v1.4.2.csv ([Smith 2024a](https://doi.org/https://doi.org/10.5281/zenodo.10566813 ), [2024b](https://doi.org/https://doi.org/10.5281/zenodo.13142999 ))
-	file v1.2.0; species_configs_properties_calibration1.2.0.csv ([Smith 2024a](https://doi.org/https://doi.org/10.5281/zenodo.10566813 ), [2024b](https://doi.org/https://doi.org/10.5281/zenodo.13142999 ))

Note that both have newer versions available, but it is not possible to guarantee that they work with this version of fair (v2.1.3) and this python script. Any difference in actual modelled warming should be so minor as to be not relevant.

Use
-	solar_erf_timebounds.csv  ([Smith 2024a](https://doi.org/https://doi.org/10.5281/zenodo.10566813 ), [2024b](https://doi.org/https://doi.org/10.5281/zenodo.13142999 ))
-	volcanic_ERF_1750-2101_timebounds.csv ([Smith 2024a](https://doi.org/https://doi.org/10.5281/zenodo.10566813 ), [2024b](https://doi.org/https://doi.org/10.5281/zenodo.13142999 ))

### Global emissions files
Use
-	rcmip-concentrations-annual-means-v5-1-0.csv ([Nicholls & Lewis 2021](https://doi.org/10.5281/zenodo.4589756))
-	rcmip-emissions-annual-means-v5-1-0.csv ([Nicholls & Lewis 2021](https://doi.org/10.5281/zenodo.4589756))
-	rcmip-radiative-forcing-annual-means-v5-1-0.csv ([Nicholls & Lewis 2021](https://doi.org/10.5281/zenodo.4589756))

### Country-level GHG emissions pathways
A file of [combined historical and TIM-LEAF scenarios data](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/data/combined) e.g.  IRL_histWheatley2021_S3.csv is an emissions input file for Ireland (1750 to 2070). Created as detailed [here](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/README.md).

The scenario can have any name but it must match the scenario name provided in the python script. Data are expected annually from (1750 or) 1850 to 2299. 

## Key steps
The python countrylevel_IRL.py script has various comments that explain the key steps. 

Key steps are to define the global emissions scenario (this is important as the radiative efficacy of a country’s emissions depends on global background concentrations), the name of the specific country-level emissions scenario you want to run (e.g. ‘BAU'), and a historical reference year (e.g. 1990 or 2026). 

The historical reference year is used to quantify how much emissions since a given date have contributed to global warming (this is important to show how much of the total warming is due to recent emissions, i.e. CH₄, compared to historical emissions). 

Now the specific fair scenarios that you want to run are defined (1) the global baseline and then (2) the warming from each individual gas at country level as specified.  

There are three different types of scenario:
1.	global emissions scenario (e.g. ssp126) 
2.	Ireland’s emissions scenario (e.g. BAU)
3.	fair scenarios (e.g. IRLCO2, which is defined as global emissions minus in this case Ireland’s (i.e. country level) fossil fuel CO₂ emissions). 

Fair 'runs' the fair scenarios. The other scenarios are used only to define the emissions used in those fair scenarios. 

After these initial definitions (first block of code) fair is being set up in the standard way. 

Then after the line 
```python
df_IRL_emis = pd.read_csv(IRL_scenarios_file) 
```

comes a block of code where the calculations are done to define the fair scenarios, i.e. global emissions minus the Ireland emissions of a specific gas; and for the historical reference year, global emissions minus Ireland emissions of an Ireland emissions of a specific gas; and for the historical reference year, global emissions minus Ireland emissions of a specific gas up to the historical reference year.

Now fair is run. 

## Outputs

Outputs are written to a file, including various ways of expressing the warming from multiple gases, including the warming from emissions after the historical reference year. 

Output appears in a .csv file with a name that is COUNTRY_GLOBALSCENARIO_COUNTRY-SCENARIO&YEAR.csv e.g. [IRL_ssp126_BAU2020.csv](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/fair/output).

YEAR is the year you are interested in assessing temperature change from. It can be any year (e.g. 1990, 2015, 2020 or most recent year) depending on what you want from your scenarios analysis.

A file e.g. [NZ_ssp126_EB41990.xlsx](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/fair/output) (sourced from the CCC in New Zealand) with some rudimentary graphs to demonstrate how the individual calculated columns can work to show total warming, or the warming from emissions since the historical reference year, i.e. 2020, or the contribution from emissions up to 2020 and from 2021. 

## References
- Climate Change Commission. (2024a). Input data files for temperature modelling, New Zealand. 

- Climate Change Commission. (2024b). Technical annex final report on the fourth emissions budget and 2050 target review.

- Leach NJ, Jenkins S, Nicholls Z, Smith CJ, Lynch J, Cain M, Walsh T, Wu B, Tsutsui J & Allen MR (2021). FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration. Geoscientific Model Development, 14(5), 3007–3036. https://doi.org/10.5194/gmd-14-3007-2021

- Nicholls Z, Meinshausen M, Lewis J, Gieseke R, Dommenget D, Dorheim K, Fan C-S, Fuglestvedt JS, Gasser T, Golüke U, Goodwin P, Hartin C, Hope AP, Kriegler E, Leach NJ, Marchegiani D, McBride LA, Quilcaille Y, Rogelj J, Salawitch RJ, Samset BH, Sandstad M, Shiklomanov AN, Skeie RB, Smith CJ, Smith S, Tanaka K, Tsutsui J & Xie Z (2020). Reduced Complexity Model Intercomparison Project Phase 1: Introduction and evaluation of global-mean temperature response. Geoscientific Model Development, https://doi.org/10.5194/gmd-13-5175-2020

- Nicholls Z & Lewis J (2021). Reduced Complexity Model Intercomparison Project (RCMIP) protocol (Version v5.1.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.4589756

- Smith C (2023). FaIR Version 2.1.3. https://doi.org/https://github.com/OMS-NetZero/FAIR/releases 
- Smith C (2024a). FaIR calibration data. https://doi.org/https://doi.org/10.5281/zenodo.10566813 
- Smith C (2024b). FaIR calibration data (1.4.2) [Dataset]. Zenodo. https://doi.org/https://doi.org/10.5281/zenodo.13142999 
- Smith C, Gasser T, Nicholls Z, Armour K, Collins W, Forster P, Meinshausen M, Watanabe M (2021). The Earth’s Energy Budget, Climate Feedbacks and Climate Sensitivity Supplementary Material. In Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change.  [Masson-Delmotte V, Zhai P, Pirani A,  Connors SL, Péan C, Berger S, Caud N, Chen Y, Goldfarb L, Gomis MI, Huang M, Leitzell, K, Lonnoy E, Matthews JBR, Maycock TK, Waterfield T, Yelekçi O, Yu R & Zhou B (eds.)]
- Wheatley, J. (2021). Ireland greenhouse gas and sulphate aerosol emissions 1745-2019. https://doi.org/https://doi.org/10.5281/zenodo.7004406
- Wheatley, J. (2023). Temperature neutrality and Irish methane policy. Climate Policy, 23(10), 1229–1242. https://doi.org/10.1080/14693062.2023.2191921
