# Mississippi County Health Risk Stratification System

## Project Overview

A data engineering and analytics system that ranks all 82 Mississippi counties by a composite health risk score. The system integrates chronic disease prevalence data from CDC PLACES with social vulnerability indicators from the CDC Social Vulnerability Index (SVI). It identifies high-risk counties, decomposes primary risk drivers per county, and visualizes geographic patterns of health disparity across the state.

The project follows a full data pipeline: raw data ingestion, cleaning, structured SQL database design, analytical queries, composite risk scoring, and visualization.

## Datasets Used

**CDC PLACES (2025 Release)**
- County-level chronic disease prevalence across the United States
- Indicators used: diabetes, obesity, hypertension, COPD
- Filtered to Mississippi's 82 counties
- Source: https://data.cdc.gov

**CDC Social Vulnerability Index (SVI 2022)**
- County-level social and economic vulnerability for Mississippi
- Indicators used: poverty rate, unemployment rate, uninsured rate, no vehicle access, no high school diploma rate, overall SVI score
- Source: https://www.atsdr.cdc.gov

Both datasets are joined on FIPS county codes.

## Key Findings

- Humphreys County ranks highest with a composite risk score of 0.98. Its poverty rate is 56.5% and obesity prevalence is 52.4%.

- 16 of 82 counties meet the dual high-risk threshold: top risk quartile and SVI score above 0.75. These counties are concentrated in the Mississippi Delta and southwest regions.

- Counties in the highest SVI quartile average 20.5% diabetes prevalence compared to 14.5% in the lowest quartile. That is a 42% difference driven entirely by social and economic conditions.

- Social vulnerability is the primary risk driver in 32 of 82 counties, more than any single chronic disease. Obesity-driven counties average the highest composite scores at 0.71.

- Forrest and Lamar counties (Hattiesburg area) fall in the moderate risk range with scores of 0.274 and 0.165, well below the high-risk threshold.

## Composite Risk Score Methodology

Each county is assigned a weighted composite score between 0 and 1:

| Indicator         | Weight | Rationale                                         |
|-------------------|--------|---------------------------------------------------|
| Diabetes rate     | 25%    | Strongest chronic disease burden indicator in MS  |
| Obesity rate      | 20%    | Primary driver of multiple downstream conditions  |
| Hypertension rate | 20%    | Leading cause of stroke and heart disease         |
| SVI score         | 25%    | Captures social determinants of health            |
| COPD rate         | 10%    | Respiratory burden with strong poverty correlation|

Health indicators are min-max normalized to 0-1 before scoring. The SVI
score is used directly as it is already normalized by the CDC.

## Database Schema

| Table                  | Description                                          |
|------------------------|------------------------------------------------------|
| `counties`             | FIPS code, county name, population                   |
| `health_indicators`    | Diabetes, obesity, hypertension, COPD    |
| `social_vulnerability` | Poverty, unemployment, uninsured, SVI score          |
| `risk_scores`          | Composite score, rank, high-risk flag, risk driver   |


## Tools and Technologies

- Python (pandas, matplotlib, geopandas)
- SQLite
- CDC PLACES and CDC SVI public datasets