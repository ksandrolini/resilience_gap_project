with source as (
    select * from {{ source('ess_source', 'ess_multilevel_nuts1') }}
),

renamed_and_filtered as (
    select
        cntry as country_code,
        nuts1,
     	-- Baseline macro indicators (economic anxiety, migration, demographics).
        n1_gdp_pps_eu27_2020_hab_2017 AS nuts1_gdp_percap_pps_2017,
        n1_gdp_pps_hab_eu27_2020_2017 AS nuts1_gdp_percap_pps_pct_eu_avg_2017,
        n1_unraall_2017 as nuts1_unemployment_rate_pct_2017,
        n1_cnmigratrt_2020 as nuts1_net_migration_2020, -- one exception, data not available for all countries in 2017, need to use 2020


        -- 2022 macro indicators
        n1_gdp_pps_eu27_2020_hab_2022 AS nuts1_gdp_percap_pps_2022,
        n1_gdp_pps_hab_eu27_2020_2022 AS nuts1_gdp_percap_pps_pct_eu_avg_2022,
        n1_unraall_2022 as nuts1_unemployment_rate_pct_2022,        
        n1_cnmigratrt_2022 as nuts1_net_migration_2022

    from source
    -- Geographic Scope Filter
    where cntry in ('BG', 'DE', 'FI', 'FR', 'GR', 'IT', 'PL', 'PT', 'ES', 'SE') and nuts1 NOT LIKE '%Z'
)

select * from renamed_and_filtered
