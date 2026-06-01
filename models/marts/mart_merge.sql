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

SELECT	l.ess11_region_code,
		m.nuts1,
	    m.nuts1_gdp_euro_2022,
	    m.nuts1_gdp_pct_eu27_avg,
	    m.nuts1_unemployment_rate_pct_2022,
	    m.nuts1_net_migration_2022,
	    m.nuts1_pop_density_2022,
	    m.nuts1_pop_growth_rate_2022,
	    r.*
		

FROM respondents r
-- Step 1: Find out where the respondent lives based on their survey code
LEFT JOIN region_lookup l 
    ON r.nuts_region = l.ess11_region_code 
    AND r.country_code = l.country_code

-- Step 2: Bring in the clean NUTS1 stats for that region
LEFT JOIN macro_data m 
    ON l.nuts1 = m.nuts1 
    AND l.country_code = m.country_code
