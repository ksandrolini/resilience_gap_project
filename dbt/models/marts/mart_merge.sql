{{ config(
    materialized='table'
) }}

WITH respondents AS (
    SELECT * FROM {{ ref('stg_ess_main') }}
),

region_lookup AS (
    SELECT * FROM {{ ref('stg_multilevel_region_lookup') }}
),

macro_data AS (
    SELECT * FROM {{ ref('stg_multilevel_NUTS_1') }}
)

SELECT
    -- 1. IDS / STRUCTURE
    m.nuts1 AS nuts1_region,
    r.country_code,
    r.nuts_region,
    r.respondent_id,
    r.model_analysis_wt,

    -- 2. MACRO STRUCTURAL CONTEXT (ABSOLUTE LEVELS)
    m.nuts1_gdp_euro_2022,
    m.nuts1_gdp_pct_eu_avg_2022,
    m.nuts1_unemployment_rate_pct_2022,
    m.nuts1_net_migration_2022,
    m.nuts1_pop_density_2022,
    m.nuts1_pop_growth_rate_2022,

    -- 3. MACRO SHOCKS (DELTAS)
    (m.nuts1_gdp_pct_eu_avg_2022 - m.nuts1_gdp_pct_eu_avg_2017)
        AS delta_nuts1_gdp_pct_eu_avg_5yr,

    (m.nuts1_unemployment_rate_pct_2022 - m.nuts1_unemployment_rate_pct_2017)
        AS delta_nuts1_unemployment_rate_5yr,

    (m.nuts1_net_migration_2022 - m.nuts1_net_migration_2020)
        AS delta_nuts1_net_migration_2yr,

    (m.nuts1_pop_growth_rate_2022 - m.nuts1_pop_growth_rate_2017)
        AS delta_nuts1_pop_growth_rate_5yr,

    -- 4. INDIVIDUAL SOCIOECONOMIC CONTROLS
    r.age,
    r.gender,
    r.citizen,
    r.identify_ethnic_majority,
    r.educ_attainment,
    r.hh_income_comfort,
    r.unemp_last_5_years,
    r.how_religious,

    -- 5. POLITICAL MECHANISMS
    r.personal_say_govt,
    r.eu_role,
    r.country_attachment,
    r.eur_attachment,

	-- TRUST COMPONENTS (To be collapsed into index in Python)
    r.trstprl,
    r.trstlgl,
    r.trst_pol_parties,
    r.ppltrst,

    -- 6. CULTURAL ATTITUDES
    r.immigrants_impact_country,
    r.govt_role_income_inequality,
    r.left_right_alignment,

    -- 7. VALUES / DIAGNOSTICS
    r.sat_life,
    r.voting_behavior_manifest,

    -- 8. DERIVED MOBILITY
    r.educ_attainment - greatest(r.educ_attainment_mother, r.educ_attainment_father) 
        AS intergen_educational_mobility,

    -- 9. TARGET VARIABLE
    CASE
        WHEN r.country_code = 'FR' AND r.vote_fr IN (7,8,9) THEN 1
        WHEN r.country_code = 'FR' AND r.vote_fr IS NOT NULL THEN 0

        WHEN r.country_code = 'DE' AND r.vote_de2 IN (6) THEN 1
        WHEN r.country_code = 'DE' AND r.vote_de2 IS NOT NULL THEN 0

        WHEN r.country_code = 'GR' AND r.vote_gr IN (5,6,7,12) THEN 1
        WHEN r.country_code = 'GR' AND r.vote_gr IS NOT NULL THEN 0

        WHEN r.country_code = 'IT' AND r.vote_it IN (1,4) THEN 1
        WHEN r.country_code = 'IT' AND r.vote_it IS NOT NULL THEN 0

        WHEN r.country_code = 'PL' AND r.vote_pl IN (2,5) THEN 1
        WHEN r.country_code = 'PL' AND r.vote_pl IS NOT NULL THEN 0

        WHEN r.country_code = 'ES' AND r.vote_es IN (3) THEN 1
        WHEN r.country_code = 'ES' AND r.vote_es IS NOT NULL THEN 0

        WHEN r.country_code = 'SE' AND r.vote_se IN (8) THEN 1
        WHEN r.country_code = 'SE' AND r.vote_se IS NOT NULL THEN 0

        ELSE NULL
    END AS rw_populist_vote

FROM respondents r

LEFT JOIN region_lookup l
    ON r.nuts_region = l.ess11_region_code
    AND r.country_code = l.country_code

LEFT JOIN macro_data m
    ON l.nuts1 = m.nuts1
    AND l.country_code = m.country_code
    