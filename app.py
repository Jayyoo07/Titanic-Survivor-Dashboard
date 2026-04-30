"""
app.py  ·  RMS Titanic — Survival Analytics Dashboard
Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import load_and_clean_data

st.set_page_config(
    page_title="Titanic Survival Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_SURVIVED    = "#2A9D8F"
COLOR_PERISHED    = "#9B2226"
COLOR_PRIMARY     = "#0B2545"
COLOR_ACCENT      = "#E8B04B"
SURVIVAL_PALETTE  = {"Yes": COLOR_SURVIVED, "No": COLOR_PERISHED}

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
  h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif; color: #0B2545; letter-spacing: 0.2px; }

  /* ── SIDEBAR BASE ── */
  section[data-testid="stSidebar"] {
      background-color: #1a1f2e !important;
  }
  /* Target only text/inline elements — NOT divs, to avoid bleeding into slider wrappers */
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span:not([data-baseweb="tag"] span),
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] small,
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3,
  section[data-testid="stSidebar"] li,
  section[data-testid="stSidebar"] a { color: #F4F6F8 !important; }

  /* ── MULTISELECT DROPDOWN CONTAINER ── */
  section[data-testid="stSidebar"] [data-baseweb="select"] > div {
      background-color: #111827 !important;
      border: 1px solid #2e3a4e !important;
      border-radius: 6px !important;
  }

  /* ── RED TAGS ── */
  section[data-testid="stSidebar"] span[data-baseweb="tag"] {
      background-color: #E63946 !important;
      border-radius: 5px !important;
      padding: 2px 8px !important;
  }
  section[data-testid="stSidebar"] span[data-baseweb="tag"] span,
  section[data-testid="stSidebar"] span[data-baseweb="tag"] svg { color: #FFFFFF !important; fill: #FFFFFF !important; }

  /* ── SLIDERS — value labels only, no background overrides ── */
  section[data-testid="stSidebar"] [data-testid="stSlider"] p {
      color: #E63946 !important;
      font-weight: 600 !important;
  }

  [data-testid="stMetric"] {
      background: #F4F6F8; border-left: 5px solid #0B2545;
      padding: 14px 16px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  [data-testid="stMetricLabel"] { font-size: 12px; color: #5A6B7B; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; }
  [data-testid="stMetricValue"] { font-size: 26px; font-weight: 700; color: #0B2545; }

  .section-card {
      background: #FFFFFF; border-radius: 12px; padding: 18px 22px 12px;
      margin-bottom: 18px; box-shadow: 0 2px 8px rgba(11,37,69,0.07); border: 1px solid #E4EAF0;
  }
  .section-title { font-family: 'Playfair Display', Georgia, serif; font-size: 19px; font-weight: 700; color: #0B2545; margin: 0 0 2px 0; }
  .section-subtitle { font-size: 13px; color: #6B7A8D; margin: 0; line-height: 1.5; }

  .chart-caption {
      font-size: 12.5px; color: #5A6B7B; margin: -4px 0 16px 2px;
      line-height: 1.55; border-left: 3px solid #D8DEE4; padding-left: 10px;
  }
  .chart-caption b { color: #0B2545; }

  .insight-box {
      background: linear-gradient(135deg, #0B2545 0%, #13315C 100%);
      color: #F4F6F8; padding: 20px 26px; border-radius: 10px;
      border-left: 6px solid #E8B04B; margin: 8px 0 22px 0;
      box-shadow: 0 4px 12px rgba(11,37,69,0.18);
  }
  .insight-box h3 { color: #E8B04B; margin: 0 0 6px 0; font-family: 'Playfair Display', Georgia, serif; font-size: 17px; }
  .insight-box p { font-size: 14.5px; line-height: 1.7; margin: 0; color: #F4F6F8; }

  .mini-insight {
      background: #F0FAF8; border-left: 5px solid #2A9D8F;
      padding: 11px 18px; border-radius: 0 8px 8px 0;
      margin: 4px 0 0 0; font-size: 13px; color: #2C3E50; line-height: 1.7;
  }
  .mini-insight strong { color: #0B2545; }

  hr { border-color: #DDE4EC !important; margin: 6px 0 22px 0 !important; }

  .footer {
      text-align: center; color: #5A6B7B; font-size: 13px;
      padding: 18px 0; border-top: 1px solid #D8DEE4; margin-top: 40px;
  }
  .footer a { color: #0B2545; text-decoration: none; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

df = load_and_clean_data()

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

filtered = df[
    df["Pclass"].isin(selected_class)
    & df["Sex"].isin(selected_sex)
    & df["EmbarkedPort"].isin(selected_port)
    & df["Age"].between(*age_range)
    & df["Fare"].between(*fare_range)
    & df["TravelStatus"].isin(selected_travel)
]

st.image("banner.png", use_container_width=True)
st.markdown("""
<div style="text-align:center;padding:10px 0 4px 0;">
  <h1 style="font-size:32px;margin-bottom:4px;">RMS Titanic — Survival Analytics</h1>
  <p style="color:#5A6B7B;font-size:15px;margin:0;">
    Explore how <b>class</b>, <b>sex</b>, <b>age</b>, and <b>fare</b> shaped who lived and who perished.
    Use the sidebar to drill into any passenger group.
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

if filtered.empty:
    st.warning("No passengers match the current filters. Widen the selections in the sidebar.")
    st.stop()

total         = len(filtered)
survivors     = int(filtered["SurvivedBin"].sum())
survival_rate = survivors / total * 100
female_rate   = (filtered.loc[filtered["Sex"] == "Female", "SurvivedBin"].mean() * 100
                 if (filtered["Sex"] == "Female").any() else 0)
male_rate     = (filtered.loc[filtered["Sex"] == "Male", "SurvivedBin"].mean() * 100
                 if (filtered["Sex"] == "Male").any() else 0)
avg_fare      = filtered["Fare"].mean()

st.markdown("### At a Glance")
st.caption("Live totals for your current filter selection.")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("👥 Passengers",      f"{total:,}")
c2.metric("👨‍👩‍👧‍👧 Survivors",       f"{survivors:,}")
c3.metric("📈 Survival Rate",   f"{survival_rate:.1f}%")
c4.metric("♀ Female Survival", f"{female_rate:.1f}%")
c5.metric("♂ Male Survival",   f"{male_rate:.1f}%")
c6.metric("💷 Avg Fare",        f"£{avg_fare:.2f}")

fc_female_rate = df[(df["Pclass"] == "First Class") & (df["Sex"] == "Female")]["SurvivedBin"].mean() * 100
tc_male_rate   = df[(df["Pclass"] == "Third Class") & (df["Sex"] == "Male")]["SurvivedBin"].mean() * 100
gap            = fc_female_rate - tc_male_rate

st.markdown(f"""
<div class="insight-box">
  <h3>Key Insight — Survival was decided by class and sex, not chance.</h3>
  <p>A <b>First-Class woman</b> had a <b>{fc_female_rate:.0f}%</b> chance of surviving.
  A <b>Third-Class man</b> had only <b>{tc_male_rate:.0f}%</b> — a <b>{gap:.0f}-point gap</b>.
  The "women and children first" protocol existed but was unevenly enforced across decks.
  Class privilege was the strongest predictor of survival; sex was a close second.</p>
</div>
""", unsafe_allow_html=True)

# ── SECTION 1 ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <p class="section-title">1 · Who Survived? — Class &amp; Sex</p>
  <p class="section-subtitle">The two strongest predictors of survival, shown side by side.</p>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns([1.05, 1], gap="large")

with col_a:
    pivot = (filtered.pivot_table(values="SurvivedBin", index="Sex",
                                  columns="Pclass", aggfunc="mean") * 100)
    pivot = pivot.reindex(columns=["First Class", "Second Class", "Third Class"])
    fig = px.imshow(
        pivot.round(1), text_auto=".1f",
        color_continuous_scale=[[0, COLOR_PERISHED], [0.5, "#F4F6F8"], [1, COLOR_SURVIVED]],
        aspect="auto",
        labels=dict(x="Passenger Class", y="Sex", color="Survival %"),
        zmin=0, zmax=100,
    )
    fig.update_layout(
        title="Survival Rate Heatmap (%)",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=30), height=320,
        xaxis=dict(title="Passenger Class", title_font=dict(size=13, color="#0B2545")),
        yaxis=dict(title="Sex",             title_font=dict(size=13, color="#0B2545")),
    )
    fig.update_traces(textfont=dict(size=22, color="black", family="Georgia"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Each cell = survival rate (%) for that sex + class pair. <b>Darker teal = better odds; darker red = worse.</b></p>', unsafe_allow_html=True)

with col_b:
    sb = filtered.groupby(["Pclass", "Sex", "Survived"], observed=True).size().reset_index(name="Count")
    fig = px.sunburst(
        sb, path=["Pclass", "Sex", "Survived"], values="Count",
        color="Survived", color_discrete_map=SURVIVAL_PALETTE,
    )
    fig.update_layout(
        title="Class → Sex → Survived",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=320,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Rings go inward: Class → Sex → Outcome. Segment size = passenger count. <b>Click any segment to zoom in.</b></p>', unsafe_allow_html=True)

f1_df  = filtered[(filtered["Pclass"] == "First Class") & (filtered["Sex"] == "Female")]
m3_df  = filtered[(filtered["Pclass"] == "Third Class") & (filtered["Sex"] == "Male")]
f1_rate = f1_df["SurvivedBin"].mean() * 100 if len(f1_df) > 0 else 0
m3_rate = m3_df["SurvivedBin"].mean() * 100 if len(m3_df) > 0 else 0

st.markdown(f"""
<div class="mini-insight">
<strong>Being female in any class outperformed being male in the class above.</strong>
First-Class women survived at <strong>{f1_rate:.0f}%</strong>; Third-Class men at just <strong>{m3_rate:.0f}%</strong>.
Third Class held the most passengers yet yielded the fewest survivors — deck location and gate access shaped outcomes as much as any protocol.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 2 ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <p class="section-title">2 · Did Age or Fare Make a Difference?</p>
  <p class="section-subtitle">Ticket price and age both mattered — but not equally across all classes.</p>
</div>
""", unsafe_allow_html=True)

col_c, col_d = st.columns(2, gap="large")

with col_c:
    fig = px.histogram(
        filtered, x="Age", color="Survived",
        nbins=30, barmode="overlay", opacity=0.78,
        color_discrete_map=SURVIVAL_PALETTE, marginal="box",
        labels={"Age": "Passenger Age (years)", "count": "Number of Passengers"},
    )
    fig.update_layout(
        title="Age Distribution by Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=390, bargap=0.05,
        xaxis_title="Age (years)", yaxis_title="Passengers",
        legend_title_text="Survived?",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Bars show passenger count at each age. <b>Teal = survived, red = perished.</b> The box plot above shows median + spread. Hover any bar for exact counts.</p>', unsafe_allow_html=True)

with col_d:
    fig = px.box(
        filtered, x="Pclass", y="Fare", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE,
        category_orders={"Pclass": ["First Class", "Second Class", "Third Class"]},
        points="outliers",
        labels={"Pclass": "Passenger Class", "Fare": "Ticket Fare (£)"},
    )
    fig.update_layout(
        title="Fare Paid by Class & Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=390,
        xaxis_title="Passenger Class", yaxis_title="Fare (£)",
        legend_title_text="Survived?",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">The centre line in each box = median fare. <b>Compare teal vs red boxes within the same class</b> to see if paying more actually helped.</p>', unsafe_allow_html=True)

child_df         = filtered[filtered["Age"] < 10]
child_surv       = child_df["SurvivedBin"].mean() * 100 if len(child_df) > 0 else 0
median_fare_surv = filtered[filtered["Survived"] == "Yes"]["Fare"].median()
median_fare_died = filtered[filtered["Survived"] == "No"]["Fare"].median()

st.markdown(f"""
<div class="mini-insight">
<strong>Age mattered most at the youngest end; fare mattered most inside First Class.</strong>
Children under 10 survived at <strong>{child_surv:.0f}%</strong>.
Survivors paid a median fare of <strong>£{median_fare_surv:.1f}</strong> vs <strong>£{median_fare_died:.1f}</strong> for those who perished.
In Third Class the gap is negligible — once on the lower decks, spending more made no difference.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 3 ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <p class="section-title">3 · Did Travelling Together Help? — Family Size &amp; Port</p>
  <p class="section-subtitle">Was it better to have companions in the chaos? And did where you boarded matter?</p>
</div>
""", unsafe_allow_html=True)

col_e, col_f = st.columns(2, gap="large")

with col_e:
    fam = (filtered.groupby("FamilySize")
           .agg(rate=("SurvivedBin", "mean"), count=("SurvivedBin", "size"))
           .reset_index())
    fam["rate"] *= 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=fam["FamilySize"], y=fam["count"], name="Passengers",
               marker_color="#D8DEE4",
               hovertemplate="Family size %{x}<br>%{y} passengers<extra></extra>"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=fam["FamilySize"], y=fam["rate"], name="Survival %",
                   mode="lines+markers", line=dict(color=COLOR_ACCENT, width=3),
                   marker=dict(size=10, line=dict(color=COLOR_PRIMARY, width=1)),
                   hovertemplate="Family size %{x}<br><b>%{y:.1f}%</b> survived<extra></extra>"),
        secondary_y=True,
    )
    fig.update_layout(
        title="Family Size vs. Survival Rate",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=390,
        xaxis_title="Family Size (incl. yourself)",
        legend=dict(orientation="h", y=1.08, x=0),
    )
    fig.update_yaxes(title_text="Passengers", secondary_y=False)
    fig.update_yaxes(title_text="Survival %", secondary_y=True, range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Grey bars (left axis) = passenger count. <b>Gold line (right axis) = survival rate.</b> Size 1 = alone. Look for where the gold line peaks.</p>', unsafe_allow_html=True)

with col_f:
    emb = (filtered.groupby(["EmbarkedPort", "Survived"])
           .size().reset_index(name="Count"))
    fig = px.bar(
        emb, x="EmbarkedPort", y="Count", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE, barmode="stack", text="Count",
        labels={"EmbarkedPort": "Port of Embarkation", "Count": "Passengers"},
    )
    fig.update_layout(
        title="Survival by Port of Embarkation",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=390,
        xaxis_title="Port", yaxis_title="Passengers",
        legend_title_text="Survived?",
    )
    fig.update_traces(textposition="inside", textfont_color="white", textfont_size=13)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Each bar = one port. <b>Compare the teal-to-red ratio within each bar</b> — not just total height — to judge relative survival rates.</p>', unsafe_allow_html=True)

alone_rate    = fam.loc[fam["FamilySize"] == 1, "rate"].values[0] if 1 in fam["FamilySize"].values else 0
best_fam_size = int(fam.loc[fam["rate"].idxmax(), "FamilySize"]) if not fam.empty else 0
best_fam_rate = fam["rate"].max() if not fam.empty else 0
cherb_df      = filtered[filtered["EmbarkedPort"] == "Cherbourg"]
cherb_rate    = cherb_df["SurvivedBin"].mean() * 100 if len(cherb_df) > 0 else 0

st.markdown(f"""
<div class="mini-insight">
<strong>Small families outlasted solo travellers; Cherbourg passengers fared best of all ports.</strong>
Travelling alone gave just <strong>{alone_rate:.0f}%</strong> odds; a group of <strong>{best_fam_size}</strong> reached <strong>{best_fam_rate:.0f}%</strong>.
Very large groups (7+) saw survival collapse — coordinating evacuation together became overwhelming.
Cherbourg's <strong>{cherb_rate:.0f}%</strong> rate reflects a wealthier, First-Class–heavy boarding mix, not any port advantage.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 4 ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <p class="section-title">4 · The Title Effect — How Social Role Shaped Survival</p>
  <p class="section-subtitle">Titles (Mr, Mrs, Miss, Master, Rare) encode sex, age, and social status — a surprisingly powerful predictor.</p>
</div>
""", unsafe_allow_html=True)

col_g, col_h = st.columns(2, gap="large")

with col_g:
    fig = px.violin(
        filtered, x="Title", y="Age", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE, box=True, points=False,
        category_orders={"Title": ["Master", "Miss", "Mrs", "Mr", "Rare"]},
        labels={"Title": "Passenger Title", "Age": "Age (years)"},
    )
    fig.update_layout(
        title="Age Distribution by Title & Survival",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=390,
        xaxis_title="Title", yaxis_title="Age (years)",
        legend_title_text="Survived?",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Shape width = how many passengers of that age. <b>Master</b> = boys under 13 · <b>Rare</b> = officers, clergy, nobility. Compare teal vs red per title.</p>', unsafe_allow_html=True)

with col_h:
    ag = (filtered.groupby("AgeGroup", observed=True)["SurvivedBin"]
          .mean().reset_index())
    ag["Survival %"] = ag["SurvivedBin"] * 100
    fig = px.bar(
        ag, x="AgeGroup", y="Survival %",
        color="Survival %",
        color_continuous_scale=[[0, COLOR_PERISHED], [1, COLOR_SURVIVED]],
        text="Survival %",
        labels={"AgeGroup": "Age Group", "Survival %": "Survival Rate (%)"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                      textfont=dict(size=14, color="#0B2545"))
    fig.update_layout(
        title="Survival Rate by Age Group",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=50, b=10), height=390,
        yaxis_range=[0, 110], coloraxis_showscale=False,
        xaxis_title="Age Group", yaxis_title="Survival Rate (%)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<p class="chart-caption">Bar height = % who survived in that age group. <b>Teal = higher survival, red = lower.</b> The number above each bar is the exact rate.</p>', unsafe_allow_html=True)

master_df   = filtered[filtered["Title"] == "Master"]
mr_df       = filtered[filtered["Title"] == "Mr"]
master_surv = master_df["SurvivedBin"].mean() * 100 if len(master_df) > 0 else 0
mr_surv     = mr_df["SurvivedBin"].mean()     * 100 if len(mr_df)     > 0 else 0
top_age_group = ag.loc[ag["Survival %"].idxmax(), "AgeGroup"] if not ag.empty else "—"
top_age_rate  = ag["Survival %"].max()         if not ag.empty else 0
low_age_group = ag.loc[ag["Survival %"].idxmin(), "AgeGroup"] if not ag.empty else "—"
low_age_rate  = ag["Survival %"].min()         if not ag.empty else 0

st.markdown(f"""
<div class="mini-insight">
<strong>Boys and women were prioritised; adult men faced the worst odds at every age.</strong>
"Master" (boys under ~13) survived at <strong>{master_surv:.0f}%</strong>, while "Mr" — the largest group — managed only <strong>{mr_surv:.0f}%</strong>.
By age group, <strong>{top_age_group}</strong> had the highest rate at <strong>{top_age_rate:.0f}%</strong>;
<strong>{low_age_group}</strong> the lowest at <strong>{low_age_rate:.0f}%</strong>.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("Browse the underlying passenger records"):
    st.caption("Reflects your current filter selection. Download as CSV for further analysis.")
    show_cols = ["Name", "Survived", "Pclass", "Sex", "Age", "Fare",
                 "FamilySize", "EmbarkedPort", "Title"]
    st.dataframe(filtered[show_cols], use_container_width=True, height=320)
    csv = filtered[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data (CSV)", csv, "titanic_filtered.csv", "text/csv")

st.markdown("""
<div class="footer">
  <b>Data source:</b>
  <a href="https://www.kaggle.com/datasets/yasserh/titanic-dataset/data" target="_blank">Kaggle — Titanic Dataset</a>,
  derived from <a href="https://www.encyclopedia-titanica.org/" target="_blank">Encyclopedia Titanica</a>.
  Public-domain passenger manifest · 891 records · Streamlit + Plotly.
</div>
""", unsafe_allow_html=True)