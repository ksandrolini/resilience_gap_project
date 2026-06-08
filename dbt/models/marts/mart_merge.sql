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
    l.ess11_region_code,
    m.nuts1,
    
    -- 1. ABSOLUTE LEVELS (2022 Structural Baseline Controls)
    m.nuts1_gdp_euro_2022,
    m.nuts1_gdp_pct_eu_avg_2022,
    m.nuts1_unemployment_rate_pct_2022,
    m.nuts1_net_migration_2022,
    m.nuts1_pop_density_2022,
    m.nuts1_pop_growth_rate_2022,
    
    -- 2. CALCULATED DELTAS (Macroeconomic Shocks)
    (m.nuts1_gdp_pct_eu_avg_2022 - m.nuts1_gdp_pct_eu_avg_2017) AS delta_gdp_pct_eu_avg_5yr,
    (m.nuts1_unemployment_rate_pct_2022 - m.nuts1_unemployment_rate_pct_2017) AS delta_unemployment_pct_5yr,
    (m.nuts1_net_migration_2022 - m.nuts1_net_migration_2020) AS delta_net_migration_2yr, -- Controlled 2020 baseline exception
    (m.nuts1_pop_growth_rate_2022 - m.nuts1_pop_growth_rate_2017) AS delta_pop_growth_rate_5yr,

    -- 3. INDIVIDUAL RESPONDENT DATA
    r.*,
    
    -- 4. ANALYTICAL TARGET VARIABLE: BINARY POPULIST VOTE INDICATOR
    case
        -- France
        when r.country_code = 'FR' and vote_fr in (7, 8, 9) then 1 -- Debout la France, Rassemblement National, Reconquete
        when r.country_code = 'FR' and vote_fr is not null then 0

        -- Germany
        when r.country_code = 'DE' and vote_de2 in (6) then 1 -- AfD
        when r.country_code = 'DE' and vote_de2 is not null then 0

        -- Greece
        when r.country_code = 'GR' and vote_gr in (5, 6, 7, 12) then 1 --Ελληνική Λύση (Greek Solution), ΛΑΟΣ (LAOS), Σπαρτιάτες (Spartans) (Not in PopuList), Νίκη (NIKI) (Not in PopuList)
        when r.country_code = 'GR' and vote_gr is not null then 0

        -- Italy
        when r.country_code = 'IT' and vote_it in (1, 4) then 1 -- Fratelli d'Italia, Lega
        when r.country_code = 'IT' and vote_it is not null then 0

        -- Poland
        when r.country_code = 'PL' and vote_pl in (2, 5) then 1 -- PiS, Konfederacja (Not in PopuList)
        when r.country_code = 'PL' and vote_pl is not null then 0

        -- Spain
        when r.country_code = 'ES' and vote_es in (3) then 1 -- VOX
        when r.country_code = 'ES' and vote_es is not null then 0

        -- Sweden
        when r.country_code = 'SE' and vote_se in (8) then 1 -- Sverigedemokraterna
        when r.country_code = 'SE' and vote_se is not null then 0

        -- Safely falls back to NULL for non-voters, blanks, refusals, and other-country rows
        else null
    end as rw_populist_vote

FROM respondents r
-- Step 1: Find out where the respondent lives based on their survey code
LEFT JOIN region_lookup l 
    ON r.nuts_region = l.ess11_region_code 
    AND r.country_code = l.country_code

-- Step 2: Bring in the clean NUTS1 stats for that region
LEFT JOIN macro_data m 
    ON l.nuts1 = m.nuts1 
    AND l.country_code = m.country_code
    