{{ config(
    materialized='table'
) }}

WITH respondents AS (
    SELECT * FROM {{ ref('stg_ess_main') }}
),
nuts1_data AS (
    SELECT * FROM {{ ref('stg_multilevel_NUTS_1') }}
)

SELECT
    -- 1. IDS / STRUCTURE
    m.nuts1 AS nuts1_region,
    r.country_code,
    r.nuts_region,
    r.respondent_id,
    r.model_analysis_wt,

    -- 2. MACRO STRUCTURAL CONTEXT (ABSOLUTE LEVELS) & DELTAS
    
    -- NUTS 1
    m.nuts1_gdp_percap_pps_2022,
    m.nuts1_gdp_percap_pps_pct_eu_avg_2022,
    m.nuts1_unemployment_rate_pct_2022,
    m.nuts1_net_migration_2022,
        
    (m.nuts1_gdp_percap_pps_2022 - m.nuts1_gdp_percap_pps_2017)
        AS delta_nuts1_gdp_percap_pps_euro_5yr,
        
    (m.nuts1_gdp_percap_pps_pct_eu_avg_2022 - m.nuts1_gdp_percap_pps_pct_eu_avg_2017)
        AS delta_nuts1_gdp_percap_pps_pct_eu_avg_5yr,

    (m.nuts1_unemployment_rate_pct_2022 - m.nuts1_unemployment_rate_pct_2017)
        AS delta_nuts1_unemployment_rate_5yr,

    (m.nuts1_net_migration_2022 - m.nuts1_net_migration_2020)
        AS delta_nuts1_net_migration_2yr,

     
    -- 4. INDIVIDUAL SOCIOECONOMIC CONTROLS
    r.age,
    r.gender,
    r.educ_attainment,
    r.hh_income_comfort,
    r.unemp_last_5_years,


	-- TRUST COMPONENTS (To be collapsed into index in Python)
    r.trstprl,
    r.trstlgl,
    r.trst_pol_parties,
    r.ppltrst,

    -- 6. CULTURAL ATTITUDES
    r.immigrants_impact_country,
    r.left_right_alignment,

    -- 7. VALUES / DIAGNOSTICS
    r.voting_behavior_manifest,

    -- 8. DERIVED MOBILITY
    r.educ_attainment - greatest(r.educ_attainment_mother, r.educ_attainment_father) 
        AS intergen_educational_mobility,

    -- 9. TARGET VARIABLE
    CASE
	    
	    WHEN r.country_code = 'BG' AND r.vote_bg IN (6, 8) THEN 1
        WHEN r.country_code = 'BG' AND r.vote_bg IS NOT NULL THEN 0
        
        WHEN r.country_code = 'FI' AND r.vote_fi IN (8, 15, 20, 21, 22) THEN 1
        WHEN r.country_code = 'FI' AND r.vote_fi IS NOT NULL THEN 0
        
        WHEN r.country_code = 'FR' AND r.vote_fr IN (7,8,9) THEN 1
        WHEN r.country_code = 'FR' AND r.vote_fr IS NOT NULL THEN 0

        WHEN r.country_code = 'DE' AND r.vote_de2 IN (6) THEN 1
        WHEN r.country_code = 'DE' AND r.vote_de2 IS NOT NULL THEN 0

        WHEN r.country_code = 'GR' AND r.vote_gr IN (5,6,7,12) THEN 1
        WHEN r.country_code = 'GR' AND r.vote_gr IS NOT NULL THEN 0

        WHEN r.country_code = 'IT' AND r.vote_it IN (1,4,9,11) THEN 1
        WHEN r.country_code = 'IT' AND r.vote_it IS NOT NULL THEN 0

        WHEN r.country_code = 'PL' AND r.vote_pl IN (5) THEN 1
        WHEN r.country_code = 'PL' AND r.vote_pl IS NOT NULL THEN 0

        WHEN r.country_code = 'PT' AND r.vote_pt IN (2,5,6) THEN 1
        WHEN r.country_code = 'PT' AND r.vote_pt IS NOT NULL THEN 0
        
        WHEN r.country_code = 'ES' AND r.vote_es IN (3) THEN 1
        WHEN r.country_code = 'ES' AND r.vote_es IS NOT NULL THEN 0

        WHEN r.country_code = 'SE' AND r.vote_se IN (8) THEN 1
        WHEN r.country_code = 'SE' AND r.vote_se IS NOT NULL THEN 0

        ELSE NULL
    END AS radical_right_vote

FROM respondents r

LEFT JOIN nuts1_data m
    ON SUBSTRING(r.nuts_region, 1, 3) = m.nuts1
    AND r.country_code = m.country_code