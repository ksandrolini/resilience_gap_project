with raw_source as (
    -- Dynamically point to the table declared in src_ess.yml
    select * from {{ source('ess_source', 'ess_main_raw') }}
)

select
    -- Core Demographics & Geography
    idno as respondent_id,
    cntry as country_code,
    regunit AS nuts_level,
    region AS nuts_region,
    
    
    -- Survey Weights
    dweight as design_wt,
    pspwght as post_stratification_wt,
    pweight as pop_size_wt,
    anweight as analysis_wt,

    -- News, politics, current affairs
    nwspol as news_pol_CA_mins_daily,
    polintr,
    psppsgva as personal_say_govt,
    psppipla as personal_influence_politics,

    -- Systemic trust vectors
    ppltrst,
    trstprl,
    trstlgl,
    trstprt as trst_pol_parties,
    trstep as trst_euro_parl,

    -- Voting and ideology
    vote as vote_yn,
    prtvtffr as vote_fr,
    prtvgde2 as vote_de2, -- Germany has a 2 vote system, use the second (proportional party list vote) as it is more comparable
    prtvtegr as vote_gr,
    prtvteit as vote_it,
    prtvtfpl as vote_pl,
    prtvtges as vote_es,
    prtvtese as vote_se,
    lrscale as left_right_alignment,
    euftf as eu_role,

    -- Satisfaction
    stflife as sat_life,
    stfeco as sat_economy,
    stfgov as sat_gov,
    stfdem as sat_demo,

    -- Policy and macro attitudes
    gincdif as govt_role_income_inequality,
    imdfetn as allow_diverse_immigrants,
    imbgeco as immigration_impact_economy,
    imueclt as immigration_impact_culture,
    imwbcnt as immigrants_impact_country,

    -- Personal / demographic
    ctzcntr as citizen,
    feethngr as identify_ethnic_majority,
    gndr as gender,
    agea as age,

    -- Values
    atchctr as country_attachment,
    atcherp as eur_attachment,
    rlgdgr as how_religious,
    ipeqopta as imp_treat_ppl_equally,
    ipudrsta as imp_understand_diff_ppl,
    ipstrgva as imp_govt_strength,

    -- Employment / income
    uemp12m as unemp_over_12_mos_ever,
    uemp5yr as unemp_last_5_years,
    hinctnta as hh_income_decile,
    hincfel as hh_income_comfort,

    -- Socioeconomic Mobility
    eisced as educ_attainment,
    eiscedf as educ_attainment_father,
    eiscedm as educ_attainment_mother


from raw_source
where idno is not null and cntry in ('DE', 'FR', 'IT', 'PL', 'ES', 'SE', 'GR') and region NOT LIKE '%Z'
