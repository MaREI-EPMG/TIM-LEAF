
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

# TIMES-Ireland Model for land, energy, agriculture and forestry systems (TIM-LEAF v1.0)

[![DOI](https://zenodo.org/badge/429173600.svg)](https://zenodo.org/badge/latestdoi/429173600)

## Purpose of the model
TIM-LEAF is a national integrated model of Ireland's land, energy, agriculture and forestry systems. The model extends the [TIMES-Ireland Model (TIM)](https://github.com/MaREI-EPMG/times-ireland-model) to represent interactions between energy-system transformation, land availability, agricultural production, forestry, bioenergy, carbon stocks and greenhouse gas emissions within a single modelling framework.

The underlying TIM represents the Irish energy system, including energy supply, conversion technologies, transmission infrastructure and end-use sectors. TIM-LEAF extends this framework by making key processes in the agriculture, land-use and forestry systems endogenous to the optimisation. Agricultural mitigation, afforestation, bioenergy and carbon dioxide removal technologies can be evaluated alongside energy-system transformation rather than in silos. 

TIM-LEAF can be run under alternative scenario assumptions, including business-as-usual conditions and cumulative carbon-budget constraints. The model identifies the least-cost system configuration satisfying the specified scenario constraints.

TIM-LEAF is soft-linked to FaIR v2.1.3 ([Leach et al., 2021](https://gmd.copernicus.org/articles/14/3007/2021); [Smith, 2023](https://github.com/OMS-NetZero/FAIR/releases); [Smith, 2024](https://doi.org/10.5281/zenodo.13951079)), a simple climate model used to assess the temperature response associated with national greenhouse-gas emissions pathways.


## TIM-LEAF development
The main model devlopments are: 

- updated agricultural mitigation options based on Teagasc marginal abatement cost (MAC) curves;
- a national land-use system representing seven aggregated land categories
- a new forestry system representing forest land, forest biomass harvesting and future afforestation pathways 
- forest carbon sequestration and saturation dynamics
- harvested wood product (HWP) carbon storage
- endogenous bioenergy supply linked to agricultural land and forestry biomass;
- integrated GHG accounting across energy, agriculture and LULUCF

## Model architecture

### Land use system
The national land-use system is dissagregated into seven land categories within the model, callibrated against the National Inventory Document (NID). TIM-LEAF focuses on forest land, grassland, cropland and wetland/peatlands as they account for the majority of Ireland’s LULUCF greenhouse gas fluxes and represent key mitigation pathways. 

Land allocation is governed by:

$$
L_{\mathrm{agri},m,t}
+
\sum_{a \in A_{\mathrm{AFOLU}}}
L_{a,m,t}
\leq
S_{m,t}
$$

where $L_{\mathrm{agri},m,t}$ is the agricultural land requirement, $L_{a,m,t}$ represents land endogenously allocated to bioenergy production and other AFOLU land-use pathways, and $S_{m,t}$ is the total available area of land type $m$.

Agricultural land requirements are determined from exogenously specified crop and livestock production. The remaining land is then available for endogenous allocation between competing AFOLU uses, including bioenergy and forestry. 

Land-use transitions are constrained by physical land availability and allowable conversion pathways:

$$
S_{m,t+1} = S_{m,t} + \sum_{n \neq m} \mathrm{CONV}_{n \rightarrow m,t} - \sum_{n \neq m} \mathrm{CONV}_{m \rightarrow n,t}
$$

This formulation conserves total land area while allowing transitions between land categories over time.

###  Energy system 
The energy system in TIM-LEAF builds on the optimisation framework developed by [(Balyk et al., 2022)](https://doi.org/10.5194/gmd-15-4991-2022), representing the full energy system, including primary energy supply, conversion technologies, transmission infrastructure, and end-use sectors. Detailed formulation and sectoral assumptions are described in [(Balyk et al., 2022)](https://doi.org/10.5194/gmd-15-4991-2022).

### Agriculture system 
The existing Agri-TIMES representation was extended and updated to incorporate agricultural mitigation options based on marginal abatement cost (MAC) curves developed by [Teagasc (2023)](https://teagasc.ie/environment/climate-centre/publications/reports/marginal-abatement-cost-curve-2023/). The model includes mitigation options across different levels of technology readiness, including: low-emission slurry spreading (LESS), clover inclusion, manure storage covers, manure acidification, anerobic digestion and menthane inhibitors. 

In the core scenarios, adoption of agricultural mitigation technologies is influenced by the marginal abatement costs, uptake dynamics and deployment limits capping the  maximum share of technology rollout. 

TIM-LEAF includes a low-demand scenario represents structural change in agriculture, with reduced livestock production and increased cereal output. Cereal area follows FAPRI projections [(Lanigan et al., 2024)](https://teagasc.ie/publications/modelling-irish-agricultural-ghg-emissions-and-mitigation-to-2050-scenarios-for-the-carbon-budgets-working-group-php/), while dairy and non-dairy cattle are assumed to
decline by 50% by 2050 relative to 2022 levels.

###  Forest system 
The forestry system is a major and new component developed as part of TIM-LEAF, to include: 
- forest land and biomass production
- biomass harvesting across thinning and felling practices
- future afforestation pathways 
- forest carbon sequestration and carbon saturation dynamics
- harvested wood product (HWP) carbon storage

#### Sustainable forest harvest 
The model determines the  level of forest harvesting subject to this constraint:

$$ H^{\max}_{f,t} = \theta_{f,t} \cdot S_{\mathrm{for},t} $$

where $H$<sup>max</sup><sub>f,t</sub> is the maximum harvest, 
$\theta$<sub>f,t</sub> is the sustainable harvest rate, and 
$S$<sub>for,t</sub> is the forest land area.

 Historical data for 2015–2023 are sourced from [Forest Statistics 2025](https://www.gov.ie/en/campaigns/a9d3c-forestry-in-ireland/) with harvest levels linearly extrapolated to 2070. This extrapolated pathway defines the High Harvest (HH) level and represents the upper bound of sustainable roundwood extraction used in TIM-LEAF. Two additional harvest variants are derived from this upper bound: Medium Harvest (MH) at 70% of HH and Low Harvest (LH) at 40% of HH.

#### Afforestation pathways
TIM-LEAF introduces future endogenous afforestation pathways, allowing suitable non-forest land, including wetland and grassland, to be converted to managed forest.
Alternative afforestation pathways can be specified to represent different levels of deployment and policy ambition. The model includes three targets of afforestation: (1) Low afforestation (8,000 ha yr⁻¹ ), medium afforestation (10,650 ha yr⁻¹) and high afforestation (25,000 ha yr⁻¹).

#### Forest carbon dynamics  
To represent the changing sequestration rate of forests as stands mature, a forest age-dependent saturation profile is implemented using the TIMES SHAPE functionality. The sequestration profile follows the Chapman–Richards functional form, a growth model widely used in forestry literature [(Zhao-gang & Feng-ri, 2003)](https://doi.org/10.1007/BF02856757):

$$
S(a) = k a^p e^{-ca}
$$

where $a$ is stand age in years, $k$ is a scaling constant controlling the maximum sequestration rate, $p$ is a shape parameter controlling the early growth trajectory, and $c$ is a decay parameter controlling the decline after the peak.

For simplicity, $p$ is assumed to be 1 in TIM-LEAF. The resulting age-dependent sequestration function is:

$$
S(a) = S_{\max} \left(\frac{a}{a_{\mathrm{peak}}}\right) e^{\left(1-\frac{a}{a_{\mathrm{peak}}}\right)}
$$


####  Harvested wood product carbon storage
HWP carbon storage is modelled using a first-order decay (FOD) formulation, following the IPCC 2019 Refinement Tier 1, FOD, production approach [(Rüter et al., 2019)](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html).
For computational efficiency, sawn wood and wood-based panels are combined into a single `Wood_Products` pool using a weighted effective decay constant:

$$
k_{\mathrm{eff}} = \frac{\sum_l k_l\,\overline{\mathrm{Inflow}}_l}{\sum_l \overline{\mathrm{Inflow}}_l}
$$

where $k_l$ is the decay constant for product category $l$, and $\overline{\mathrm{Inflow}}_l$ is the average annual HWP inflow over 1990–1994 for that product category, expressed in tonnes of carbon (tC).

The aggregated FOD formulation becomes:

$$
C_{\mathrm{total}}(t+1) = C_{\mathrm{total}}(t)e^{-k_{\mathrm{eff}}} + \frac{\mathrm{Inflow}_{\mathrm{total}}(t)}{k_{\mathrm{eff}}}\left(1-e^{-k_{\mathrm{eff}}}\right)
$$

The annual change in the HWP carbon stock is:

$$
\Delta C_{\mathrm{total}}(t) = C_{\mathrm{total}}(t+1) - C_{\mathrm{total}}(t)
$$

where:

$$
\mathrm{Inflow}_{\mathrm{total}}(t) = \mathrm{Inflow}_{\text{sawn wood}}(t) + \mathrm{Inflow}_{\text{wood-based panels}}(t)
$$

The initial HWP stock is reconstructed using historical production data from 1990 to 2017.

#### HWP implementation in TIM-LEAF

 The HWP representation is decomposed into two components: (1) a process-flow representation of carbon inflow and (2) a storage-based representation of carbon decay.

The process-flow component represents the transfer of carbon from harvested wood products into the HWP storage pool. A process-flow efficiency, $\eta_{\mathrm{inflow}}$, is used to represent the fraction of harvested carbon entering the storage pool:

$$
\eta_{\mathrm{inflow}} = \frac{1-e^{-k_{\mathrm{eff}}}}{k_{\mathrm{eff}}}
$$

The remaining carbon is represented as instantaneous HWP carbon emissions, while the stored fraction is transferred to the HWP carbon pool.

The second component represents the gradual decay of carbon stored in HWPs. The annual fraction of carbon remaining in storage is:

$$
e^{-k_{\mathrm{eff}}}
$$

Within the TIMES storage process, `STG_CHRG` defines the initial HWP carbon stock, derived from the reconstructed historical HWP stock, while `STG_LOSS` represents the decay of the stored carbon using the effective decay rate:

$$
k_{\mathrm{eff}}
$$

This structure allows the HWP carbon stock to evolve over time in response to endogenous wood-product flows and the decay of previously stored carbon.

In the model version, **instantaneous HWP carbon emissions associated with harvesting are endogenous** and are therefore included in the model's cumulative carbon-budget constraint. The subsequent annual change in HWP carbon stock is calculated **ex post** from the modelled HWP stock trajectory and is not an endogenous term in the carbon budget constraint.

###  Endogenous bioenergy supply
 Biomass availability from agriculture and forestry is connected directly to the energy system.
Energy crops compete for available land, while forestry biomass is constrained by sustainable harvest potentials. The energy system determines bioenergy demand through the optimisation, while the AFOLU system determines the biomass that can be supplied subject to land, yield, harvest and conversion constraints.

Bioenergy supply is  directly linked to land allocation and forest harvesting within the integrated optimisatio as follows:

$$
ACT^{\mathrm{bio}}_t \leq \eta^{\mathrm{conv}} \left(\sum_{a \in A_{\mathrm{energy}}} \sum_{m \in M} Y_{a,t}\,L_{\mathrm{energy},m,t} + \sum_{f \in F} H^{\max}_{f,t}\right)
$$

where $ACT^{\mathrm{bio}}_{t}$ is the endogenous bioenergy consumption determined by the energy-system optimisation, $Y_{a,t}$ is the biomass yield per hectare of energy crop $a$, $L_{\mathrm{energy},m,t}$ is the land allocated to energy crops on land type $m$, $\eta^{\mathrm{conv}}$ is the biomass-to-energy conversion efficiency and $H^{\max}_{f,t}$ is the maximum sustainable forest harvest.

### Integrated GHG accounting
With its unified structure, TIM-LEAF endogenously accounts for: 
- CO₂ emissions from energy use and industrial processes
- CH₄ and N₂O emissions from agricultural activities
- CO₂, CH₄ and N₂O emissions and removals associated with LULUCF
- Changes in land and forest carbon stocks
- Instantaneous carbon emissions associated with HWP
- CO₂ removals from carbon dioxide removal technologies such as CCS and DACCS.

## Model solution and output
For each scenario, TIM-LEAF identifies the least-cost combination of energy-system transformation, agricultural mitigation, land-use change, forestry, bioenergy and carbon dioxide removal required to satisfy the imposed system constraints.

For scenarios subject to a cumulative carbon budget, the cumulative emissions are given as: 

$$
Net_t = E^{\mathrm{energy}}_t + E^{\mathrm{AFOLU}}_t - \Delta C^{\mathrm{Land}}_t + HWP^{\mathrm{Instant}}_t - CDR_t
$$

where $E^{\mathrm{energy}}_t$ represents CO₂ emissions from fossil-fuel combustion and industrial processes in the energy system, $E^{\mathrm{AFOLU}}_t$ represents CO₂, CH₄ and N₂O emissions from agricultural and land-use activities, $\Delta C^{\mathrm{Land}}_t$ represents changes in land and forest carbon stocks, $HWP^{\mathrm{Instant}}_t$ represents instantaneous carbon emissions from harvested wood products at harvest, and $CDR_t$ represents CO₂ removal from carbon dioxide removal technologies such as CCS and DACCS.

such that the total net emissions satisfies the cumulative carbon-budget constraint: 

$$
\sum_{t \in T} Net_t
\leq
CB
$$

where $CB$ is the imposed cumulative carbon budget over the modelling horizon.

The scenario outputs then include: 
- energy technology and fuel deployment
- land allocation and land use change 
- energy crops production, forest harvesting levels and biomass supply
- land carbon stock changes
- sectoral GHG emissions 
- CDR deployment 

The resulting emissions pathways is then passed to the TIM-LEAF-FaIR workflow, where they are used to evaluate their corresponding temperature responses. 

## TIM-LEAF-FaIR integration
All files associated with the TIM-LEAF-FaIR integration can be found in this [folder](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow).

### Country-level emissions contribution in FaIR
Compiling and running FaIR v 2.1.3 with a `modified fair.py` is documented [here](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/fair_readme.md).

### Running the TIM-LEAF–FaIR workflow
The integrated TIM-LEAF–FaIR workflow consists of running TIM-LEAF, transferring and processing the resulting emissions data and running the FaIR model. The workflow requires [TIM-LEAF model outputs](https://github.com/MaREI-EPMG/TIM-LEAF/tree/main/TIM-LEAF-FaIR_workflow/data/TIM-LEAF_scenarios), the TIM-LEAF–FaIR data transfer script [`data_transfer_from_TIM.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/data_transfer_from_TIM.py), the FaIR script [`countrylevel_IRL.py`](https://github.com/MaREI-EPMG/TIM-LEAF/blob/main/TIM-LEAF-FaIR_workflow/fair/countrylevel_IRL.py) and the required Python dependencies.

### TIM-LEAF to FaIR data transfer
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

## Documentation
More information on the TIMES model generator and specific information about TIM can be found in the [Documentation](https://doi.org/10.5194/gmd-15-4991-2022) and the [repository](https://github.com/MaREI-EPMG/times-ireland-model).

Source code for FaIR v2.1.3  soft linked to TIM-LEAF is available [here](https://github.com/OMS-NetZero/FAIR/releases) under November 23 2023 fair v2.1.3. 

## About the developers
The list of developers and funding is described in the [Acknowledgements](/ACKNOWLEDGEMENT.md) section. 

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

- DAFM. (2025). Forest Statistics Ireland 2025. https://www.gov.ie/en/campaigns/a9d3c-forestry-in-ireland/

- EPA. (2024). Ireland’s National Inventory Report 2024. www.epa.ie

- Leach, N. J., Jenkins, S., Nicholls, Z., Smith, C. J., Lynch, J., Cain, M., Walsh, T., Wu, B., Tsutsui, J., & Allen, M. R. (2021). FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration. Geoscientific Model Development, 14(5), 3007–3036. https://doi.org/10.5194/gmd-14-3007-2021

- Rüter, S., William Matthews, R., Lundblad, M., Sato, A., & Ahmed Hassan, R. (2019). Chapter 12: Harvested Wood Products. In 2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories.

- Smith, C. (2023). FaIR Version 2.1.3. https://doi.org/https://github.com/OMS-NetZero/FAIR/releases

- Smith, C. (2024). FaIR calibration data. https://doi.org/https://doi.org/10.5281/zenodo.10566813

- Teagasc. (2023). Marginal Abatement Cost Curve 2023 Executive Summary 2 Teagasc Marginal Abatement Cost Curve 2023.

- Wheatley, J. (2021, October 6). Ireland greenhouse gas and sulphate aerosol emissions 1745-2019. https://doi.org/https://doi.org/10.5281/zenodo.7004406

- Wheatley, J. (2023). Temperature neutrality and Irish methane policy. Climate Policy, 23(10), 1229–1242. https://doi.org/10.1080/14693062.2023.2191921

- Zhao-gang, L., & Feng-ri, L. (2003). The generalized Chapman-Richards function and applications to tree and stand growth. Journal of Forestry Research, 14(1), 19–26. https://doi.org/10.1007/BF02856757