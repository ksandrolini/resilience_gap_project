# The Geography of Discontent

A multi-level, multi-country empirical analysis investigating the intersections of regional macroeconomics, individual institutional trust, and radical-right voting behavior across Europe using European Social Survey (ESS) Round 11 microdata and Eurostat regional metrics.

---

## 1. Project Overview

This project investigates the multi-level drivers of radical-right voting behavior across European regions. 

The core premise is that electoral radicalization is not a simple byproduct of direct economic hardship. Instead, it occurs within a complex intersection of individual-level attitudes and localized regional dynamics. The project evaluates this phenomenon through two distinct analytical paths:
* **Behavioral Inference Modeling:** A fixed-effects Generalized Linear Model (GLM) calculating odds ratios to weigh the predictive power of individual values against regional environments.
* **Spatial Typologies:** A K-Means clustering approach that groups geographic regions purely by structural metrics, subsequently overlaying survey realities to discover how public sentiment aligns with structural conditions.

The project translates these findings into an interactive **Streamlit Dashboard Engine** designed to offer spatial insights for political scientists, public policy researchers, and electoral strategists.

---

## 2. Project Context

Public and media commentary on European populism frequently leans on uniform, sweeping narratives: the "globalization losers" thesis or uniform regional backlashes. 

This project operates at a finer spatial resolution (**NUTS 1 geographic aggregations**). By bridging individual microdata with regional macro-baselines, it explores whether citizens vote for the radical right because of their immediate regional economic surroundings, or if unobserved national baselines and deeper cultural/institutional trust deficits play the true defining role.

The foundational principle guiding this research is:
> Individual attitudes outweigh short-term economic macro shifts, yet national political histories anchor the absolute baseline likelihood of radical-right support.

---

## 3. Data Infrastructure & Scope

The analytical pipeline dynamically integrates and harmonizes two distinct data granularities across a **10-nation European subset**:

* **Individual-Level Microdata:** *European Social Survey (ESS) Round 11 (2023/2024)*. Features core metrics tracking political orientation, socio-demographic baselines, institutional trust scores, and self-reported voting choices.
* **Regional-Level Macro Metrics:** *Eurostat Regional Databases*. Features structural indicators aggregated at the NUTS 1 level, including GDP per capita (as a % of the EU average), standardized unemployment rates, and net migration metrics.
* **Spatial Geometry Engine:** Standardized **NUTS 1 TopoJSON/GeoJSON** boundaries to enable custom coordinate mapping.

*Main Production Stack:* Python, Pandas, NumPy, Statsmodels (GLM module), Scikit-Learn (K-Means), Plotly Express & Graph Objects, and Streamlit.

---

## 4. Key Variables & Dimensional Tiers

### 4.1 Outcome Focus
* **Primary Binary Dependent Variable:** Self-reported voting choice for a recognized radical-right political entity (`radical_right_vote`, mapped 0 or 1).
* **Composite Covariate:** Institutional Trust Index (`trust_index`), constructed by averaging evaluations of parliaments, politicians, and political parties.

### 4.2 Multi-Level Explanatory Structure

| Tier | Concept | Variable Input | Target Capture |
| :--- | :--- | :--- | :--- |
| **Regional Tier (Macro)** | Economic Performance | `gdp` | GDP per capita as a % of the European Union average |
| **Regional Tier (Macro)** | Labor Insecurity | `unemployment` | Standardized regional unemployment rates |
| **Regional Tier (Macro)** | Demographics | `migration` | Net migration window (calculated via a 2-year delta) |
| **Individual Tier (Micro)**| Institutional Trust | `trust_index
