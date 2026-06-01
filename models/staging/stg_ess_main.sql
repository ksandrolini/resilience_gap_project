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
    
    
    -- Survey Weights (Crucial for getting accurate aggregates later)
    dweight as design_wt,
    pspwght as post_stratification_wt,
    pweight as pop_size_wt,
    anweight as analysis_wt,

    -- News, politics, current affairs
    nwspol as news_pol_CA_mins_daily,
    netustm as internet_use_mins_daily,
    polintr,
    psppsgva as personal_say_govt,
    psppipla as personal_influence_politics,
    pstplonl as post_online_pol_last_yr,

    -- Trust vars
    ppltrst,
    pplfair,
    pplhlp,
    trstprl,
    trstlgl,
    trstplt as trst_pols,
    trstprt as trst_pol_parties,
    trstep as trt_euro_parl,
    trstun,

    -- Voting vars
    vote as vote_yn,
    prtvtffr as vote_fr,
    prtvgde1 as vote_de1,
    prtvgde2 as vote_de2,
    prtvteit as vote_it,
    prtvtfpl as vote_pl,
    prtvtges as vote_es,
    prtvtese as vote_se,
    prtvtdgb as vote_gb,
    lrscale as left_right_alignment,
    euftf as eu_role,

    -- Satisfaction
    stflife as sat_life,
    stfeco as sat_economy,
    stfgov as sat_gov,
    stfdem as sat_demo,
    stfedu as sat_educ,
    stfhlth as sat_health,

    -- Income
    gincdif as govt_role_income_inequality,

    -- Immigration
    imdfetn as allow_diverse_immigrants,
    imsmetn as allow_same_ethnic_immigrants,
    impcntr as allow_poorer_immigrants,
    imbgeco as immigration_impact_economy,
    imueclt as immigration_impact_culture,
    imwbcnt as immigrants_impact_country,

    -- Personal / demographic
    happy,
    dscrgrp as personal_discrim_against,
    ctzcntr as citizen,
    feethngr as identify_ethnic_majority,
    gndr as gender,
    agea as age,
    agegroup,

    -- Values
    atchctr as country_attachment,
    atcherp as eur_attachment,
    rlgblg as religious,
    rlgdgr as how_religious,
    ipeqopta as imp_treat_ppl_equally,
    ipudrsta as imp_understand_diff_ppl,
    ipstrgva as imp_govt_strength,

    -- Educational attainment
    eisced as educ_attainment,
    eduyrs as educ_years_completed,

    -- Employment / income
    uemp3m as unemp_over_3_mos_ever,
    uemp12m as unemp_over_12_mos_ever,
    uemp5yr as unemp_last_5_years,
    hinctnta as hh_income_decile,
    hincfel as hh_income_comfort,
    atncrse as skills_course_last_year,

    -- Socioeconomic Mobility
    eiscedf as educ_attainment_father,
    eiscedm as educ_attainment_mother


from raw_source
where idno is not null and cntry in ('DE', 'FR', 'IT', 'PL', 'ES', 'SE', 'GB')
