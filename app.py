"""
app.py
------
RMS Titanic — Survival Analytics Dashboard.
Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import load_and_clean_data

#  PAGE CONFIG
st.set_page_config(
    page_title="Titanic Survival Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

#  COLOR PALETTE 

COLOR_SURVIVED = "#2A9D8F"     
COLOR_PERISHED = "#9B2226"     
COLOR_PRIMARY  = "#0B2545"     
COLOR_ACCENT   = "#E8B04B"     
SURVIVAL_PALETTE = {"Yes": COLOR_SURVIVED, "No": COLOR_PERISHED}

#  CSS 
st.markdown("""
<style>
    h1, h2, h3 {
        font-family: 'Georgia', 'Times New Roman', serif;
        color: #0B2545;
        letter-spacing: 0.2px;
    }
    [data-testid="stMetric"] {
        background-color: #F4F6F8;
        border-left: 5px solid #0B2545;
        padding: 14px 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] { font-size: 13px; color: #5A6B7B; }
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #0B2545; }
    [data-testid="stMetricDelta"] { font-size: 13px !important; color: #5A6B7B !important; }
    [data-testid="stMetricDelta"] svg { display: none; }
    .insight-box {
        background: linear-gradient(135deg, #0B2545 0%, #13315C 100%);
        color: #F4F6F8;
        padding: 22px 28px;
        border-radius: 10px;
        border-left: 6px solid #E8B04B;
        margin: 18px 0 26px 0;
        box-shadow: 0 4px 12px rgba(11, 37, 69, 0.15);
    }
    .insight-box h3 {
        color: #E8B04B; margin: 0 0 6px 0;
        font-family: 'Georgia', serif; font-size: 19px;
    }
    .insight-box p {
        font-size: 16px; line-height: 1.6; margin: 0;
        color: #F4F6F8;
    }
    .chart-caption {
        font-size: 13.5px; color: #5A6B7B; margin-top: -6px; margin-bottom: 24px; margin-left: 2px;
        line-height: 1.5; border-left: 3px solid #D8DEE4; padding-left: 10px;
    }
    .footer {
        text-align: center; color: #5A6B7B; font-size: 13px;
        padding: 18px 0; border-top: 1px solid #D8DEE4; margin-top: 40px;
    }
    .footer a { color: #0B2545; text-decoration: none; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

#  LOAD DATA
df = load_and_clean_data()

#  SIDEBAR FILTERS
st.sidebar.markdown("### 🎚️ Filters")
st.sidebar.caption("Refine the analysis. All charts below update live.")

selected_class = st.sidebar.multiselect(
    "Passenger Class",
    options=["First Class", "Second Class", "Third Class"],
    default=["First Class", "Second Class", "Third Class"],
)
selected_sex = st.sidebar.multiselect(
    "Sex", options=["Female", "Male"], default=["Female", "Male"]
)
selected_port = st.sidebar.multiselect(
    "Port of Embarkation",
    options=sorted(df["EmbarkedPort"].unique()),
    default=sorted(df["EmbarkedPort"].unique()),
)
age_range = st.sidebar.slider(
    "Age Range",
    int(df["Age"].min()), int(df["Age"].max()),
    (int(df["Age"].min()), int(df["Age"].max())),
)
fare_range = st.sidebar.slider(
    "Fare Range (£)",
    float(df["Fare"].min()), float(df["Fare"].max()),
    (float(df["Fare"].min()), float(df["Fare"].max())),
)
selected_travel = st.sidebar.multiselect(
    "Travel Status",
    options=["Alone", "With Family"],
    default=["Alone", "With Family"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: combine filters to slice the manifest.")

# Apply filters
filtered = df[
    df["Pclass"].isin(selected_class)
    & df["Sex"].isin(selected_sex)
    & df["EmbarkedPort"].isin(selected_port)
    & df["Age"].between(*age_range)
    & df["Fare"].between(*fare_range)
    & df["TravelStatus"].isin(selected_travel)
]

#  HEADER
st.image("banner.png", use_container_width=True)
st.markdown("---")

# Empty-state guard
if filtered.empty:
    st.warning("No passengers match the current filter combination. "
               "Widen the filters in the sidebar to continue.")
    st.stop()

#  KPI ROW
total          = len(filtered)
survivors      = int(filtered["SurvivedBin"].sum())
perished       = total - survivors
survival_rate  = (survivors / total * 100) if total > 0 else 0
perished_rate  = (perished / total * 100) if total > 0 else 0

female_rate    = (filtered.loc[filtered["Sex"] == "Female", "SurvivedBin"].mean() * 100
                  if (filtered["Sex"] == "Female").any() else 0)
male_rate      = (filtered.loc[filtered["Sex"] == "Male",   "SurvivedBin"].mean() * 100
                  if (filtered["Sex"] == "Male").any() else 0)

fc_rate        = (filtered.loc[filtered["Pclass"] == "First Class", "SurvivedBin"].mean() * 100
                  if (filtered["Pclass"] == "First Class").any() else 0)
tc_rate        = (filtered.loc[filtered["Pclass"] == "Third Class", "SurvivedBin"].mean() * 100
                  if (filtered["Pclass"] == "Third Class").any() else 0)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total passengers", f"{total:,}", "in this dataset", delta_color="off")
c2.metric("Survived", f"{survivors:,}", f"{survival_rate:.1f}% survival rate", delta_color="off")
c3.metric("Did not survive", f"{perished:,}", f"{perished_rate:.1f}% perished", delta_color="off")
c4.metric("Female survival", f"~{int(round(female_rate))}%", f"vs {int(round(male_rate))}% for men", delta_color="off")
c5.metric("1st class survival", f"~{int(round(fc_rate))}%", f"vs {int(round(tc_rate))}% 3rd class", delta_color="off")

#  KEY INSIGHT CALLOUT  (always computed on the FULL dataset for stability)
fc_female_rate = df[(df["Pclass"] == "First Class") & (df["Sex"] == "Female")]["SurvivedBin"].mean() * 100
tc_male_rate   = df[(df["Pclass"] == "Third Class") & (df["Sex"] == "Male")]["SurvivedBin"].mean() * 100
gap            = fc_female_rate - tc_male_rate

st.markdown(f"""
<div class="insight-box">
  <h3> KEY INSIGHT — Survival was decided by class and sex, not chance.</h3>
  <p>A <b> Female First-Class passenger</b> had a <b>{fc_female_rate:.0f}%</b> chance of surviving. While 
   <b>Male Third-Class passenger</b> had only a <b>{tc_male_rate:.0f}%</b> chance, that's a stark
  <b>{gap:.0f}-point</b> gap. The "women and children first" protocol existed, hence why the male to female survival ratio is so high,
  but it was unevenly enforced across decks. Class privilege, was the strongest single predictor of survivability. 
  The sex of the individual is a close second</p>
</div>
""", unsafe_allow_html=True)

#  ROW 1 — Heatmap (centerpiece) + Sunburst
st.markdown("### Survival by Class and Sex")
col_a, col_b = st.columns([1.05, 1])

with col_a:
    pivot = (filtered.pivot_table(values="SurvivedBin", index="Sex",
                                  columns="Pclass", aggfunc="mean") * 100)
    pivot = pivot.reindex(columns=["First Class", "Second Class", "Third Class"])
    fig = px.imshow(
        pivot.round(1),
        text_auto=".1f",
        color_continuous_scale=[[0, COLOR_PERISHED], [0.5, "#F4F6F8"], [1, COLOR_SURVIVED]],
        aspect="auto",
        labels=dict(x="Passenger Class", y="Sex", color="Survival %"),
        zmin=0, zmax=100,
    )
    fig.update_layout(
        title="Survival Rate Heatmap (%)",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
    )
    fig.update_traces(textfont=dict(size=20, color="black", family="Georgia"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Being female significantly improved survival chances across all classes. First-class females had the highest survival rate, while third-class males faced the lowest odds.</p>', unsafe_allow_html=True)

with col_b:
    sb = filtered.groupby(["Pclass", "Sex", "Survived"], observed=True).size().reset_index(name="Count")
    fig = px.sunburst(
        sb, path=["Pclass", "Sex", "Survived"], values="Count",
        color="Survived", color_discrete_map=SURVIVAL_PALETTE,
    )
    fig.update_layout(
        title="Passenger Breakdown — Class → Sex → Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">The outermost ring highlights the stark contrast in outcomes. Third-class passengers made up the largest group on board but yielded the fewest survivors.</p>', unsafe_allow_html=True)

#  ROW 2 — Age histogram + Fare boxplot
col_c, col_d = st.columns(2)

with col_c:
    fig = px.histogram(
        filtered, x="Age", color="Survived",
        nbins=30, barmode="overlay", opacity=0.75,
        color_discrete_map=SURVIVAL_PALETTE, marginal="box",
    )
    fig.update_layout(
        title="Age Distribution by Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420, bargap=0.05,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Young children had disproportionately high survival rates across all demographics. Adult men between 20 and 40 formed the largest passenger segment but suffered the most casualties.</p>', unsafe_allow_html=True)

with col_d:
    fig = px.box(
        filtered, x="Pclass", y="Fare", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE,
        category_orders={"Pclass": ["First Class", "Second Class", "Third Class"]},
        points="outliers",
    )
    fig.update_layout(
        title="Fare Paid by Class & Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Passengers who survived generally paid higher ticket fares, particularly in first class. In lower classes, spending slightly more money made little to no difference in survival.</p>', unsafe_allow_html=True)

#  ROW 3 — Family size dual-axis + Embarkation stack
col_e, col_f = st.columns(2)

with col_e:
    fam = (filtered.groupby("FamilySize")
           .agg(rate=("SurvivedBin", "mean"), count=("SurvivedBin", "size"))
           .reset_index())
    fam["rate"] *= 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=fam["FamilySize"], y=fam["count"],
               name="Passengers", marker_color="#D8DEE4",
               hovertemplate="Size %{x}<br>%{y} passengers<extra></extra>"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=fam["FamilySize"], y=fam["rate"],
                   name="Survival %", mode="lines+markers",
                   line=dict(color=COLOR_ACCENT, width=3),
                   marker=dict(size=10, line=dict(color=COLOR_PRIMARY, width=1)),
                   hovertemplate="Size %{x}<br>%{y:.1f}% survived<extra></extra>"),
        secondary_y=True,
    )
    fig.update_layout(
        title="Family Size vs. Survival Rate",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
        xaxis_title="Family Size (incl. self)",
    )
    fig.update_yaxes(title_text="Passengers", secondary_y=False)
    fig.update_yaxes(title_text="Survival %", secondary_y=True, range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Passengers travelling in small groups survived at much higher rates than solo travellers. However, coordinating evacuation for families of 5 or more proved highly detrimental.</p>', unsafe_allow_html=True)

with col_f:
    emb = (filtered.groupby(["EmbarkedPort", "Survived"])
           .size().reset_index(name="Count"))
    fig = px.bar(
        emb, x="EmbarkedPort", y="Count", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE, barmode="stack", text="Count",
    )
    fig.update_layout(
        title="Survival by Port of Embarkation",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    fig.update_traces(textposition="inside", textfont_color="white")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Cherbourg passengers show higher survival rates primarily because more wealthy, first-class passengers boarded there. Southampton provided the most passengers but saw the highest overall losses.</p>', unsafe_allow_html=True)

#  ROW 4 — Title violin + Age-group bar
col_g, col_h = st.columns(2)

with col_g:
    fig = px.violin(
        filtered, x="Title", y="Age", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE, box=True, points=False,
        category_orders={"Title": ["Master", "Miss", "Mrs", "Mr", "Rare"]},
    )
    fig.update_layout(
        title="Age Distribution by Title & Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">"Master" (young boys) and female titles were heavily prioritised during the evacuation. In contrast, "Mr"—the largest passenger group—experienced the poorest survival rates regardless of age.</p>', unsafe_allow_html=True)

with col_h:
    ag = (filtered.groupby("AgeGroup", observed=True)["SurvivedBin"]
          .mean().reset_index())
    ag["Survival %"] = ag["SurvivedBin"] * 100
    fig = px.bar(
        ag, x="AgeGroup", y="Survival %",
        color="Survival %",
        color_continuous_scale=[[0, COLOR_PERISHED], [1, COLOR_SURVIVED]],
        text="Survival %",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title="Survival Rate by Age Group",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420, yaxis_range=[0, 105],
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Infants and young children were the most likely demographic to survive. Survival chances steadily declined for older teenagers and adults before dropping off entirely for senior passengers.</p>', unsafe_allow_html=True)

#  DATA EXPLORER
with st.expander("📋 Browse the underlying passenger records"):
    show_cols = ["Name", "Survived", "Pclass", "Sex", "Age", "Fare",
                 "FamilySize", "EmbarkedPort", "Title"]
    st.dataframe(filtered[show_cols], use_container_width=True, height=320)
    csv = filtered[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️  Download filtered data (CSV)",
        csv, "titanic_filtered.csv", "text/csv",
    )

#  FOOTER  /  ATTRIBUTION

st.markdown("""
<div class="footer">
  <b>Data source:</b>
  <a href="https://www.kaggle.com/datasets/yasserh/titanic-dataset/data" target="_blank">
    Kaggle — Titanic Survival Prediction Dataset
  </a>, derived from
  <a href="https://www.encyclopedia-titanica.org/" target="_blank">Encyclopedia Titanica</a>.
  Public-domain passenger manifest. <br>
</div>
""", unsafe_allow_html=True)
