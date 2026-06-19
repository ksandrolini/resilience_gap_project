import json
import urllib.request
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Global CSS to boost readability for presentations
st.markdown(
    """
    <style>
    html, body, p, li {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    h3 { font-size: 30px !important; }
    h2 { font-size: 36px !important; }
    h1 { font-size: 44px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(layout="wide")

# =====================================================================
# DATA PIPELINE LAYER
# =====================================================================
@st.cache_data
def load_hierarchical_data():
    ACTIVE_K = 6
    CLUSTER_COL = f"cluster_k{ACTIVE_K}"

    df_reg = pd.read_csv("dashboard_regional_data.csv")
    df_ind = pd.read_csv("dashboard_individual_data.csv")
    reg_sum = pd.read_csv("regression_summary_1.csv")

    df_reg["nuts1_region"] = df_reg["nuts1_region"].str.strip().str.upper()
    df_ind["nuts1_region"] = df_ind["nuts1_region"].str.strip().str.upper()

    CLUSTER_LABELS = {
        0: "Economically Deprived Periphery",
        1: "Affluent Established Radical Right Presence",
        2: "High Migration Low Backlash Regions",
        3: "Vulnerable Battlegrounds",
        4: "Alienated and Educated Skeptics",
        5: "Status Quo Powerhouses"
    }

    df_reg["typology_name"] = df_reg[CLUSTER_COL].map(CLUSTER_LABELS)

    if CLUSTER_COL not in df_ind.columns:
        df_ind = df_ind.merge(
            df_reg[["nuts1_region", CLUSTER_COL]],
            on="nuts1_region",
            how="left",
            validate="m:1"
        )

    df_ind["typology_name"] = df_ind[CLUSTER_COL].map(CLUSTER_LABELS)

    return df_reg, df_ind, reg_sum


@st.cache_data
def load_geojson():
    url = (
        "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
        "NUTS_RG_60M_2021_4326_LEVL_1.geojson"
    )
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())


def to_3_sig_fig(val):
    if pd.isna(val) or val == 0:
        return "0.00"
    try:
        return f"{float(f'{val:.3g}')}"
    except (ValueError, TypeError):
        return "N/A"


df_regions, df_individuals, reg_summary = load_hierarchical_data()
nuts1_geojson = load_geojson()

CLUSTER_LABELS = {
    0: "Economically Deprived Periphery",
    1: "Affluent Established Radical Right Presence",
    2: "High Migration Low Backlash Regions",
    3: "Vulnerable Battlegrounds",
    4: "Alienated and Educated Skeptics",
    5: "Status Quo Powerhouses"
}

CLUSTER_COLORS = {
    0: "#4C78A8",
    1: "#F58518",
    2: "#54A24B",
    3: "#E45756",
    4: "#B279A2",
    5: "#76B7B2"
}

FOCUSED_GEO_LAYOUT = dict(
    scope="europe",
    projection_type="natural earth",
    showlakes=True,
    lakecolor="rgb(255, 255, 255)",
    lonaxis_range=[-12, 35],
    lataxis_range=[34, 71],
)

# =====================================================================
# SIDEBAR NAVIGATION
# =====================================================================
# 1. CSS Injection: Resizes the sidebar to be tighter and narrower (e.g., 260px)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 250px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("🇪🇺 The Multilevel Bridge")
section = st.sidebar.radio(
    "Navigate",
    [
        "Introduction",
        "Theory & Approach",
        "Macro Environment Visuals",
        "Individual-Level GLM Model",
        "Regional Structural Typology",
        "Key Findings",
        "Scope & Limitations",
        "Data Sources & Attributions",
    ]
)

# =====================================================================
# SECTION: INTRODUCTION
# =====================================================================
if section == "Introduction":
    st.title("What Drives Far-Right Voting?")
    st.subheader("Attitudes, Economics, or Something Else?")

    st.markdown(
        """
        Support for radical-right parties has grown across Europe, but there is still considerable disagreement about why.

        Is it driven by economic hardship? Immigration pressures? Declining trust in political institutions? Or does the answer depend on where people live?

        Using European Social Survey data from **10 European countries**, this project compares individual attitudes with regional economic conditions to identify which factors are most closely associated with radical-right voting.

        ### What This Project Examines

        * 🗺️ **Regional Context:** GDP growth, unemployment, migration, and voting patterns across European regions.
        * 👤 **Individual Attitudes:** Trust in institutions, views on immigration, education, age, and gender.
        * 🔍 **Regional Typologies:** A data-driven clustering approach that groups regions with similar economic and demographic characteristics.

        ### Why Does It Matter? 🤌🏽🤌🏽🤌🏽

        Governments often respond to political discontent based on assumptions about what is causing it. If those assumptions are wrong, policies may target the wrong problems.

        This project tests competing explanations to better understand what actually drives radical-right voting across Europe.
        """
    )


# =====================================================================
# SECTION: FOUNDATIONS, COUNTRIES & PIPELINE
# =====================================================================
elif section == "Theory & Approach":
    st.header("Project Foundations: Pressure-Testing the Literature")
    st.markdown(
        "Before diving into the data, we ground the analysis in the political sociology "
        "literature. What actually drives right-wing voting behavior? Scholars are divided into "
        "two primary camps."
    )

    tab1, tab2 = st.tabs([
        "1. Economic & Structural Accounts (Kriesi; Papaioannou & Guriev)",
        "2. Cultural Backlash (Inglehart & Norris)"
    ])

    with tab1:
        st.subheader("Economic Structure and Shock: Two Versions of the Same Mechanism")
        st.markdown("**Core Argument:** Material conditions — whether a slow-moving structural divide or a sudden shock — drive political realignment.")
        st.info(
            "**Kriesi's globalization 'losers' thesis** argues that modernization creates structural 'winners' "
            "(highly educated, mobile, urban citizens) and 'losers' (less-educated, tradition-bound, localized workers). "
            "Right-wing populists mobilize the latter group, who feel economically and culturally left behind.\n\n"
            "**Guriev and Papaioannou's shock thesis** extends this to acute disruption: sudden economic "
            "deterioration (the 2008 crash, austerity, rapid regional job losses) strains the democratic contract. "
            "When conditions deteriorate sharply, trust erodes and anti-establishment voting follows. "
            "Both accounts share a common logic — economic dislocation, whether gradual or sudden, is the primary driver."
        )

    with tab2:
        st.subheader("The Cultural Backlash Thesis")
        st.markdown("**Core Argument:** Populism is not primarily driven by economic pocketbooks, but by a value-based reaction.")
        st.warning(
            "As Western societies shifted rapidly toward progressive, cosmopolitan, and multicultural values, "
            "older and socially conservative demographics experienced a perceived status threat, contributing to a "
            "defensive nationalist and nativist political backlash."
        )

        st.markdown("---")

        st.header("Country Case Selection Matrix")
        st.markdown(
            "I use **European Social Survey (ESS Round 11)** data "
            "to test which explanation holds the most predictive weight. To capture a comprehensive picture of European political and economic dynamics, "
            "the project targets **ten distinct nations** chosen to provide variation "
            "across institutional models, welfare traditions, and structural vulnerabilities."
        )

    st.markdown(
        """
        <table style="width:100%; border-collapse: collapse; margin-top: 15px; font-family: inherit;">
            <thead>
                <tr style="border-bottom: 2px solid #4a5568; text-align: left;">
                    <th style="padding: 12px; width: 20%; font-size: 16px;">Country</th>
                    <th style="padding: 12px; width: 80%; font-size: 16px;">Strategic Institutional Profile</th>
                </tr>
            </thead>
            <tbody>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇸🇪 Sweden</td>
                <td style="padding: 12px; line-height: 1.5;">High-trust Nordic model, comprehensive social welfare state.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇩🇪 Germany</td>
                <td style="padding: 12px; line-height: 1.5;">Large coordinated market economy, strong manufacturing core, major continental migration destination.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇫🇷 France</td>
                <td style="padding: 12px; line-height: 1.5;">Highly centralized state tradition, high structural political dissatisfaction despite strong institutions.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇮🇹 Italy</td>
                <td style="padding: 12px; line-height: 1.5;">Long-term economic stagnation, deep regional inequality, history of institutional populism.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇪🇸 Spain</td>
                <td style="padding: 12px; line-height: 1.5;">Post-crisis structural recovery case, high youth unemployment, volatile and shifting political dynamics.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇬🇷 Greece</td>
                <td style="padding: 12px; line-height: 1.5;">Extreme macro-economic shock case following the sovereign debt crisis and subsequent structural adjustments.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇵🇱 Poland</td>
                <td style="padding: 12px; line-height: 1.5;">Post-socialist economic success story alongside an entrenched right-populist movement.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇵🇹 Portugal</td>
                <td style="padding: 12px; line-height: 1.5;">Southern European peripheral economy with distinct post-crisis labor market adjustments.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇫🇮 Finland</td>
                <td style="padding: 12px; line-height: 1.5;">Nordic welfare archetype facing demographic pressures and recent shifts in right-populist alignment.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px; font-weight: bold; white-space: nowrap;">🇧🇬 Bulgaria</td>
                <td style="padding: 12px; line-height: 1.5;">Post-socialist transition economy navigating demographic contraction and institutional resilience challenges.</td>
            </tr>
        </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.header("The Data Pipeline & Stack")
    st.write("")

    col_left, col_mid, col_right = st.columns([0.20, 0.60, 0.20])
    with col_mid:
        st.image(
            "data_stack.jpeg",
            caption="End-to-End Analytical Data Pipeline: From Raw Survey Data to Interactive Dashboard",
            use_container_width=True
        )

    st.markdown(
        """
        * **The Scope:** 10 European countries representing different economic models segmented into regional boundaries (**NUTS 1**).
        * **The Mapping:** Individual data from **ESS Round 11** was mapped to a binary classification (*Radical Right* vs. *Other*), verified using the academic **PopuList database** and further online research.
        * **The Engineering (dbt):** I used **dbt** to clean the data, construct indices, and apply survey weights. Individual voter profiles were then merged with regional macro indicators.

        ### Data Analytics & Interactive Interface

        * **Statistical Modeling & Diagnostics:** Powered by `statsmodels` and `scipy`. I used a Generalized Linear Model (GLM) for predictive voter inference, verified via **Variance Inflation Factors (VIF)** to check for multicollinearity among structural and attitudinal predictors.
        * **Machine Learning & Typology Generation:** Driven by `scikit-learn`. I applied **Robust Scaling** to insulate the data from regional economic outliers and ran a $K$-means clustering routine to isolate 6 regional profiles.
        * **The Interactive Engine:** Handled via `Plotly` and Streamlit's reactive components, creating spatial choropleths and metrics, backed by a structured engineering core running on `pandas` and `SQLAlchemy`.
        """
    )

# =====================================================================
# SECTION: MACRO ENVIRONMENT, TRUST & BACKLASH
# =====================================================================
elif section == "Macro Environment Visuals":
    st.header("1. Macro Environments")

    required_cols = [
        "nuts1_region",
        "delta_nuts1_gdp_percap_pps_pct_eu_avg_5yr",
        "delta_nuts1_net_migration_2yr",
    ]
    missing = [c for c in required_cols if c not in df_regions.columns]
    if missing:
        st.error(f"Missing required columns in dataset: {missing}")
        st.stop()

    df_regions["gdp_pct_str"] = df_regions["delta_nuts1_gdp_percap_pps_pct_eu_avg_5yr"].apply(to_3_sig_fig)
    df_regions["mig_shk_str"] = df_regions["delta_nuts1_net_migration_2yr"].apply(to_3_sig_fig)

    if "nuts1_unemployment_rate_pct_2022" in df_regions.columns:
        df_regions["unemp_base_str"] = df_regions["nuts1_unemployment_rate_pct_2022"].apply(to_3_sig_fig)
    elif "unemployment" in df_regions.columns:
        df_regions["unemp_base_str"] = df_regions["unemployment"].apply(to_3_sig_fig)
    else:
        df_regions["unemp_base_str"] = "N/A"

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.markdown("**Economic Divergence: 5-Year Regional GDP Trajectory vs. EU Average**<br>*(Red = Falling Behind Continental Growth Rate)*", unsafe_allow_html=True)
        fig_gdp_pct = go.Figure(go.Choropleth(
            geojson=nuts1_geojson,
            locations=df_regions["nuts1_region"],
            featureidkey="properties.NUTS_ID",
            z=df_regions["delta_nuts1_gdp_percap_pps_pct_eu_avg_5yr"],
            colorscale="RdBu",
            zmid=0.0,
            colorbar=dict(title="EU Avg % Δ", orientation="h", y=-0.15, thickness=15, len=0.7),
            customdata=df_regions[["nuts1_region", "gdp_pct_str", "mig_shk_str", "unemp_base_str"]],
            hovertemplate=(
                "<b>Region: %{customdata[0]}</b><br>"
                "5Y EU Avg % Δ: %{customdata[1]}%<br>"
                "2Y Migration Δ: %{customdata[2]}<br>"
                "Unemployment (2022): %{customdata[3]}%<extra></extra>"
            ),
        ))
        fig_gdp_pct.update_layout(geo=FOCUSED_GEO_LAYOUT, margin={"r": 0, "t": 10, "l": 0, "b": 40}, height=600)
        st.plotly_chart(fig_gdp_pct, use_container_width=True)

        st.markdown(
            """
            <div style="padding: 10px; background-color: rgba(255,255,255,0.02); border-radius: 5px;">
                <strong>Key Takeaway: Perceived vs. Real Decline</strong><br>
                • While almost all target regions experienced positive <i>nominal</i> growth over this period, large disparities emerge when benchmarked against the continental trend.<br>
                • Several key regions notably lagged behind the EU-27 baseline average, possibly emphasizing a sense of "relative decline."
            </div>
            """,
            unsafe_allow_html=True
        )

    with row1_col2:
        st.markdown("**2-Yr Net Migration Acceleration**<br>*(Red = Inflow Acceleration | Blue = Outflow)*", unsafe_allow_html=True)

        min_mig, max_mig = -20.0, 40.0
        asymmetric_rdbu = [
            [0.0, 'rgb(33,102,172)'],
            [0.1666, 'rgb(146,197,222)'],
            [0.3333, 'rgb(247,247,247)'],
            [0.5555, 'rgb(244,165,130)'],
            [0.7777, 'rgb(214,96,77)'],
            [1.0, 'rgb(178,24,43)']
        ]

        fig_mig = go.Figure(go.Choropleth(
            geojson=nuts1_geojson,
            locations=df_regions["nuts1_region"],
            featureidkey="properties.NUTS_ID",
            z=df_regions["delta_nuts1_net_migration_2yr"],
            colorscale=asymmetric_rdbu,
            zmin=min_mig,
            zmax=max_mig,
            colorbar=dict(title="Migration Δ", orientation="h", y=-0.15, thickness=15, len=0.7),
            customdata=df_regions[["nuts1_region", "gdp_pct_str", "mig_shk_str", "unemp_base_str"]],
            hovertemplate=(
                "<b>Region: %{customdata[0]}</b><br>"
                "5Y EU Avg % Δ: %{customdata[1]}%<br>"
                "2Y Migration Δ: %{customdata[2]}<br>"
                "Unemployment (2022): %{customdata[3]}%<extra></extra>"
            ),
        ))
        fig_mig.update_layout(geo=FOCUSED_GEO_LAYOUT, margin={"r": 0, "t": 10, "l": 0, "b": 40}, height=600)
        st.plotly_chart(fig_mig, use_container_width=True)

        st.markdown(
            """
            <div style="padding: 10px; background-color: rgba(255,255,255,0.02); border-radius: 5px;">
                <strong>Key Takeaway: Geopolitical Shifts vs. Rhetoric</strong><br>
                • Shock-level acceleration in Poland is primarily driven by displacement from the war in Ukraine.<br>
                • Outside of clear migration entry hubs in Spain and Italy, the actual rate of migration remains consistent elsewhere, indicating that public anxiety may outpace actual short-run demographic shifts.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Socio-Institutional Trust Distribution by Nation")

    country_order = (
        df_individuals.groupby("country_code")["trust_index"]
        .median()
        .sort_values(ascending=False)
        .index
    )

    fig_trust = px.box(
        df_individuals,
        x="country_code",
        y="trust_index",
        category_orders={"country_code": country_order},
        color="country_code",
        labels={"country_code": "Country", "trust_index": "Systemic Trust Index (0–10)"},
        title="Institutional Trust Distribution Within National Contexts"
    )

    df_regional_trust = (
        df_individuals
        .groupby(["country_code", "nuts1_region"], as_index=False)["trust_index"]
        .mean()
    )

    fig_trust.add_trace(
        go.Scatter(
            x=df_regional_trust["country_code"],
            y=df_regional_trust["trust_index"],
            mode="markers",
            marker=dict(color="black", size=7, opacity=0.75, line=dict(width=0.8, color="white")),
            name="NUTS1 Mean",
            customdata=df_regional_trust["nuts1_region"],
            hovertemplate="<b>Region: %{customdata}</b><br>Mean Trust: %{y:.2f}<extra></extra>"
        )
    )

    fig_trust.update_layout(height=400, showlegend=False, margin={"t": 40, "b": 10, "l": 10, "r": 10})
    st.plotly_chart(fig_trust, use_container_width=True)

    st.markdown(
        """
        <div style="padding: 12px; margin-top: 5px; border-left: 4px solid #4a5568; background-color: rgba(255,255,255,0.01);">
            <strong>🏛️ Systemic Trust Insights:</strong><br>
            • <b>The Nordic Anchor:</b> Nordic democracies exhibit a distinctively high median trust baseline, creating a significant societal buffer.<br>
            • <b>The Low-Trust Axis:</b> Poland and Bulgaria anchor the opposite end of the spectrum, indicating societal friction.<br>
            • <b>Sub-National Variation:</b> Germany and Italy reveal more volatile regional spreads, whereas other states are more tightly clustered.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.header("2. The Geography of Backlash")
    st.markdown(
        "This section maps spatial variation in far right voting at the NUTS1 level, "
        "highlighting heterogeneity within and across national boundaries."
    )

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Radical Right Vote Intensity")
        df_regional_vote = df_individuals.groupby("nuts1_region", as_index=False)["radical_right_vote"].mean()
        df_regional_vote["vote_pct_str"] = (df_regional_vote["radical_right_vote"] * 100).map(lambda x: f"{x:.1f}%")

        fig_vote_map = px.choropleth(
            df_regional_vote,
            geojson=nuts1_geojson,
            locations="nuts1_region",
            featureidkey="properties.NUTS_ID",
            color="radical_right_vote",
            color_continuous_scale="Reds",
            range_color=[0.0, df_regional_vote["radical_right_vote"].max()],
            labels={"radical_right_vote": "Vote Share"},
        )
        fig_vote_map.update_traces(
            customdata=df_regional_vote[["nuts1_region", "vote_pct_str"]],
            hovertemplate="<b>Region: %{customdata[0]}</b><br>Far Right Vote Share: %{customdata[1]}<extra></extra>"
        )
        fig_vote_map.update_layout(
            geo=FOCUSED_GEO_LAYOUT,
            margin={"r": 0, "t": 10, "l": 0, "b": 40},
            height=600,
            coloraxis_colorbar=dict(title="Vote Share", orientation="h", y=-0.15, thickness=15, len=0.5)
        )
        st.plotly_chart(fig_vote_map, use_container_width=True)

    st.markdown(
        """
        <div style="padding: 12px; background-color: rgba(255,255,255,0.02); border-radius: 5px; border-top: 3px solid #e74c3c;">
            <strong>Institutional Normalization</strong><br>
            • The highest concentration of radical-right voting is in <b>Italy and France</b>, reflecting mainstream political options where voting far-right has transitioned from a fringe protest mechanism into a normalized institutional choice.
        </div>
        """,
        unsafe_allow_html=True
    )

    with col4:
        st.subheader("Voting Behaviour Composition by Country")
        keep_categories = ["Valid Party Vote", "Ineligible / Not Applicable", "Refuse to Say"]

        df_individuals["voting_behavior_display"] = (
            df_individuals["voting_behavior_manifest"]
            .where(df_individuals["voting_behavior_manifest"].isin(keep_categories), "Other / Missing")
        )

        df_cross = pd.crosstab(
            df_individuals["country_code"],
            df_individuals["voting_behavior_display"],
            normalize="index"
        ) * 100
        df_cross = df_cross.sort_values(by="Valid Party Vote", ascending=True)

        color_map = {
            "Valid Party Vote": "#4a90d9",
            "Ineligible / Not Applicable": "#b0b0b0",
            "Refuse to Say": "#d4a847",
            "Other / Missing": "#e0e0e0"
        }

        fig_stacked = px.bar(df_cross, orientation="h", barmode="stack", color_discrete_map=color_map)
        fig_stacked.update_traces(texttemplate="%{value:.1f}%", textposition="inside", cliponaxis=False)
        fig_stacked.update_layout(
            xaxis_title="Percentage of Respondents (%)",
            yaxis_title="Country",
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5),
            margin={"t": 30, "b": 60, "l": 20, "r": 20},
            height=600
        )
        st.plotly_chart(fig_stacked, use_container_width=True)

        # Behavioral Composition Takeaways
    st.markdown(
        """
        <div style="padding: 12px; background-color: rgba(255,255,255,0.02); border-radius: 5px; border-top: 3px solid #d4a847;">
            <strong>The Social Stigma Effect</strong><br>
            • Significant variations emerge in respondents' willingness to disclose their actual vote choices, suggesting <b>social stigma</b>. Countries like <b>Sweden</b> display distinct disclosure dynamics compared to <b>Italy</b>, highlighting where non-random missing data may obscure the true strength of polarizing factions.
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================================
# SECTION: INDIVIDUAL-LEVEL GLM MODEL
# =====================================================================
elif section == "Individual-Level GLM Model":
    st.header("3. Which Factors Matter Most?")
    # Consolidated Modeling Strategy & Technical Reading Guide
    st.info(
    """
    **Model Objective:** This model quantifies how individual attitudes relate to radical-right voting propensity, using a survey-weighted binomial logistic regression (GLM).

     **Modeling Strategy & Statistical Guide**

    To maximize clarity, this framework prioritizes **parsimony** by restricting the specification to essential predictors. Because country fixed effects require regional variation to compute, **Portugal and Finland are omitted** from those specific controls as they each contain only 1 NUTS-1 region.

    **How to read the table below:**

    Coefficients represent **log-odds** estimates. Significance levels follow standard academic thresholds: `* p < 0.05` (Significant), `** p < 0.01` (Highly Significant), and `*** p < 0.001` (Extremely Significant).
    """
)

    required_df_cols = {"variable", "coef", "pvalue", "stderr"}
    if not required_df_cols.issubset(reg_summary.columns):
        st.error(f"reg_summary layout anomaly. Missing targets: {required_df_cols}")
        st.stop()

    def get_stars(p_val):
        if p_val is None:
            return ""
        p = float(p_val)
        if p < 0.001:
            return "***"
        if p < 0.01:
            return "**"
        if p < 0.05:
            return "*"
        return ""

    def get_var_stats(var_name):
        match = reg_summary.loc[reg_summary["variable"] == var_name]
        if not match.empty:
            row = match.iloc[0]
            return float(row["coef"]), float(row["pvalue"])
        return None, None


    # 2. INTERPRETATION GUIDE BOXES (Kept pristine as requested)
    st.markdown("### Interpretation Guide: Percentage Impact on Odds")

    guide_metrics = {
        "immigrants_impact_country": "Immigration Sentiment (per unit increase) - Do immigrants make this country worse or better (0-10)",
        "trust_index": "Institutional Trust (per unit increase): composite of trust in parliament, legal system, and political parties (0-10)",
        "educ_attainment": "Education Attainment (per level increase), from less than lower secondary to higher tertiary",
    }

    g_col1, g_col2, g_col3 = st.columns(3)
    guide_cols = [g_col1, g_col2, g_col3]

    for col, (var, label) in zip(guide_cols, guide_metrics.items()):
        coef, _ = get_var_stats(var)
        if coef is not None:
            pct_effect = (np.exp(coef) - 1) * 100
            direction = "Increase" if pct_effect > 0 else "Decrease"
            color = "red" if pct_effect > 0 else "green"

            with col:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 5px; border-left: 4px solid {color};">
                        <strong style="font-size: 14px;">{label}</strong><br>
                        <span style="font-size: 24px; font-weight: bold; color: {color};">{abs(pct_effect):.1f}%</span>
                        <span style="font-size: 14px;">{direction} in Odds</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("")

    # 3. REGRESSION DATA PROCESSING & TABLE RENDER (Redundant coefficient metric columns stripped)
    display_df = reg_summary.copy()
    display_df["stars"] = display_df["pvalue"].apply(get_stars)
    display_df["variable"] = display_df["variable"] + display_df["stars"]
    display_df["coef"] = display_df["coef"].astype(float).map("{:.3f}".format)
    display_df["pvalue"] = display_df["pvalue"].astype(float).apply(
        lambda p: "<0.001" if p < 0.001 else f"{p:.3f}"
    )
    display_df["stderr"] = display_df["stderr"].astype(float).map("{:.3f}".format)

    model_order = [
        "Intercept", "C(country_code)[T.DE]", "C(country_code)[T.ES]", "C(country_code)[T.FI]",
        "C(country_code)[T.FR]", "C(country_code)[T.GR]", "C(country_code)[T.IT]",
        "C(country_code)[T.PL]", "C(country_code)[T.PT]", "C(country_code)[T.SE]",
        "delta_nuts1_gdp_percap_pps_pct_eu_avg_5yr", "delta_nuts1_unemployment_rate_5yr",
        "delta_nuts1_net_migration_2yr", "trust_index", "immigrants_impact_country",
        "educ_attainment", "gender", "age"
    ]

    order_mapping = {
        var + get_stars(reg_summary.loc[reg_summary["variable"] == var, "pvalue"].values[0] if var in reg_summary["variable"].values else None): idx
        for idx, var in enumerate(model_order)
    }

    display_df["sort_order"] = display_df["variable"].map(order_mapping)
    display_df = display_df.sort_values("sort_order").drop(columns=["stars", "sort_order"])

    column_sequence = ["variable", "coef", "pvalue", "stderr"]
    display_df = display_df[column_sequence]

    # Renders the flat complete table layout seamlessly
    st.table(display_df)

    st.markdown(
        """
        ### 🗳️ What Actually Drives Radical-Right Voting?

        The individual-level data reveals a clear hierarchy of what matters most to voters.
        Rather than short-run economic shifts, voting behavior is heavily associated with personal outlooks and national history.

        **The National Context (The Core Baseline)** 💪🏼💪🏼💪🏼
        * Even when comparing voters with the *exact same* education, age, and attitudes, **national context remains the strongest factor**.
        * Simply living in **Italy, France, Finland, Sweden, or Spain** gives voters a significantly higher baseline probability of voting radical right, reflecting established parties and distinct national political landscapes.
        ---
        **Attitudes Matter** 💪🏼💪🏼
        * **Immigration Perceptions:** Discontent with immigration is the single strongest predictor of radical-right voting in the dataset.
        * **Institutional Trust:** Lower trust in political institutions is associated with a significant increase in anti-establishment voting.

        ---

        **Secondary Drivers (Demographics)** 💪🏼
        * **Education:** Higher formal education is associated with lower support, though its effect size is smaller than the attitudinal variables above.
        * **Gender & Age:** Women and older respondents show noticeably lower baseline support.

    """
    )

# =====================================================================
# SECTION: REGIONAL STRUCTURAL TYPOLOGY
# =====================================================================
elif section == "Regional Structural Typology":
    st.header("4. Regional Structural Typology")

    st.markdown(
        """
        1. **Structural Grouping:** A clustering model groups regions purely by macro metrics (*GDP per capita (as a percentage of EU average), unemployment, net migration*).
        2. **Behavioral Overlay:** Survey data (*trust levels, voting behavior*) is overlaid onto these groups to see how attitudes align with economic realities.
        """
    )

    k_opt = 6
    cluster_col = f"cluster_k{k_opt}"

    df_regions["nuts1_region"] = df_regions["nuts1_region"].astype(str).str.strip().str.upper()
    cluster_map = df_regions[["nuts1_region", cluster_col]].copy()
    cluster_map[cluster_col] = cluster_map[cluster_col].astype(int)

    fig_clusters = go.Figure()

    for cid in sorted(cluster_map[cluster_col].dropna().unique()):
        sub = cluster_map[cluster_map[cluster_col] == cid]
        fig_clusters.add_trace(go.Choropleth(
            geojson=nuts1_geojson,
            locations=sub["nuts1_region"],
            featureidkey="properties.NUTS_ID",
            z=[cid] * len(sub),
            name=CLUSTER_LABELS[cid],
            colorscale=[[0, CLUSTER_COLORS[cid]], [1, CLUSTER_COLORS[cid]]],
            showscale=False,
            showlegend=True,
            marker_line_width=0.3,
            hovertemplate="<b>Region: %{location}</b><br>Structural Archetype: " + CLUSTER_LABELS[cid] + "<extra></extra>",
        ))

    fig_clusters.update_layout(
        geo=FOCUSED_GEO_LAYOUT,
        legend=dict(
            title=dict(text="Structural Typology", font=dict(size=22, weight="bold")),
            orientation="v",
            x=0.82,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            font=dict(size=20),
            traceorder="normal"
        ),
        margin={"r": 60, "t": 10, "l": 0, "b": 10},
        height=600
    )
    st.plotly_chart(fig_clusters, use_container_width=True)

    st.markdown("#### Cluster-Level Structural and Behavioural Profile Matrix")

    regional_behavior_means = df_individuals.groupby("nuts1_region", as_index=False)[["trust_index", "radical_right_vote"]].mean()
    df_final_display = df_regions.merge(regional_behavior_means, on="nuts1_region", how="left")
    df_final_display["typology_name"] = df_final_display[cluster_col].map(CLUSTER_LABELS)

    profile_cols = [c for c in ["gdp", "unemployment", "migration", "trust_index", "radical_right_vote"] if c in df_final_display.columns]

    profile_summary = (
        df_final_display
        .groupby("typology_name", as_index=False)[profile_cols]
        .median()
    )

    ordered_typologies = [
        "Economically Deprived Periphery",
        "Affluent Established Radical Right Presence",
        "High Migration Low Backlash Regions",
        "Vulnerable Battlegrounds",
        "Alienated and Educated Skeptics",
        "Status Quo Powerhouses"
    ]

    profile_summary["typology_name"] = pd.Categorical(
        profile_summary["typology_name"],
        categories=ordered_typologies,
        ordered=True
    )
    profile_summary = profile_summary.sort_values("typology_name")

    format_rules = {
        "gdp": "{:.2f}",
        "unemployment": "{:.1f}%",
        "migration": "{:.2f}",
        "trust_index": "{:.2f}",
        "radical_right_vote": "{:.1%}"
    }
    applied_formats = {k: v for k, v in format_rules.items() if k in profile_cols}

    st.dataframe(
        profile_summary.style.format(applied_formats),
        use_container_width=True
    )

# =====================================================================
# SECTION: STRATEGIC IMPLICATIONS
# =====================================================================
elif section == "Key Findings":
    st.header("What Do the Results Suggest?")
    st.markdown(
        """
        The results challenge several common assumptions about radical-right voting.

        * **Economic hardship alone does not explain political outcomes.** Some of the most economically disadvantaged regions in the dataset do not exhibit especially high levels of radical-right support, while several affluent regions record above-average vote shares.
        * **Immigration attitudes and institutional trust matter more than macro factors** — and more than actual migration rates.
        * **National context remains the most influential factor**, even after accounting for individual attitudes and regional conditions — pointing to institutional and political baselines the model doesn't capture directly.

        Taken together, radical-right voting is best understood as a multi-level phenomenon: individual attitudes outweigh short-term economic shifts, while national political history sets the baseline likelihood across Europe.
        """
    )
# =====================================================================
# SECTION: SCOPE & LIMITATIONS
# =====================================================================
elif section == "Scope & Limitations":
    st.header("Scope & Limitations")

    lim_col1, lim_col2 = st.columns(2)

    with lim_col1:
        st.markdown(
            """
            ### ⌛️ Time & Technical Trade-offs
            * **The 3-Week Sprint:** All research, data wrangling, analysis, and this entire dashboard were completed within a tight three-week timeline.
            * **The "Snapshot" Reality:** The model looks at a specific moment in time (cross-sectional survey data). It captures **predictive associations**, but does not establish causal proof.
            * **The Migration Data Window:** Migration data was not consistently available over the time period, so a **2-year delta** was used rather than 5 years.
            * **The Clustering Balancing Act:** In the K-Means model, balancing structural stability against interpretability is difficult. One cluster contains only 4 regions, possibly capturing residual variation.
            """
        )

    with lim_col2:
        st.markdown(
            """
            ### 🗺️ Survey Reality & Border Friction
            * **The Region (NUTS 1):** These are coarse, large regions which obscure nuance. NUTS 2 would offer more local detail, but not all countries in the survey support that granularity, and sample sizes per region would decrease significantly. NUTS 1 keeps the sample sizes robust.
            * **The Regional Imbalance (Fixed Effects Omissions):** Some nations have numerous NUTS regions, providing rich internal variation. Others, like **Portugal and Finland**, map to only a single NUTS-1 region. Because a region cannot vary against itself, these were omitted from the fixed effects model.
            * **The Stigma of the Ballot Box:** Radical voting behavior often suffers from non-random missing data, due to outright refusals to disclose or social stigma around admitting a far-right vote choice.
            """
        )

# =====================================================================
# SECTION: DATA SOURCES & ATTRIBUTIONS
# =====================================================================
elif section == "Data Sources & Attributions":
    st.header("Data Sources, Theoretical Frameworks & Technical Attributions 📚")

    tab_data, tab_theory, tab_ai = st.tabs(["📊 Core Datasets", "📖 Academic Theory", "🛠️ AI Collaboration Stack"])

    with tab_data:
        st.markdown(
            """
            ### Primary Empirical Data

            * **Individual-Level Survey Microdata:** *European Social Survey (ESS)* (Multi-round cumulative dataset).
            * **Regional Structural Baseline Metrics:** *Eurostat Regional Databases* (NUTS1 Geographic Aggregations).
            """
        )

    with tab_theory:
        st.markdown(
            """
            ### Political Economy & Structural Cleavage Literatures

            This regional typology and behavioral analysis are grounded in three core paradigms of contemporary electoral geography:

            * **The "Structural Conflict / Globalization Losers" Thesis**
              * *Kriesi, H., et al. (2006, 2012)* — *West European Politics / Cambridge University Press*.
              * Frames the structural division between "winners" and "losers" of globalization, describing the mechanism through which lower educational attainment and changing demographics shape regional political battlegrounds.

            * **The "Cultural Backlash" Model**
              * *Inglehart, R., & Norris, P. (2016, 2019)* — *Harvard Kennedy School / Cambridge University Press*.
              * Argues that radical-right voting in wealthy, secure, and high-trust contexts is primarily driven by a reaction against shifting cultural values and identity, rather than acute economic deprivation.

            * **The Macro-Political Economy of Populism Synthesis**
              * *Guriev, S., & Papaioannou, E. (2022)* — *Journal of Economic Literature*.
              * Provides the empirical framework for evaluating the joint role of economic insecurity and identity politics in shaping the geography of anti-establishment sentiment.
            """
        )

    with tab_ai:
        st.markdown(
            """
            ### AI Collaboration 🤖

            This dashboard, its analytical pipelines, data re-structuring steps, and front-end visualizations were built using a lot of AI consultation (Claude, Gemini, and ChatGPT) for code drafting, debugging, and narrative framing throughout the three-week sprint. They saved my life.
            """
        )