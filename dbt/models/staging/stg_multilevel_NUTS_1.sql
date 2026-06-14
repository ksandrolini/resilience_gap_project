with source as (
    select * from {{ source('ess_source', 'ess_multilevel_nuts1') }}
),

renamed_and_filtered as (
    select
        cntry as country_code,
        nuts1,
     	-- 2017 macro indicators (economic anxiety, migration, demographics)
        n1_gdp_eurhab_2017 as nuts1_gdp_euro_2017,
        n1_gdp_eurhab_eu27_2020_2017 as nuts1_gdp_pct_eu_avg_2017,
        n1_unraall_2017 as nuts1_unemployment_rate_pct_2017,
        n1_pode_2017 as nuts1_pop_density_2017,
        n1_growrt_2017 as nuts1_pop_growth_rate_2017,
        
        -- one exception, data not available for all countries in 2017, need to use 2020
        n1_cnmigratrt_2020 as nuts1_net_migration_2020,

        -- 2022 macro indicators
        n1_gdp_eurhab_2022 as nuts1_gdp_euro_2022,
        n1_gdp_eurhab_eu27_2020_2022 as nuts1_gdp_pct_eu_avg_2022,
        n1_unraall_2022 as nuts1_unemployment_rate_pct_2022,        
        n1_pode_2022 as nuts1_pop_density_2022,
        n1_growrt_2022 as nuts1_pop_growth_rate_2022,
        n1_cnmigratrt_2022 as nuts1_net_migration_2022

    from source
    -- Geographic Scope Filter
    where cntry in ('DE', 'IT', 'GR', 'FR', 'ES', 'SE', 'PL') and nuts1 NOT LIKE '%Z'
)

select * from renamed_and_filtered
