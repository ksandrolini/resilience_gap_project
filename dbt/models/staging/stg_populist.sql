with raw_source as (
    -- Dynamically point to the table declared in src_ess.yml
    select * from {{ source('ess_source', 'the_populist') }}
)
select party_name, country_name, party_name_english, party_name_short, populist, farright
from raw_source
where country_name in ('Bulgaria', 'Finland', 'France', 'Germany', 'Greece', 'Italy', 'Poland', 'Portugal', 'Spain', 'Sweden') AND farright = 1