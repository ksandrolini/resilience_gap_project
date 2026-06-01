with source as (
    select * from {{ source('ess_source', 'ess_multilevel_nuts1') }}
),

renamed_and_filtered as (
    select
        -- Identifiers
        cntry as country_code,
        nuts1,
        
        -- 2022 macro indicators (economic anxiety, migration, demographics)
        n1_gdp_eurhab_2022 as nuts1_gdp_euro_2022,
        n1_gdp_eurhab_eu27_2020_2022 as nuts1_gdp_pct_eu27_avg,
        n1_cnmigratrt_2022 as nuts1_net_migration_2022,
        n1_pode_2022 as nuts1_pop_density_2022,
        n1_growrt_2022 as nuts1_pop_growth_rate_2022,
        n1_unraall_2022 as nuts1_unemployment_rate_pct_2022


    from source
    -- Geographic Scope Filter
    where cntry in ('DE', 'IT', 'GB', 'FR', 'ES', 'SE', 'PL')
)

select * from renamed_and_filtered
