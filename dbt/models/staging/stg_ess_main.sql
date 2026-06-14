with raw_source as (
    -- Dynamically point to the table declared in src_ess.yml
    select * from {{ source('ess_source', 'ess_main_raw') }}
)

select 

    -- Pass through identifiers and weight untouched
    idno as respondent_id,
    cntry as country_code,
    regunit AS nuts_level, 
    region as nuts_region,
    
    -- Winsorization of model weight
    case when anweight > 5.0 then 5.0 else anweight end as model_analysis_wt,
    
    -- Need to recast 'missing' values as in the ESS they are numeric (e.g. 77, 7777, 9999, etc.). These correspond to different types of missing: refused, don't know, NA, missing.
    -- For models and clustering we will treat as NA
    -- 1. Padded continuous metrics
    case when agea = 999 then null else agea end as age,

    -- 2. 11-point scales (0-10 are valid; 77, 88, 99 become NULL)
    case when ppltrst in (77, 88, 99) then null else ppltrst end as ppltrst,
    case when trstprl in (77, 88, 99) then null else trstprl end as trstprl,
    case when trstlgl in (77, 88, 99) then null else trstlgl end as trstlgl,
    case when trstprt in (77, 88, 99) then null else trstprt end as trst_pol_parties,
    case when trstep in (77, 88, 99) then null else trstep end as trst_euro_parl,
    case when lrscale in (77, 88, 99) then null else lrscale end as left_right_alignment,
    case when euftf in (77, 88, 99) then null else euftf end as eu_role,
    case when stflife in (77, 88, 99) then null else stflife end as sat_life,
    case when stfeco in (77, 88, 99) then null else stfeco end as sat_economy,
    case when stfgov in (77, 88, 99) then null else stfgov end as sat_gov,
    case when stfdem in (77, 88, 99) then null else stfdem end as sat_demo,
    case when imbgeco in (77, 88, 99) then null else imbgeco end as immigration_impact_economy,
    case when imueclt in (77, 88, 99) then null else imueclt end as immigration_impact_culture,
    case when imwbcnt in (77, 88, 99) then null else imwbcnt end as immigrants_impact_country,
    case when atchctr in (77, 88, 99) then null else atchctr end as country_attachment,
    case when atcherp in (77, 88, 99) then null else atcherp end as eur_attachment,
    case when rlgdgr in (77, 88, 99) then null else rlgdgr end as how_religious,
    case when hinctnta in (77, 88, 99) then null else hinctnta end as hh_income_decile,

    -- 3. Human Values Scale (1-6 are valid; 77, 88, 99 become NULL)
    case when ipeqopta in (77, 88, 99) then null else ipeqopta end as imp_treat_ppl_equally,
    case when ipudrsta in (77, 88, 99) then null else ipudrsta end as imp_understand_diff_ppl,
    case when ipstrgva in (77, 88, 99) then null else ipstrgva end as imp_govt_strength,

    -- 4. Short ordinal/binary scales (7, 8, 9 become NULL)
    case when polintr in (7, 8, 9) then null else polintr end as polintr,
    case when psppsgva in (7, 8, 9) then null else psppsgva end as personal_say_govt,
    case when psppipla in (7, 8, 9) then null else psppipla end as personal_influence_politics,
    case when vote in (7, 8, 9) then null else vote end as vote_yn,
    case when gincdif in (7, 8, 9) then null else gincdif end as govt_role_income_inequality,
    case when imdfetn in (7, 8, 9) then null else imdfetn end as allow_diverse_immigrants,
    case when ctzcntr in (7, 8, 9) then null else ctzcntr end as citizen,
    case when feethngr in (7, 8, 9) then null else feethngr end as identify_ethnic_majority,
    case when uemp12m in (7, 8, 9) then null else uemp12m end as unemp_over_12_mos_ever,
    case when uemp5yr in (7, 8, 9) then null else uemp5yr end as unemp_last_5_years,
    case when hincfel in (7, 8, 9) then null else hincfel end as hh_income_comfort,
	case
	    when gndr = 1 then 0
	    when gndr = 2 then 1
	    else null
	end as gender, -- recode to 0/1 binary
	
    -- 5. Education Scales (0 'impossible to standardize', 55 is "Other", 77, 88, 99 are missing)
    case when eisced in (0, 55, 77, 88, 99) then null else eisced end as educ_attainment,
    case when eiscedf in (0, 55, 77, 88, 99) then null else eiscedf end as educ_attainment_father,
    case when eiscedm in (0, 55, 77, 88, 99) then null else eiscedm end as educ_attainment_mother,

 -- 6. Voting Blocks (66 is Country Omission, 77, 88, 99 are missing)
    -- France
    case 
        when nullif(trim(prtvtffr::varchar), '')::int in (10, 11, 66, 77, 88, 99) then null 
        else nullif(trim(prtvtffr::varchar), '')::int 
    end as vote_fr,

    -- Germany (Party List)
    case 
        when nullif(trim(prtvgde2::varchar), '')::int in (66, 77, 88, 99) then null 
        else nullif(trim(prtvgde2::varchar), '')::int 
    end as vote_de2,

    -- Greece
    case 
        when nullif(trim(prtvtegr::varchar), '')::int in (32, 33, 66, 77, 88, 99) then null 
        else nullif(trim(prtvtegr::varchar), '')::int 
    end as vote_gr,

    -- Italy
    case 
        when nullif(trim(prtvteit::varchar), '')::int in (66, 77, 88, 99) then null 
        else nullif(trim(prtvteit::varchar), '')::int 
    end as vote_it,

    -- Poland
    case 
        when nullif(trim(prtvtfpl::varchar), '')::int in (66, 77, 88, 99) then null 
        else nullif(trim(prtvtfpl::varchar), '')::int 
    end as vote_pl,

    -- Spain
    case 
        when nullif(trim(prtvtges::varchar), '')::int in (51, 52, 66, 77, 88, 99) then null 
        else nullif(trim(prtvtges::varchar), '')::int 
    end as vote_es,

    -- Sweden
    case 
        when nullif(trim(prtvtese::varchar), '')::int in (66, 77, 88, 99) then null 
        else nullif(trim(prtvtese::varchar), '')::int 
    end as vote_se,
 
 	-- CATEGORICAL BEHAVIORAL VOTING FLAG
    case
        ---------------------------------------------------------
        -- FRANCE (prtvtffr)
        ---------------------------------------------------------
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  = 10 then 'Blank Ballot'
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  = 11 then 'Invalid Ballot'
        when cntry = 'FR' and nullif(trim(prtvtffr::varchar), '')::int  is not null then 'Valid Party Vote'

        ---------------------------------------------------------
        -- GERMANY (prtvgde2)
        ---------------------------------------------------------
        when cntry = 'DE' and nullif(trim(prtvgde2::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'DE' and nullif(trim(prtvgde2::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'DE' and nullif(trim(prtvgde2::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'DE' and nullif(trim(prtvgde2::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'DE' and nullif(trim(prtvgde2::varchar), '')::int  is not null then 'Valid Party Vote'

        ---------------------------------------------------------
        -- GREECE (prtvtegr)
        ---------------------------------------------------------
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  = 33 then 'Blank Ballot'
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  = 32 then 'Invalid Ballot'
        when cntry = 'GR' and nullif(trim(prtvtegr::varchar), '')::int  is not null then 'Valid Party Vote'

        ---------------------------------------------------------
        -- ITALY (prtvteit)
        ---------------------------------------------------------
        when cntry = 'IT' and nullif(trim(prtvteit::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'IT' and nullif(trim(prtvteit::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'IT' and nullif(trim(prtvteit::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'IT' and nullif(trim(prtvteit::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'IT' and nullif(trim(prtvteit::varchar), '')::int  is not null then 'Valid Party Vote'

        ---------------------------------------------------------
        -- SPAIN (prtvtges)
        ---------------------------------------------------------
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  = 51 then 'Blank Ballot'
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  = 52 then 'Invalid Ballot'
        when cntry = 'ES' and nullif(trim(prtvtges::varchar), '')::int  is not null then 'Valid Party Vote'

        ---------------------------------------------------------
        -- SWEDEN (prtvtese)
        ---------------------------------------------------------
        when cntry = 'SE' and nullif(trim(prtvtese::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'SE' and nullif(trim(prtvtese::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'SE' and nullif(trim(prtvtese::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'SE' and nullif(trim(prtvtese::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'SE' and nullif(trim(prtvtese::varchar), '')::int  is not null then 'Valid Party Vote'

        ---------------------------------------------------------
        -- POLAND (prtvtfpl)
        ---------------------------------------------------------
        when cntry = 'PL' and nullif(trim(prtvtfpl::varchar), '')::int  = 66 then 'Ineligible / Not Applicable'
        when cntry = 'PL' and nullif(trim(prtvtfpl::varchar), '')::int  = 77 then 'Refuse to Say'
        when cntry = 'PL' and nullif(trim(prtvtfpl::varchar), '')::int  = 88 then 'Don''t Know'
        when cntry = 'PL' and nullif(trim(prtvtfpl::varchar), '')::int  = 99 then 'No Answer / System Missing'
        when cntry = 'PL' and nullif(trim(prtvtfpl::varchar), '')::int  is not null then 'Valid Party Vote'

        -- Catch-all for any weird outliers or system gaps
        else 'System Skip / Undefined'
    end as voting_behavior_manifest  
    
from raw_source
where idno is not null and cntry in ('DE', 'FR', 'IT', 'PL', 'ES', 'SE', 'GR') and region NOT LIKE '%Z' -- NUTS _Z regions are small 'other' subset for people with special residential status (diplomats, army bases, etc.)

