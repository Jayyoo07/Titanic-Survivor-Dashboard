"""
app.py  ·  RMS Titanic — Survival Analytics Dashboard (Enhanced)
Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import load_and_clean_data

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Titanic Survival Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── COLORS ────────────────────────────────────────────────────────────────────
COLOR_SURVIVED    = "#2A9D8F"
COLOR_PERISHED    = "#9B2226"
COLOR_PRIMARY     = "#0B2545"
COLOR_ACCENT      = "#E8B04B"
SURVIVAL_PALETTE  = {"Yes": COLOR_SURVIVED, "No": COLOR_PERISHED}

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── fonts & base ──────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap');

  html, body, [class*="css"] {
      font-family: 'Source Sans 3', sans-serif;
  }
  h1, h2, h3 {
      font-family: 'Playfair Display', Georgia, serif;
      color: #0B2545;
      letter-spacing: 0.2px;
  }

  /* ── sidebar ───────────────────────────────────── */
  section[data-testid="stSidebar"] {
      background: #0B2545 !important;
      border-right: 3px solid #E8B04B;
  }
  section[data-testid="stSidebar"] * { color: #F4F6F8 !important; }
  section[data-testid="stSidebar"] .stSlider > div > div { background: #E8B04B !important; }

  /* ── KPI metrics ───────────────────────────────── */
  [data-testid="stMetric"] {
      background: #F4F6F8;
      border-left: 5px solid #0B2545;
      padding: 14px 16px;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  [data-testid="stMetricLabel"] { font-size: 12px; color: #5A6B7B; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; }
  [data-testid="stMetricValue"] { font-size: 26px; font-weight: 700; color: #0B2545; }

  /* ── section wrappers ──────────────────────────── */
  .section-card {
      background: #FFFFFF;
      border-radius: 12px;
      padding: 24px 28px 18px;
      margin-bottom: 28px;
      box-shadow: 0 2px 8px rgba(11,37,69,0.07);
      border: 1px solid #E4EAF0;
  }
  .section-header {
      display: flex; align-items: flex-start; gap: 14px;
      margin-bottom: 6px;
  }
  .section-icon {
      font-size: 28px; line-height: 1;
  }
  .section-title {
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 20px; font-weight: 700; color: #0B2545;
      margin: 0 0 2px 0;
  }
  .section-subtitle {
      font-size: 13px; color: #6B7A8D; margin: 0; line-height: 1.5;
  }
  .how-to-read {
      background: #EEF4FB;
      border-left: 4px solid #0B2545;
      border-radius: 0 6px 6px 0;
      padding: 10px 16px;
      font-size: 13px;
      color: #2C3E50;
      margin: 10px 0 18px 0;
      line-height: 1.6;
  }
  .how-to-read strong { color: #0B2545; }

  /* ── insight boxes ─────────────────────────────── */
  .insight-box {
      background: linear-gradient(135deg, #0B2545 0%, #13315C 100%);
      color: #F4F6F8;
      padding: 22px 28px;
      border-radius: 10px;
      border-left: 6px solid #E8B04B;
      margin: 8px 0 24px 0;
      box-shadow: 0 4px 12px rgba(11,37,69,0.18);
  }
  .insight-box h3 {
      color: #E8B04B; margin: 0 0 6px 0;
      font-family: 'Playfair Display', Georgia, serif; font-size: 18px;
  }
  .insight-box p { font-size: 15px; line-height: 1.7; margin: 0; color: #F4F6F8; }

  .mini-insight {
      background: #F0FAF8;
      border-left: 5px solid #2A9D8F;
      padding: 12px 20px;
      border-radius: 0 8px 8px 0;
      margin: 6px 0 0 0;
      font-size: 13.5px;
      color: #2C3E50;
      line-height: 1.7;
  }
  .mini-insight strong { color: #0B2545; }

  /* ── legend pills ──────────────────────────────── */
  .legend-row { display: flex; gap: 16px; margin: 0 0 14px 0; flex-wrap: wrap; }
  .legend-pill {
      display: flex; align-items: center; gap: 7px;
      background: #F4F6F8; border-radius: 20px;
      padding: 5px 14px; font-size: 13px; font-weight: 600; color: #0B2545;
      border: 1px solid #DDE4EC;
  }
  .pill-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }

  /* ── divider ───────────────────────────────────── */
  hr { border-color: #DDE4EC !important; margin: 6px 0 24px 0 !important; }

  /* ── footer ────────────────────────────────────── */
  .footer {
      text-align: center; color: #5A6B7B; font-size: 13px;
      padding: 18px 0; border-top: 1px solid #D8DEE4; margin-top: 40px;
  }
  .footer a { color: #0B2545; text-decoration: none; font-weight: 600; }

  /* ── chart label override ──────────────────────── */
  .js-plotly-plot .plotly .g-xtitle,
  .js-plotly-plot .plotly .g-ytitle { font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df = load_and_clean_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚢 Dashboard Filters")
    st.caption("Every chart updates instantly when you change a filter below.")
    st.markdown("---")

    st.markdown("**📌 How to use this dashboard**")
    st.info(
        "1. Use the filters to narrow the passenger group you want to study.\n"
        "2. Scroll down — charts are arranged from broad overview → detailed breakdown.\n"
        "3. Each chart has a **How to read** tip and a **💡 Insight** below it.",
        icon="ℹ️",
    )
    st.markdown("---")

    selected_class = st.multiselect(
        "🎫 Passenger Class",
        options=["First Class", "Second Class", "Third Class"],
        default=["First Class", "Second Class", "Third Class"],
        help="First Class = upper deck, closer to lifeboats. Third Class = lower decks.",
    )
    selected_sex = st.multiselect(
        "🧑 Sex",
        options=["Female", "Male"],
        default=["Female", "Male"],
    )
    selected_port = st.multiselect(
        "⚓ Port of Embarkation",
        options=sorted(df["EmbarkedPort"].unique()),
        default=sorted(df["EmbarkedPort"].unique()),
        help="Cherbourg (France), Queenstown (Ireland), Southampton (England).",
    )
    age_range = st.slider(
        "🎂 Age Range",
        int(df["Age"].min()), int(df["Age"].max()),
        (int(df["Age"].min()), int(df["Age"].max())),
    )
    fare_range = st.slider(
        "💷 Fare Range (£)",
        float(df["Fare"].min()), float(df["Fare"].max()),
        (float(df["Fare"].min()), float(df["Fare"].max())),
    )
    selected_travel = st.multiselect(
        "👨‍👩‍👧 Travel Status",
        options=["Alone", "With Family"],
        default=["Alone", "With Family"],
    )
    st.markdown("---")
    st.caption("💡 Tip: Try filtering to **Female + First Class** then **Male + Third Class** to see the biggest survival gap.")

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
filtered = df[
    df["Pclass"].isin(selected_class)
    & df["Sex"].isin(selected_sex)
    & df["EmbarkedPort"].isin(selected_port)
    & df["Age"].between(*age_range)
    & df["Fare"].between(*fare_range)
    & df["TravelStatus"].isin(selected_travel)
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.image("banner.png", use_container_width=True)

st.markdown("""
<div style="text-align:center;padding:10px 0 4px 0;">
  <h1 style="font-size:32px;margin-bottom:4px;">RMS Titanic — Survival Analytics</h1>
  <p style="color:#5A6B7B;font-size:15px;margin:0;">
    Explore how <b>class</b>, <b>sex</b>, <b>age</b>, and <b>fare</b> shaped who lived and who perished.<br>
    Use the sidebar filters to drill into any passenger group.
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Empty-state guard
if filtered.empty:
    st.warning("⚠️ No passengers match the current filters. Widen the selections in the sidebar.")
    st.stop()

# ── KPI ROW ───────────────────────────────────────────────────────────────────
total         = len(filtered)
survivors     = int(filtered["SurvivedBin"].sum())
survival_rate = survivors / total * 100
female_rate   = (filtered.loc[filtered["Sex"] == "Female", "SurvivedBin"].mean() * 100
                 if (filtered["Sex"] == "Female").any() else 0)
male_rate     = (filtered.loc[filtered["Sex"] == "Male", "SurvivedBin"].mean() * 100
                 if (filtered["Sex"] == "Male").any() else 0)
avg_fare      = filtered["Fare"].mean()

st.markdown("### 📊 At a Glance — Current Filter Selection")
st.caption("These six numbers summarise all passengers matching your sidebar filters right now.")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("👥 Passengers",     f"{total:,}",          help="Total passengers in the filtered group.")
c2.metric("🟢 Survivors",      f"{survivors:,}",      help="How many survived out of the filtered group.")
c3.metric("📈 Survival Rate",  f"{survival_rate:.1f}%", help="% of filtered passengers who survived.")
c4.metric("♀ Female Survival", f"{female_rate:.1f}%", help="Survival rate among women in the filtered group.")
c5.metric("♂ Male Survival",   f"{male_rate:.1f}%",   help="Survival rate among men in the filtered group.")
c6.metric("💷 Avg Fare",       f"£{avg_fare:.2f}",    help="Average ticket price for the filtered group.")

# ── KEY INSIGHT CALLOUT ───────────────────────────────────────────────────────
fc_female_rate = df[(df["Pclass"] == "First Class") & (df["Sex"] == "Female")]["SurvivedBin"].mean() * 100
tc_male_rate   = df[(df["Pclass"] == "Third Class") & (df["Sex"] == "Male")]["SurvivedBin"].mean() * 100
gap            = fc_female_rate - tc_male_rate

st.markdown(f"""
<div class="insight-box">
  <h3>🔍 KEY INSIGHT — Survival was decided by class and sex, not chance.</h3>
  <p>A <b>First-Class woman</b> had a <b>{fc_female_rate:.0f}%</b> chance of surviving —
  nearly certain rescue. A <b>Third-Class man</b> had only <b>{tc_male_rate:.0f}%</b> —
  a stark <b>{gap:.0f}-point gap</b>. The "women and children first" protocol existed,
  but was unevenly enforced across decks. Class privilege was the strongest predictor of
  survivability; sex was a close second.</p>
</div>
""", unsafe_allow_html=True)

# ── SECTION 1: CLASS × SEX ────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <div class="section-header">
    <div class="section-icon">🗺️</div>
    <div>
      <p class="section-title">1 · Who Survived? — Breakdown by Class &amp; Sex</p>
      <p class="section-subtitle">The two most powerful predictors of survival on the Titanic were passenger class and sex.
      These two charts let you see both simultaneously.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns([1.05, 1], gap="large")

with col_a:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this heatmap:</strong>
      Each cell shows the <em>survival rate (%)</em> for that row (sex) + column (class) combination.
      <strong style="color:#2A9D8F;">Green = high survival</strong>,
      <strong style="color:#9B2226;">Red = low survival</strong>, white = ~50%.
      The darker the green, the better the odds. Compare rows to see the sex effect;
      compare columns to see the class effect.
    </div>
    """, unsafe_allow_html=True)

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
        title="Survival Rate Heatmap (%) — Each cell = % who survived",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=30),
        height=340,
        xaxis=dict(title="Passenger Class", title_font=dict(size=13, color="#0B2545")),
        yaxis=dict(title="Sex",             title_font=dict(size=13, color="#0B2545")),
    )
    fig.update_traces(textfont=dict(size=22, color="black", family="Georgia"))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this sunburst:</strong>
      Click any ring segment to zoom in. The <em>innermost ring</em> = passenger class;
      <em>middle ring</em> = sex; <em>outer ring</em> = survived (Yes/No).
      Segment size = number of passengers.
      <strong style="color:#2A9D8F;">Teal = survived</strong>,
      <strong style="color:#9B2226;">red = perished</strong>.
    </div>
    """, unsafe_allow_html=True)

    sb = filtered.groupby(["Pclass", "Sex", "Survived"], observed=True).size().reset_index(name="Count")
    fig = px.sunburst(
        sb, path=["Pclass", "Sex", "Survived"], values="Count",
        color="Survived", color_discrete_map=SURVIVAL_PALETTE,
    )
    fig.update_layout(
        title="Breakdown: Class → Sex → Survived (size = passenger count)",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)

f1_df = filtered[(filtered["Pclass"] == "First Class") & (filtered["Sex"] == "Female")]
m3_df = filtered[(filtered["Pclass"] == "Third Class") & (filtered["Sex"] == "Male")]
f1_rate = f1_df["SurvivedBin"].mean() * 100 if len(f1_df) > 0 else 0
m3_rate = m3_df["SurvivedBin"].mean() * 100 if len(m3_df) > 0 else 0

st.markdown(f"""
<div class="mini-insight">
💡 <strong>Being female in any class outperformed being male in the class above.</strong>
First-Class women survived at <strong>{f1_rate:.0f}%</strong> — near-certain rescue —
while Third-Class men had just <strong>{m3_rate:.0f}%</strong> odds.
The sunburst confirms Third Class carried the most passengers but yielded the fewest survivors.
Deck location and gate access shaped outcomes as much as any official protocol.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 2: AGE + FARE ─────────────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <div class="section-header">
    <div class="section-icon">📉</div>
    <div>
      <p class="section-title">2 · Did Age or Fare Make a Difference?</p>
      <p class="section-subtitle">Beyond class and sex, ticket price and passenger age both had measurable effects —
      but not always in the way you'd expect.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

col_c, col_d = st.columns(2, gap="large")

with col_c:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this histogram:</strong>
      Each bar shows how many passengers of that age existed.
      <strong style="color:#2A9D8F;">Teal bars = survived</strong>,
      <strong style="color:#9B2226;">red bars = perished</strong>.
      The mini box-plot at the top shows the median and spread.
      Taller teal bars at a given age = better odds for that age group.
      Hover a bar for exact counts.
    </div>
    """, unsafe_allow_html=True)

    fig = px.histogram(
        filtered, x="Age", color="Survived",
        nbins=30, barmode="overlay", opacity=0.78,
        color_discrete_map=SURVIVAL_PALETTE, marginal="box",
        labels={"Age": "Passenger Age (years)", "count": "Number of Passengers"},
    )
    fig.update_layout(
        title="Age Distribution — who survived at each age?",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=400, bargap=0.05,
        xaxis_title="Passenger Age (years)",
        yaxis_title="Number of Passengers",
        legend_title_text="Survived?",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this box plot:</strong>
      Each box shows the fare distribution for that class + survival group.
      The <em>line inside the box</em> = median fare; the box = middle 50% of passengers;
      the whiskers = full range; dots = outliers.
      Compare teal vs red boxes within the same class to see if spending more helped.
    </div>
    """, unsafe_allow_html=True)

    fig = px.box(
        filtered, x="Pclass", y="Fare", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE,
        category_orders={"Pclass": ["First Class", "Second Class", "Third Class"]},
        points="outliers",
        labels={"Pclass": "Passenger Class", "Fare": "Ticket Fare (£)"},
    )
    fig.update_layout(
        title="Fare Paid vs Survival — did a pricier ticket save you?",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=400,
        xaxis_title="Passenger Class",
        yaxis_title="Ticket Fare (£)",
        legend_title_text="Survived?",
    )
    st.plotly_chart(fig, use_container_width=True)

child_df = filtered[filtered["Age"] < 10]
child_surv = child_df["SurvivedBin"].mean() * 100 if len(child_df) > 0 else 0
median_fare_surv = filtered[filtered["Survived"] == "Yes"]["Fare"].median()
median_fare_died = filtered[filtered["Survived"] == "No"]["Fare"].median()

st.markdown(f"""
<div class="mini-insight">
💡 <strong>Age mattered most at the youngest end; fare mattered most inside First Class.</strong>
Children under 10 survived at <strong>{child_surv:.0f}%</strong> — "children first" had real weight.
Survivors paid a median fare of <strong>£{median_fare_surv:.1f}</strong> vs <strong>£{median_fare_died:.1f}</strong>
for those who perished. Yet in Third Class, the fare gap between survivors and non-survivors is negligible —
once on the lower decks, spending more made no further difference to your odds.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 3: FAMILY + EMBARKATION ──────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <div class="section-header">
    <div class="section-icon">👨‍👩‍👧</div>
    <div>
      <p class="section-title">3 · Did Travelling Together Help? &amp; Does Port Matter?</p>
      <p class="section-subtitle">Was it better to have family around in a crisis?
      And did where you boarded affect your chances?</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

col_e, col_f = st.columns(2, gap="large")

with col_e:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this combo chart:</strong>
      The <em>grey bars</em> (left axis) show how many passengers had each family size.
      The <em>gold line</em> (right axis) shows the survival rate (%) for that family size.
      Family size 1 = travelling alone. A peak in the gold line = best odds for that group size.
    </div>
    """, unsafe_allow_html=True)

    fam = (filtered.groupby("FamilySize")
           .agg(rate=("SurvivedBin", "mean"), count=("SurvivedBin", "size"))
           .reset_index())
    fam["rate"] *= 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=fam["FamilySize"], y=fam["count"],
               name="# Passengers", marker_color="#D8DEE4",
               hovertemplate="Family size %{x}<br>%{y} passengers<extra></extra>"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=fam["FamilySize"], y=fam["rate"],
                   name="Survival %", mode="lines+markers",
                   line=dict(color=COLOR_ACCENT, width=3),
                   marker=dict(size=10, line=dict(color=COLOR_PRIMARY, width=1)),
                   hovertemplate="Family size %{x}<br><b>%{y:.1f}%</b> survived<extra></extra>"),
        secondary_y=True,
    )
    fig.update_layout(
        title="Family Size vs Survival Rate — sweet spot at 2–4 members",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=400,
        xaxis_title="Family Size (including yourself)",
        legend=dict(orientation="h", y=1.08, x=0),
    )
    fig.update_yaxes(title_text="Number of Passengers", secondary_y=False)
    fig.update_yaxes(title_text="Survival Rate (%)", secondary_y=True, range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

with col_f:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this stacked bar:</strong>
      Each bar = one boarding port. Bar height = total passengers.
      <strong style="color:#2A9D8F;">Teal = survived</strong>,
      <strong style="color:#9B2226;">red = perished</strong>.
      The number labels show counts. To compare rates (not raw counts), look at the
      teal-to-red ratio within each bar — a taller teal section = better survival rate.
    </div>
    """, unsafe_allow_html=True)

    emb = (filtered.groupby(["EmbarkedPort", "Survived"])
           .size().reset_index(name="Count"))
    fig = px.bar(
        emb, x="EmbarkedPort", y="Count", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE, barmode="stack", text="Count",
        labels={"EmbarkedPort": "Port of Embarkation", "Count": "Number of Passengers"},
    )
    fig.update_layout(
        title="Survival by Port — Cherbourg had the best teal-to-red ratio",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=400,
        xaxis_title="Port of Embarkation",
        yaxis_title="Number of Passengers",
        legend_title_text="Survived?",
    )
    fig.update_traces(textposition="inside", textfont_color="white", textfont_size=13)
    st.plotly_chart(fig, use_container_width=True)

alone_rate    = fam.loc[fam["FamilySize"] == 1, "rate"].values[0] if 1 in fam["FamilySize"].values else 0
best_fam_size = int(fam.loc[fam["rate"].idxmax(), "FamilySize"]) if not fam.empty else 0
best_fam_rate = fam["rate"].max() if not fam.empty else 0
cherb_df      = filtered[filtered["EmbarkedPort"] == "Cherbourg"]
cherb_rate    = cherb_df["SurvivedBin"].mean() * 100 if len(cherb_df) > 0 else 0

st.markdown(f"""
<div class="mini-insight">
💡 <strong>Small families outlasted solo travellers; Cherbourg passengers fared best.</strong>
Travelling alone gave just <strong>{alone_rate:.0f}%</strong> survival odds, while a group of
<strong>{best_fam_size}</strong> reached <strong>{best_fam_rate:.0f}%</strong> —
companions likely helped claim lifeboat spots.
Very large groups (7+) saw odds collapse, overwhelmed by the chaos of coordinating evacuation together.
Cherbourg's <strong>{cherb_rate:.0f}%</strong> survival rate reflects its wealthier, First-Class–heavy
boarding mix — not any special advantage of the French port itself.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 4: TITLE + AGE GROUP ──────────────────────────────────────────────
st.markdown("""
<div class="section-card">
  <div class="section-header">
    <div class="section-icon">🎖️</div>
    <div>
      <p class="section-title">4 · The Title Effect — How Social Role Shaped Survival</p>
      <p class="section-subtitle">Titles on the manifest (Mr, Mrs, Miss, Master, Rare) encode sex, age, and social status
      all at once — making them a surprisingly powerful survival predictor.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

col_g, col_h = st.columns(2, gap="large")

with col_g:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this violin chart:</strong>
      Each "violin" shape shows the <em>age distribution</em> for that title.
      Fatter = more passengers of that age. The embedded box = median + interquartile range.
      <strong style="color:#2A9D8F;">Teal = survived</strong>,
      <strong style="color:#9B2226;">red = perished</strong>.
      Titles: <b>Master</b> = boys under ~13 · <b>Miss</b> = unmarried women · <b>Mrs</b> = married women ·
      <b>Mr</b> = adult men · <b>Rare</b> = officers, clergy, nobility, etc.
    </div>
    """, unsafe_allow_html=True)

    fig = px.violin(
        filtered, x="Title", y="Age", color="Survived",
        color_discrete_map=SURVIVAL_PALETTE, box=True, points=False,
        category_orders={"Title": ["Master", "Miss", "Mrs", "Mr", "Rare"]},
        labels={"Title": "Passenger Title", "Age": "Age (years)"},
    )
    fig.update_layout(
        title="Age by Title & Survival — Mr dominated in count but not luck",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=400,
        xaxis_title="Passenger Title",
        yaxis_title="Age (years)",
        legend_title_text="Survived?",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_h:
    st.markdown("""
    <div class="how-to-read">
      <strong>📖 How to read this bar chart:</strong>
      Each bar = one age group; bar height = survival rate (%).
      Colour grades from <strong style="color:#9B2226;">red (low %)</strong>
      to <strong style="color:#2A9D8F;">teal (high %)</strong>.
      The number above each bar = exact survival rate.
      Hover for details. Compare bars to see which age group fared best and worst.
    </div>
    """, unsafe_allow_html=True)

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
        title="Survival Rate by Age Group — children led, seniors suffered most",
        font=dict(family="Georgia, serif", size=13),
        margin=dict(l=10, r=10, t=55, b=10),
        height=400, yaxis_range=[0, 110],
        coloraxis_showscale=False,
        xaxis_title="Age Group",
        yaxis_title="Survival Rate (%)",
    )
    st.plotly_chart(fig, use_container_width=True)

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
💡 <strong>Boys and women were prioritised; adult men faced the worst odds at every age.</strong>
"Master" (boys under ~13) survived at <strong>{master_surv:.0f}%</strong>, while "Mr" —
the largest group by far — managed only <strong>{mr_surv:.0f}%</strong>.
By age, <strong>{top_age_group}</strong> had the highest rate at <strong>{top_age_rate:.0f}%</strong>;
<strong>{low_age_group}</strong> the lowest at <strong>{low_age_rate:.0f}%</strong>.
The "Rare" group (officers, clergy, nobility) shows the widest age spread —
a mix of duty-bound crew, older elites, and privileged exceptions.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── DATA EXPLORER ─────────────────────────────────────────────────────────────
with st.expander("📋 Browse the underlying passenger records (filtered)"):
    st.caption("This table reflects your current sidebar filter selection. You can download it as a CSV.")
    show_cols = ["Name", "Survived", "Pclass", "Sex", "Age", "Fare",
                 "FamilySize", "EmbarkedPort", "Title"]
    st.dataframe(filtered[show_cols], use_container_width=True, height=320)
    csv = filtered[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️  Download filtered data (CSV)",
        csv, "titanic_filtered.csv", "text/csv",
    )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <b>Data source:</b>
  <a href="https://www.kaggle.com/datasets/yasserh/titanic-dataset/data" target="_blank">
    Kaggle — Titanic Dataset
  </a>, derived from
  <a href="https://www.encyclopedia-titanica.org/" target="_blank">Encyclopedia Titanica</a>.
  Public-domain passenger manifest · 891 records · Streamlit + Plotly.
</div>
""", unsafe_allow_html=True)