import urllib.request
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================================================
# MULTI-LEVEL DATA LOADING ENGINE
# =====================================================================
@st.cache_data
def load_hierarchical_data():
    # Load separate regional structures
    df_reg = pd.read_csv("dashboard_regional_data.csv")
    df_reg["nuts1_region"] = df_reg["nuts1_region"].astype(str).str.strip().str.upper()
    # Load as a simple CSV
    reg_summary = pd.read_csv("regression_summary_1.csv")
    # Establish regional archetype string labels
    cluster_labels = {
        0: "Moderate Baseline",
        1: "High Migration",
        2: "Affluent High-Trust Core",
        3: "Low-Trust Populist Strongholds",
        4: "Economically Stressed Periphery"
    }
    df_reg["typology_name"] = df_reg["cluster_k5"].map(cluster_labels)
    
    # Load separate individual survey responses
    df_ind = pd.read_csv("dashboard_individual_data.csv")
    df_ind["nuts1_region"] = df_ind["nuts1_region"].astype(str).str.strip().str.upper()
    df_ind["typology_name"] = df_ind["cluster_k5"].map(cluster_labels)
    
    return df_reg, df_ind, reg_summary

try:
    df_regions, df_individuals, reg_summary = load_hierarchical_data()
except FileNotFoundError:
    st.error("🚨 Dashboard files missing. Please run the double export step in your notebook.")
    st.stop()

# Reliable, raw Eurostat NUTS-1 public geographic boundary repository
nuts1_geojson_url = "https://raw.githubusercontent.com/eurostat/Nuts2grid/master/GeoJson/NUTS_RG_60M_2021_4326_LEVL_1.geojson"

# Bounding box coordinates to securely lock viewports over your study region
geo_viewport_config = dict(
    projection_type="transverse mercator",
    center={"lat": 52.0, "lon": 10.0},
    visible=True,
    showcountries=True,
    countrycolor="LightGrey",
    lataxis_range=[36, 66],
    lonaxis_range=[-10, 32]
)

# =====================================================================
# HEADER NARRATIVE
# =====================================================================
st.title("🇪🇺 The Multilevel Bridge")
st.markdown("### Sub-National Economic Environments, Institutional Trust, and Populist Backlash")
st.markdown(
    "This dashboard functions as an interactive thesis. By parsing macro-economic environments "
    "independently of individual voter psychology, we explore how spatial structural inequality "
    "transforms into anti-system political mobilization across European regions."
)
st.markdown("---")

# =====================================================================
# SECTION 1: MACRO ENVIRONMENTS & SYSTEMIC TRUST VARIANCE
# =====================================================================
st.header("1. Macro Environments & Trust Crises")
st.markdown(
    "**The Paradox:** Regional development markers like GDP changes and net migration do not align uniformly with political anger. "
    "Instead, institutional trust acts as a highly localized, geographical cushion or vulnerability vector."
)

st.subheader("Regional Development Traps (Macro Shock Matrix)")
st.markdown("*Independent structural visuals loaded directly from your notebook.*")

# Step 1: Explicitly download and parse the GeoJSON dict (cached for app performance)
@st.cache_data
def load_geojson():
    url = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_60M_2021_4326_LEVL_1.geojson"
    import urllib.request
    import json
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())
        
nuts1_geojson = load_geojson()

# Step 2: Helper function
def to_3_sig_fig(val):
    if pd.isna(val) or val == 0:
        return "0.00"
    try:
        return f"{float(f'{val:.3g}')}"
    except (ValueError, TypeError):
        return "N/A"

# Step 3: Ensure your df_regions actually contains nuts1_unemployment_rate_pct_2022
df_regions["gdp_shk_str"] = df_regions["delta_nuts1_gdp_percap_euro_5yr"].apply(to_3_sig_fig)
df_regions["mig_shk_str"] = df_regions["delta_nuts1_net_migration_2yr"].apply(to_3_sig_fig)

# Safely handle the unemployment column if it's missing or misnamed in your df_regions
if "nuts1_unemployment_rate_pct_2022" in df_regions.columns:
    df_regions["unemp_base_str"] = df_regions["nuts1_unemployment_rate_pct_2022"].apply(to_3_sig_fig)
else:
    df_regions["unemp_base_str"] = df_regions["unemployment"].apply(to_3_sig_fig)

# Step 4: Configure shared continental baseline views
geo_layout = dict(
    scope="europe",
    showcountries=True,
    countrycolor="LightGrey",
    showlakes=False,
    projection_type="transverse mercator",
    center={"lat": 52.0, "lon": 10.0},
    lataxis_range=[36, 66],
    lonaxis_range=[-10, 32]
)

# Create layout columns for the two maps
col1, col2 = st.columns(2)

with col1:
    st.markdown("**5-Yr GDP per Capita Delta (€)**<br>*(Red = Economic Decline)*", unsafe_allow_html=True)
    
    # Build Panel A: GDP per Capita Shock
    fig_gdp = go.Figure(go.Choropleth(
        geojson=nuts1_geojson,
        locations=df_regions["nuts1_region"],
        featureidkey="properties.NUTS_ID",
        z=df_regions["delta_nuts1_gdp_percap_euro_5yr"],
        colorscale="RdBu",
        zmid=0.0,
        colorbar=dict(
            title="GDP Δ (€)",
            len=0.75,
            y=0.5
        ),
        customdata=df_regions[["nuts1_region", "gdp_shk_str", "mig_shk_str", "unemp_base_str"]],
        hovertemplate=(
            "<b>Region: %{customdata[0]}</b><br>"
            "5-Yr GDP Delta: €%{customdata[1]}<br>"
            "2-Yr Migration Delta: %{customdata[2]}<br>"
            "2022 Unemployment Base: %{customdata[3]}%<extra></extra>"
        ),
    ))

    fig_gdp.update_layout(
        geo=geo_layout,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=450,
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

with col2:
    st.markdown("**2-Yr Net Migration Delta**<br>*(Blue = Outflow | Red = Influx)*", unsafe_allow_html=True)
    
    # Build Panel B: Migration Shock
    fig_mig = go.Figure(go.Choropleth(
        geojson=nuts1_geojson,
        locations=df_regions["nuts1_region"],
        featureidkey="properties.NUTS_ID",
        z=df_regions["delta_nuts1_net_migration_2yr"],
        colorscale="RdBu_r",
        zmid=0.0,
        colorbar=dict(
            title="Migration Δ",
            len=0.75,
            y=0.5
        ),
        customdata=df_regions[["nuts1_region", "gdp_shk_str", "mig_shk_str", "unemp_base_str"]],
        hovertemplate=(
            "<b>Region: %{customdata[0]}</b><br>"
            "5-Yr GDP Delta: €%{customdata[1]}<br>"
            "2-Yr Migration Delta: %{customdata[2]}<br>"
            "2022 Unemployment Base: %{customdata[3]}%<extra></extra>"
        ),
    ))

    fig_mig.update_layout(
        geo=geo_layout,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=450,
    )
    st.plotly_chart(fig_mig, use_container_width=True)


# =====================================================================
# FULL WIDTH SECTION: TRUST DISTRIBUTION
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Socio-Institutional Trust Distribution by Nation")

# 1. Build the base boxplots using individual data (NO points)
fig_trust = px.box(
    df_individuals,
    x="country_code",
    y="trust_index",
    color="country_code",
    labels={"country_code": "Country Code", "trust_index": "Composite Trust Index (0-10)"},
    title="Regional Trust Dispersion Within Countries"
)

# 2. Calculate the specific NUTS-1 regional averages for the overlay
df_regional_trust = df_individuals.groupby(["country_code", "nuts1_region"])["trust_index"].mean().reset_index()

# 3. Add the regional averages as a distinct scatter layer on top of the boxes
fig_trust.add_trace(
    go.Scatter(
        x=df_regional_trust["country_code"],
        y=df_regional_trust["trust_index"],
        mode="markers",
        marker=dict(
            color="black", 
            size=8, 
            line=dict(width=1, color="white"), # Clean white border so they pop against the colored boxes
            opacity=0.8
        ),
        name="NUTS-1 Mean",
        customdata=df_regional_trust["nuts1_region"],
        hovertemplate="<b>Region: %{customdata}</b><br>Average Trust: %{y:.2f}<extra></extra>"
    )
)

# 4. Clean up the layout
fig_trust.update_layout(
    height=480, 
    showlegend=False, 
    margin={"t":40,"b":10}
)
st.plotly_chart(fig_trust, use_container_width=True)

st.markdown("---")

# =====================================================================
# SECTION 2: THE LANDSCAPE OF POPULIST VOTING
# =====================================================================
st.header("2. The Geography of Populist Backlash")
st.markdown(
    "Before structuring our economic types, we map out where right-wing populist voting is concentrated. "
    "Notice the vast, sub-national regional variation occurring within identical national borders."
)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Right-Wing Populist Vote Concentration")
    
    # Create regional groupings from the individual dataset for a clean map layer
    df_regional_vote = df_individuals.groupby("nuts1_region")["rw_populist_vote"].mean().reset_index()
    
    # Optional: Create a clean percentage string for the tooltip
    df_regional_vote["vote_str"] = (df_regional_vote["rw_populist_vote"] * 100).map("{:.1f}%".format)
    
    fig_vote_map = px.choropleth(
        df_regional_vote,
        geojson=nuts1_geojson, # <-- FIX: Passed the cached dictionary from Section 1, not the URL
        locations="nuts1_region",
        featureidkey="properties.NUTS_ID",
        color="rw_populist_vote",
        color_continuous_scale="Reds",
        range_color=[0.0, 0.5],
        labels={"rw_populist_vote": "Mean Vote Share"},
        hover_data={"nuts1_region": True, "rw_populist_vote": False, "vote_str": True}
    )
    
    # FIX: Apply the exact same viewport settings used in Section 1 for visual consistency
    fig_vote_map.update_layout(
        geo=geo_layout, 
        margin={"r":0,"t":10,"l":0,"b":0}, 
        height=500
    )
    st.plotly_chart(fig_vote_map, use_container_width=True)

with col4:
    st.markdown("### Voting Behavior Composition")

    # 1. Generate the cross-tabulation
    df_cross = pd.crosstab(
        df_individuals["country_code"],
        df_individuals["voting_behavior_manifest"],
        normalize="index"
    ) * 100

    # 2. Sort countries
    df_cross = df_cross.sort_values(by="Valid Party Vote", ascending=True)

    # 3. Create the interactive stacked bar chart
    fig_stacked = px.bar(
        df_cross,
        orientation="h",
        barmode="stack",
        color_discrete_sequence=px.colors.sequential.Viridis_r,
        labels={"value": "Percentage (%)", "country_code": "Country", "variable": "Voting Behavior"}
    )

    # 4. Refine text appearance and labeling
    fig_stacked.update_traces(
        texttemplate="%{value:.1f}%", # Adds the "%" sign and formats the number
        textposition="inside",        # Centers the text within the bar segment
        textfont_size=10,
        cliponaxis=False
    )

    fig_stacked.update_layout(
        xaxis_title="Percentage of Respondents (%)",
        yaxis_title="Country",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin={"t": 50, "b": 20, "l": 20, "r": 20},
        height=500
    )

    st.plotly_chart(fig_stacked, use_container_width=True)


# =====================================================================
# SECTION 3: THE ENGINE (GLM COEFFICIENTS PANEL)
# =====================================================================

st.header("3. Statistical Micro-Foundations (Individual-Level GLM)")
st.markdown(
    "To understand *why* geography behaves this way, we analyze individual mechanics. This statistical panel "
    "displays your pre-computed clustered log-odds regression outputs, proving that subjective trust deficits "
    "and educational metrics hold substantially more predictive weight over voting outcomes than absolute macro conditions."
)

# 1. Access coefficients directly from the loaded reg_summary dataframe
# Note: We use .loc[] to find the row where the index (or 'Unnamed: 0') matches the variable name
# Ensure your CSV 'regression_summary.csv' has an index column corresponding to the variable names
def get_coef(var_name):
    matches = reg_summary.loc[
        reg_summary["variable"] == var_name,
        "coef"
    ]

    if matches.empty:
        st.error(f"Variable not found: {var_name}")
        st.write(reg_summary["variable"].tolist())
        st.stop()

    return float(matches.iloc[0])

# 2. Key Metrics Summary
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric(label="Institutional Trust Index (β)", value=f"{get_coef('trust_index'):.2f}")
with m_col2:
    st.metric(label="Educational Attainment (β)", value=f"{get_coef('educ_attainment'):.2f}")
with m_col3:
    st.metric(label="Gender (Female β)", value=f"{get_coef('gender'):.2f}")
with m_col4:
    st.metric(label="Immigrant Impact (β)", value=f"{get_coef('immigrants_impact_country'):.2f}")

# 3. Full Regression Table
with open("logit_summary.html", "r") as f:
    summary_html = f.read()

custom_html = f"""
<style>
body {{
    color: white;
    background-color: transparent;
    font-size: 16px;
}}

table {{
    width: 100%;
    color: white;
    border-collapse: collapse;
}}

th, td {{
    color: white;
    padding: 6px;
}}

</style>

{summary_html}
"""

st.components.v1.html(
    custom_html,
    height=700,
    scrolling=True
)
st.markdown("---")

# =====================================================================
# SECTION 4: THE GRAND FINALE (THE 5 STRUCTURAL ARCHETYPES)
# =====================================================================
st.header("4. Deep Structure: The 5 Regional Typology Archetypes")

st.markdown(
    "**The Resolution:** Structural archetypes derived from unsupervised clustering "
    "summarise regional environments independent of individual-level variation."
)

# =========================================================
# CLUSTER DEFINITIONS
# =========================================================
cluster_labels = {
    0: "Moderate Baseline",
    1: "High Migration",
    2: "Affluent High-Trust Core",
    3: "Low-Trust Populist Strongholds",
    4: "Economically Stressed Periphery"
}

cluster_colors = {
    0: "#3920b9",
    1: "#a9c03b",
    2: "#d95f02",
    3: "#b30f2d",
    4: "#1b9e77"
}

# =========================================================
# DATA PREP
# =========================================================
cluster_map = df_regions[["nuts1_region", "cluster_k5"]].copy()
cluster_map["cluster_k5"] = cluster_map["cluster_k5"].astype(int)

# =========================================================
# BASE GEO DATA
# =========================================================
nuts1_geojson = load_geojson()

geo_layout = dict(
    scope="europe",
    showcountries=True,
    countrycolor="LightGrey",
    projection_type="transverse mercator",
    center={"lat": 52.0, "lon": 10.0},
)

# =========================================================
# CHOROPLETH (DISCRETE CLUSTERS WITH LEGEND)
# =========================================================
fig = go.Figure()

for cid in sorted(cluster_map["cluster_k5"].dropna().unique()):
    sub = cluster_map[cluster_map["cluster_k5"] == cid]

    fig.add_trace(
        go.Choropleth(
            geojson=nuts1_geojson,
            locations=sub["nuts1_region"],
            featureidkey="properties.NUTS_ID",
            z=[cid] * len(sub),

            name=cluster_labels[cid],

            colorscale=[
                [0, cluster_colors[cid]],
                [1, cluster_colors[cid]]
            ],

            showscale=False,
            showlegend=True,

            marker_line_width=0.3,

            hovertemplate=(
                "<b>%{location}</b><br>"
                "Type: " + cluster_labels[cid] + "<extra></extra>"
            ),
        )
    )

# =========================================================
# LAYOUT
# =========================================================
fig.update_layout(
    geo=geo_layout,

    legend=dict(
    title="Structural Types",
    x=1.02,
    y=0.5,
    xanchor="left",
    yanchor="middle",
    font=dict(size=10)
),

    margin={"r": 160, "t": 40, "l": 20, "b": 20},
    height=650
)

st.plotly_chart(fig, use_container_width=True)

# Contextual Summary Table showing profile medians
st.markdown("#### Environmental Attribute Grid Across Cluster Boundaries")

# Reconstruct behavioural + structural dataset if needed
regional_behavior_means = (
    df_individuals
    .groupby("nuts1_region")[["trust_index", "rw_populist_vote"]]
    .mean()
    .reset_index()
)

df_final_display = df_regions.merge(
    regional_behavior_means,
    on="nuts1_region",
    how="left"
)

# ensure typology exists
df_final_display["typology_name"] = df_final_display["cluster_k5"].map({
    0: "Moderate Baseline",
    1: "High Migration",
    2: "Affluent High-Trust Core",
    3: "Low-Trust Populist Strongholds",
    4: "Economically Stressed Periphery"
})

# grouped profile medians
profile_summary = (
    df_final_display
    .groupby("typology_name")[[
        "gdp",
        "unemployment",
        "migration",
        "trust_index",
        "rw_populist_vote"
    ]]
    .median()
)

# optional: enforce meaningful ordering
ordered_index = [
    "Affluent High-Trust Core",
    "Moderate Baseline",
    "High Migration",
    "Low-Trust Populist Strongholds",
    "Economically Stressed Periphery"
]

profile_summary = profile_summary.reindex(
    [x for x in ordered_index if x in profile_summary.index]
)

st.dataframe(
    profile_summary.style.format({
        "gdp": "€{:.0f}",
        "unemployment": "{:.1f}%",
        "migration": "{:+.2f}",
        "trust_index": "{:.2f} / 10",
        "rw_populist_vote": "{:.1%}"
    }),
    use_container_width=True
)