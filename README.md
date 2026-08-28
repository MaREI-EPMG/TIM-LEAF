
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

# TIMES-Ireland Model for land, energy, agriculture and forestry systems (TIM-LEAF v1.0)

[![DOI](https://zenodo.org/badge/429173600.svg)](https://zenodo.org/badge/latestdoi/429173600)

## Purpose of the model
TIM-LEAF is a national integrated model of Ireland's land, energy, agriculture and forestry systems. The model extends the [TIMES-Ireland Model (TIM)](https://github.com/MaREI-EPMG/times-ireland-model) to represent interactions between energy-system transformation, land availability, agricultural production, forestry, bioenergy, carbon stocks and greenhouse gas emissions within a single modelling framework.

Most energy-system models focus primarily on technologies, fuels and energy demand. They may not explicitly represent the emissions and land-use implications of agriculture, forestry, bioenergy, carbon dioxide removal and other land-based mitigation options, or the competition between different uses of land.

TIM-LEAF addresses these interactions by representing land, bioenergy, carbon and energy as interconnected resources within an integrated national model.

TIM-LEAF is soft-linked to FaIR v2.1.3 ([Leach et al., 2021](https://gmd.copernicus.org/articles/14/3007/2021); [Smith, 2023](https://github.com/OMS-NetZero/FAIR/releases); [Smith, 2024](https://doi.org/10.5281/zenodo.13951079)), a simple climate model used to assess the temperature response associated with national greenhouse-gas emissions pathways.


## Documentation
More information on the TIMES model generator and specific information about TIM can be found in the [Documentation](https://doi.org/10.5194/gmd-15-4991-2022) and the [repository](https://github.com/MaREI-EPMG/times-ireland-model).

Source code for FaIR v2.1.3  soft linked to TIM-LEAF is available [here](https://github.com/OMS-NetZero/FAIR/releases) under November 23 2023 fair v2.1.3. 


## About the developers
The list of developers and funding is described in the [Acknowledgements](/ACKNOWLEDGEMENT.md) section. 

# TIM-LEAF-FaIR integration
All files associated with the TIM-LEAF-FaIR integration can be found in the [folder](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow).

## Country-level emissions contribution in FaIR
Compiling and running FaIR v 2.1.3 with a `modified fair.py` is documented [here](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/fair_readme.md).

## Running the TIM-LEAF–FaIR workflow
The integrated TIM-LEAF–FaIR workflow consists of running TIM-LEAF, transferring and processing the resulting emissions data and running the FaIR model. The workflow requires [TIM-LEAF model outputs](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/data/TIM-LEAF_scenarios), the TIM-LEAF–FaIR data transfer script [`data_transfer_from_TIM.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/data_transfer_from_TIM.py), the FaIR script [`countrylevel_IRL.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/countrylevel_IRL.py) and the required Python dependencies.

## TIM-LEAF to FaIR data transfer
The data-transfer pipeline provides the interface between TIM-LEAF and FaIR. TIM-LEAF produces detailed model output files in VEDA .vd format, while FaIR requires emissions data in a different structure. The [`data_transfer_from_TIM.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/data_transfer_from_TIM.py) converts the relevant TIM-LEAF outputs into the emissions format required by the FaIR workflow.

For the diagnostic scenarios included in this repository, `data_transfer_from_TIM.py` reads the TIM-LEAF output files for the BAU, S1, S2 and S3 scenarios. These files are provided in the [directory](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/data/TIM-LEAF_scenarios) and are named as BAU.vd, S1.vd, S2.vd and S3.vd, respectively. The script reads the VEDA output files, selects the relevant emissions outputs and model years, maps TIM-LEAF emission commodities to the emissions categories required by FaIR, aggregates the results by year and scenario, and applies the required gas-specific unit conversions. It also processes land-use and land-use change CO₂ emissions and removals, calculates annual changes in harvested wood product carbon storage, and incorporates these changes into the land-use emissions balance.

The processed TIM-LEAF emissions are then combined with the base emissions time series required by the FaIR workflow, [provided by the file](https://github.com/MaREI-EPMG/FAIR/blob/master/data/TIMLEAF_Emissions.csv). 
The processed TIM-LEAF emissions are then combined with the base historical emissions time series required by the FaIR workflow, provided in [IRL_histWheatley2021_1750-2019](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/data/historical) ([Wheatley 2021](https://doi.org/https://doi.org/10.5281/zenodo.7004406), [Wheatley 2023](https://doi.org/10.1080/14693062.2023.2191921)). 

The resulting Ireland-specific emissions dataset contains the emissions components required by the FaIR workflow, including CO₂, CH₄, N₂O, HFCs, PFCs, SF₆, biogenic and land-use CO₂ (CO2B) and biogenic CH₄ (CH4B). The processed data are written to a scenario-specific CSV file, for example [IRL_histWheatley2021_S3.csv](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/data/combined) when the S3 scenario is selected. 

The Ireland-specific emissions file generated by the data-transfer step is then read by the FaIR script `countrylevel_IRL.py`. More infomration doucmented in this [file](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/fair_readme.md). 

This data-transfer pipeline is a central component of the TIM-LEAF–FaIR integration. It provides the automated translation between the detailed output structure of TIM-LEAF and the emissions input structure required by FaIR, allowing the workflow from TIM-LEAF optimisation to FaIR temperature projections to be performed without manual preparation of the emissions data. 


## Climate policy use
TIM-LEAF provides an integrated framework for assessing national climate mitigation pathways across the land use, energy, agriculture and forestry sectors. By having these sectors within a single optimisation framework, the model captures interactions and trade-offs that may be missed when sectors are modelled independently.
The model can assess how alternative agricultural and land-use pathways affect emissions trajectories, land allocation, biomass availability for energy and carbon dioxide removal (CDR), and the configuration and cost of the energy system. 

This allows mitigation options such as agricultural methane reduction, afforestation, land-use change and bioenergy to be evaluated alongside energy-system mitigation.
The TIM-LEAF–FaIR workflow further allows multi-gas emissions pathways to be translated into temperature responses, providing an additional basis for comparing alternative national mitigation strategies and understanding the contribution of individual greenhouse gases to climate outcomes.

## Scenario descriptions
The scenarios included in the repository are initial diagnostic scenarios developed to show and evaluate the integrated capabilities of TIM-LEAF. As the model continues to be developed and applied to new research questions, updated scenario sets will be added to the repository.The scenarios explore how different combinations of bioenergy, afforestation and agricultural methane mitigation reshape the least cost transition pathway across the integrated framework: 
- BAU – reference scenario representing current trends 
- S1 – Biomass-intensive mitigation pathway prioritising high land allocation to domestic bioenergy and forest biomass extraction
- S2 – A balanced pathway with reduced biomass availability relative to S1 and mitigation is distributed across afforestation and RE expansion
- S3 - A structural transformation pathway in which reduced agricultural demand and methane mitigation reduce pressure on land resources, allowing large scale afforestation and ecosystem restoration. 

Zenodo [repository of scenarios](https://doi.org/10.5281/zenodo.5517363)

## Visualisation 
- [Web app](https://epmg-dash-new-look-w0b6.onrender.com/dashboard?study_id=18&tab=charts&scenario_id=90&sector=SYS&subsector=Total+Primary+Energy+Demand) visualising results from TIM-LEAF scenarios. Users can create their own visualisations by exporting the relevant TIM-LEAF results from the dashboard. 

## Acknowledgements

The authors thank the original TIM developers and contributors, including [Balyk et al., 2022](https://doi.org/10.5194/gmd-15-4991-2022), for the source code and associated materials, which are available in the [TIMES-Ireland Model repository](https://github.com/MaREI-EPMG/times-ireland-model) and the [TIMES-Ireland Model Zenodo archive](https://doi.org/10.5281/zenodo.5517363).

We thank the New Zealand Climate Change Commission for providing the modified version of the FaIR v2.1.3 source code used in this work ([Climate Change Commission, 2024](https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Technical-Annex-Final-reports-on-the-fourth-emissions-budget-and-2050-target-review-Dec-2024.pdf)). Thanks to Chris Smith who made the original modifications to the FaIR v2.1.3 source code ([Smith, 2023](https://github.com/OMS-NetZero/FAIR/releases)).

D.J, R.M and H.D are supported by the SELFS (Sustainable integrated pathways for carbon-negative energy, land and food systems) project (Grant No. 2022-CE-1137). This project is funded under the EPA Research Programme 2021-2030. The EPA Research Programme is a Government of Ireland initiative funded by the Department of the Environment, Climate and Communications. V.A, B.S and H.D are supported by the CAPACITY Project (Grant No. RFT2022/S 164-466018) funded by the Department of Climate, Energy and the Environment (DCEE), through the Climate and Energy Modelling Services to the Climate Energy Modelling Group (CEMG). Z.H is supported by MaREI, the Research Ireland Centre for Energy, Climate and Marine (Grant No. 12/RC/2302_P2).


## Peer-reviewed publications

- [TIM: modelling pathways to meet Ireland's long-term energy system challenges with the TIMES-Ireland Model (v1.0)](https://doi.org/10.5194/gmd-15-4991-2022). 2022. *Geoscientific Model Development*.
- [Low energy demand scenario for feasible deep decarbonisation: Whole energy systems modelling for Ireland](https://doi.org/10.1016/j.rset.2022.100024). 2022. *Renewable and Sustainable Energy Transition*.
- [Decarbonisation of passenger light-duty vehicles using spatially resolved TIMES-Ireland Model](https://doi.org/10.1016/j.apenergy.2022.119078). 2022. *Applied Energy*.


## References 
- Balyk, O., Glynn, J., Aryanpur, V., Gaur, A., McGuire, J., Smith, A., Yue, X., & Daly, H. (2022). TIM: Modelling pathways to meet Ireland’s long-term energy system challenges with the TIMES-Ireland Model (v1.0). Geoscientific Model Development, 15(12), 4991–5019. https://doi.org/10.5194/gmd-15-4991-2022

- Balyk, O., Glynn, J., Aryanpur, V., Gaur, A., McGuire, J., Smith, A., Yue, X., Chiodi, A., Gargiulo, M., & Daly, H. (2024). TIMES-Ireland Model (Version v1.1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.14284187

- Climate Change Commission. (2024). Technical annex final report on the fourth emissions budget and 2050 target review. https://www.climatecommission.govt.nz/assets/Advice-to-govt-docs/Target-and-budgets-final-reports/Technical-Annex-Final-reports-on-the-fourth-emissions-budget-and-2050-target-review-Dec-2024.pdf

- Leach, N. J., Jenkins, S., Nicholls, Z., Smith, C. J., Lynch, J., Cain, M., Walsh, T., Wu, B., Tsutsui, J., & Allen, M. R. (2021). FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration. Geoscientific Model Development, 14(5), 3007–3036. https://doi.org/10.5194/gmd-14-3007-2021

- Smith, C. (2023). FaIR Version 2.1.3. https://doi.org/https://github.com/OMS-NetZero/FAIR/releases

- Smith, C. (2024). FaIR calibration data. https://doi.org/https://doi.org/10.5281/zenodo.10566813

- Wheatley, J. (2021, October 6). Ireland greenhouse gas and sulphate aerosol emissions 1745-2019. https://doi.org/https://doi.org/10.5281/zenodo.7004406

- Wheatley, J. (2023). Temperature neutrality and Irish methane policy. Climate Policy, 23(10), 1229–1242. https://doi.org/10.1080/14693062.2023.2191921
