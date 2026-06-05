WITH source AS (
    SELECT * FROM {{ source('ess_source', 'region_lookup_lean') }}
)

SELECT
    cntry AS country_code,
    "ESS11_reg" AS ess11_region_code, -- The master join key present in the individual survey
    nuts1
FROM source
WHERE cntry IN ('DE', 'IT', 'GR', 'FR', 'ES', 'SE', 'PL') and nuts1 NOT LIKE '%Z'