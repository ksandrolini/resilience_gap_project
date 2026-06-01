with raw_source as (
    -- This dynamically points to the table we declared in src_ess.yml
    select * from {{ source('ess_source', 'ess_main_raw') }}
)

select
    -- Core Demographics & Geography
    idno as respondent_id,
    cntry as country_code,
    essround as ess_round,
    edition as survey_edition,
    proddate as production_date,
    
    -- Survey Weights (Crucial for getting accurate aggregates later)
    dweight as design_weight,
    pspwght as post_stratification_weight

from raw_source
where idno is not null
