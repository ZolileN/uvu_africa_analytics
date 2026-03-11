"""
app.py  —  UVU Africa Innovation Ecosystem Dashboard
══════════════════════════════════════════════════════
A multi-page Streamlit analytics dashboard that tells the story
of UVU Africa's impact on Africa's digital economy.

Pages
─────
  1. Executive Overview     — KPIs and headline metrics
  2. Startup Ecosystem      — Funding, sectors, countries, growth
  3. Talent Pipeline        — Graduates, placements, skills demand
  4. Ecosystem Partners     — Partner network by type and sector
  5. Innovation Trends      — Media mentions, topics, sentiment

Usage
─────
  streamlit run dashboard/app.py
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="UVU Africa | Ecosystem Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme & custom CSS ────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  /* ── Global ── */
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0f1e;
    color: #e8eaf0;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1630 0%, #0a0f1e 100%);
    border-right: 1px solid #1e2a45;
  }
  section[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #8b9ab5;
    padding: 6px 0;
    transition: color 0.2s;
  }
  section[data-testid="stSidebar"] .stRadio label:hover { color: #00e5a0; }

  /* ── Page title ── */
  .page-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.03em;
    line-height: 1.1;
    background: linear-gradient(135deg, #00e5a0 0%, #00b4d8 60%, #7b61ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
  }
  .page-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: #5a6a85;
    margin-bottom: 2rem;
    font-weight: 300;
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: linear-gradient(135deg, #111827 0%, #0d1f38 100%);
    border: 1px solid #1e3050;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00e5a0, #00b4d8);
  }
  .kpi-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5a6a85;
    margin-bottom: 0.5rem;
  }
  .kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #e8eaf0;
    line-height: 1;
  }
  .kpi-delta {
    font-size: 0.78rem;
    color: #00e5a0;
    margin-top: 0.4rem;
  }

  /* ── Section headers ── */
  .section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #c8d0e0;
    letter-spacing: -0.01em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e2a45;
  }

  /* ── Insight card ── */
  .insight-card {
    background: #0d1630;
    border: 1px solid #1e3050;
    border-left: 4px solid #00e5a0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    font-size: 0.88rem;
    color: #8b9ab5;
    line-height: 1.6;
  }
  .insight-card strong { color: #e8eaf0; }

  /* ── Divider ── */
  hr { border-color: #1e2a45 !important; margin: 1.5rem 0; }

  /* ── Plotly chart backgrounds ── */
  .js-plotly-plot .plotly .bg { fill: transparent !important; }

  /* ── Remove streamlit default padding ── */
  .block-container { padding-top: 2rem; padding-bottom: 2rem; }

  /* ── Brand badge ── */
  .brand-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00e5a0 0%, #00b4d8 100%);
    color: #0a0f1e;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 0.6rem;
  }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#8b9ab5", size=12),
    xaxis=dict(gridcolor="#1e2a45", zerolinecolor="#1e2a45", tickfont=dict(color="#5a6a85")),
    yaxis=dict(gridcolor="#1e2a45", zerolinecolor="#1e2a45", tickfont=dict(color="#5a6a85")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8b9ab5")),
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#00e5a0", "#00b4d8", "#7b61ff", "#ff6b6b", "#ffd166", "#06d6a0", "#118ab2"],
)

COLOR_SEQ = ["#00e5a0", "#00b4d8", "#7b61ff", "#ff6b6b", "#ffd166", "#06d6a0", "#118ab2", "#ef476f"]

# ── Data loader ───────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

@st.cache_data(ttl=3600)
def load_data():
    def read(name):
        path = os.path.join(DATA_DIR, f"{name}.csv")
        if os.path.exists(path):
            return pd.read_csv(path)
        st.warning(f"Dataset not found: {name}.csv — run the pipeline first.")
        return pd.DataFrame()

    programs = read("programs")
    startups = read("startups")
    talent   = read("talent_programs")
    partners = read("partners")
    news     = read("news_mentions")

    # Light normalisation
    if not news.empty and "date" in news.columns:
        news["date"] = pd.to_datetime(news["date"], errors="coerce")
        news["year"] = news["date"].dt.year

    if not talent.empty:
        talent["placement_rate"] = (
            talent["job_placements"] / talent["graduates"]
        ).round(2)

    return programs, startups, talent, partners, news


programs, startups, talent, partners, news = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="brand-badge">🌍 UVU Africa</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;"
        "color:#e8eaf0;margin:0 0 0.2rem 0;'>Ecosystem Intelligence</p>"
        "<p style='font-size:0.75rem;color:#3d4f6b;margin:0 0 1.5rem 0;'>Dashboard v1.0</p>",
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "📊  Executive Overview",
            "🚀  Startup Ecosystem",
            "🎓  Talent Pipeline",
            "🤝  Ecosystem Partners",
            "📰  Innovation Trends",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.72rem;color:#3d4f6b;line-height:1.6;'>"
        "Data refreshed by the automated pipeline.<br>"
        "Run <code style='color:#00e5a0;'>update_pipeline.py</code> to update.</p>",
        unsafe_allow_html=True,
    )

    # Pipeline report if available
    report_path = os.path.join(DATA_DIR, "pipeline_report.csv")
    if os.path.exists(report_path):
        rpt = pd.read_csv(report_path)
        if "last_updated" in rpt.columns:
            last = rpt["last_updated"].iloc[0]
            st.markdown(
                f"<p style='font-size:0.7rem;color:#3d4f6b;'>Last pipeline run:<br>"
                f"<span style='color:#00e5a0;'>{last}</span></p>",
                unsafe_allow_html=True,
            )


# ═════════════════════════════════════════════════════════════════════════════==
# PAGE 1 — EXECUTIVE OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════==

if isinstance(page, str) and "Executive Overview" in page:

    st.markdown('<div class="page-title">Innovation at Scale</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">How UVU Africa is building Africa\'s digital economy — '
        'one startup, one graduate, one partnership at a time.</div>',
        unsafe_allow_html=True,
    )

    # ── KPIs ──
    total_startups   = len(startups)
    active_startups  = int((startups["status"] == "Active").sum()) if not startups.empty else 0
    total_funding    = int(startups["funding_usd"].sum()) if not startups.empty else 0
    total_programs   = len(programs)
    total_partners   = len(partners)
    total_grads      = int(talent["graduates"].sum()) if not talent.empty else 0
    total_placed     = int(talent["job_placements"].sum()) if not talent.empty else 0
    avg_placement    = round(total_placed / total_grads * 100, 1) if total_grads > 0 else 0
    sectors_covered  = startups["sector"].nunique() if not startups.empty else 0

    def kpi(label, value, delta=""):
        delta_html = f'<div class="kpi-delta">↑ {delta}</div>' if delta else ""
        return (
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'{delta_html}</div>'
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Startups Supported", total_startups, f"{active_startups} active"), unsafe_allow_html=True)
    c2.markdown(kpi("Total Funding Tracked", f"${total_funding/1_000_000:.1f}M"), unsafe_allow_html=True)
    c3.markdown(kpi("Graduates Trained", f"{total_grads:,}", f"{avg_placement}% placed"), unsafe_allow_html=True)
    c4.markdown(kpi("Ecosystem Partners", total_partners, f"{total_programs} programmes"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Sector breakdown + Startup status ──
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<div class="section-header">Startups by Sector</div>', unsafe_allow_html=True)
        if not startups.empty:
            sec_df = startups.groupby("sector").agg(
                count=("startup_id", "count"),
                total_funding=("funding_usd", "sum"),
            ).reset_index().sort_values("count", ascending=True)

            fig = go.Figure(go.Bar(
                x=sec_df["count"],
                y=sec_df["sector"],
                orientation="h",
                marker=dict(
                    color=sec_df["count"],
                    colorscale=[[0, "#0d2040"], [1, "#00e5a0"]],
                    line=dict(width=0),
                ),
                text=sec_df["count"],
                textposition="outside",
                textfont=dict(color="#8b9ab5", size=11),
                hovertemplate="<b>%{y}</b><br>Startups: %{x}<extra></extra>",
            ))
            fig.update_layout(PLOTLY_THEME, height=320)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Startup Status Distribution</div>', unsafe_allow_html=True)
        if not startups.empty:
            status_df = startups["status"].value_counts().reset_index()
            status_df.columns = ["status", "count"]
            fig2 = go.Figure(go.Pie(
                labels=status_df["status"],
                values=status_df["count"],
                hole=0.65,
                marker=dict(colors=COLOR_SEQ, line=dict(color="#0a0f1e", width=2)),
                textinfo="label+percent",
                textfont=dict(color="#8b9ab5", size=11),
                hovertemplate="<b>%{label}</b>: %{value} startups<extra></extra>",
            ))
            fig2.add_annotation(
                text=f"<b>{total_startups}</b><br><span style='font-size:10px'>total</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="#e8eaf0"),
            )
            fig2.update_layout(PLOTLY_THEME, height=320, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # ── Row 3: Talent growth over time ──
    st.markdown('<div class="section-header">Talent Development — Graduates & Placements Over Time</div>', unsafe_allow_html=True)
    if not talent.empty:
        yr_talent = talent.groupby("year").agg(
            graduates=("graduates", "sum"),
            placed=("job_placements", "sum"),
        ).reset_index()

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=yr_talent["year"], y=yr_talent["graduates"],
            name="Graduates", mode="lines+markers",
            line=dict(color="#00b4d8", width=2.5),
            marker=dict(size=7, color="#00b4d8"),
            fill="tozeroy", fillcolor="rgba(0,180,216,0.07)",
        ))
        fig3.add_trace(go.Scatter(
            x=yr_talent["year"], y=yr_talent["placed"],
            name="Placed in Jobs", mode="lines+markers",
            line=dict(color="#00e5a0", width=2.5),
            marker=dict(size=7, color="#00e5a0"),
            fill="tozeroy", fillcolor="rgba(0,229,160,0.07)",
        ))
        fig3.update_layout(PLOTLY_THEME, height=250)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Insight cards ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)
    i1, i2, i3 = st.columns(3)
    i1.markdown(
        '<div class="insight-card"><strong>Dominant Sectors:</strong> FinTech, EdTech, and AI/ML '
        'account for the largest share of startups in UVU Africa\'s portfolio, '
        'reflecting the strongest growth areas across the continent.</div>',
        unsafe_allow_html=True,
    )
    i2.markdown(
        f'<div class="insight-card"><strong>Strong Talent Outcomes:</strong> With an average '
        f'placement rate of <strong>{avg_placement}%</strong>, UVU Africa\'s training programmes '
        f'consistently outperform the national graduate employment average.</div>',
        unsafe_allow_html=True,
    )
    i3.markdown(
        '<div class="insight-card"><strong>Ecosystem Depth:</strong> A diverse network of '
        'corporate, government, and academic partners gives UVU Africa unique convening power '
        'across the African innovation ecosystem.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — STARTUP ECOSYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

elif isinstance(page, str) and "Startup Ecosystem" in page:

    st.markdown('<div class="page-title">Startup Ecosystem</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Funding flows, sector concentration, and geographic spread '
        'across UVU Africa-supported ventures.</div>',
        unsafe_allow_html=True,
    )

    if startups.empty:
        st.warning("No startup data found. Run `generate_startups.py` first.")
        st.stop()

    # ── Filters ──
    with st.expander("🔍 Filter startups", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        sel_sector  = fc1.multiselect("Sector",  sorted(startups["sector"].unique()),  default=[])
        sel_country = fc2.multiselect("Country", sorted(startups["country"].unique()), default=[])
        sel_status  = fc3.multiselect("Status",  sorted(startups["status"].unique()),  default=[])

    df = startups.copy()
    if sel_sector:  df = df[df["sector"].isin(sel_sector)]
    if sel_country: df = df[df["country"].isin(sel_country)]
    if sel_status:  df = df[df["status"].isin(sel_status)]

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Startups", len(df))
    k2.metric("Total Funding", f"${df['funding_usd'].sum()/1_000_000:.1f}M")
    k3.metric("Avg Funding", f"${df['funding_usd'].mean():,.0f}")
    k4.metric("Sectors", df["sector"].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Funding by Sector ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Total Funding by Sector</div>', unsafe_allow_html=True)
        sec_fund = df.groupby("sector")["funding_usd"].sum().reset_index().sort_values("funding_usd", ascending=False)
        fig = px.bar(
            sec_fund, x="sector", y="funding_usd",
            color="funding_usd",
            color_continuous_scale=[[0, "#0d2040"], [1, "#00e5a0"]],
            labels={"funding_usd": "Total Funding (USD)", "sector": ""},
        )
        fig.update_traces(hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>")
        fig.update_layout(PLOTLY_THEME, height=320, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Startups by Country</div>', unsafe_allow_html=True)
        country_df = df["country"].value_counts().reset_index()
        country_df.columns = ["country", "count"]
        fig2 = px.bar(
            country_df, x="count", y="country", orientation="h",
            color="count",
            color_continuous_scale=[[0, "#0d2040"], [1, "#00b4d8"]],
            labels={"count": "Startups", "country": ""},
        )
        fig2.update_traces(hovertemplate="<b>%{y}</b><br>%{x} startups<extra></extra>")
        fig2.update_layout(PLOTLY_THEME, height=320, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Funding distribution + Growth over time ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Funding Distribution</div>', unsafe_allow_html=True)
        fig3 = px.histogram(
            df, x="funding_usd", nbins=30,
            labels={"funding_usd": "Funding (USD)", "count": "Startups"},
            color_discrete_sequence=["#7b61ff"],
        )
        fig3.update_traces(hovertemplate="$%{x:,.0f}<br>%{y} startups<extra></extra>")
        fig3.update_layout(PLOTLY_THEME, height=280)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Startups Founded Per Year</div>', unsafe_allow_html=True)
        yr_df = df.groupby("founded_year").size().reset_index(name="count")
        fig4 = go.Figure(go.Scatter(
            x=yr_df["founded_year"], y=yr_df["count"],
            mode="lines+markers",
            line=dict(color="#ffd166", width=2.5),
            marker=dict(size=7, color="#ffd166"),
            fill="tozeroy", fillcolor="rgba(255,209,102,0.07)",
            hovertemplate="<b>%{x}</b>: %{y} startups<extra></extra>",
        ))
        fig4.update_layout(PLOTLY_THEME, height=280)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Scatter: funding vs employees ──
    st.markdown('<div class="section-header">Funding vs. Team Size</div>', unsafe_allow_html=True)
    if "employees" in df.columns:
        fig5 = px.scatter(
            df, x="employees", y="funding_usd",
            color="sector", size="funding_usd",
            size_max=40,
            hover_data=["startup_name", "country", "status"],
            color_discrete_sequence=COLOR_SEQ,
            labels={"employees": "Team Size", "funding_usd": "Funding (USD)", "sector": "Sector"},
        )
        fig5.update_layout(PLOTLY_THEME, height=380)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Data table ──
    with st.expander("📋 View raw startup data"):
        st.dataframe(
            df[["startup_name", "sector", "country", "founded_year", "funding_usd", "status", "employees"]]
            .sort_values("funding_usd", ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
            height=300,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TALENT PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

elif isinstance(page, str) and "Talent Pipeline" in page:

    st.markdown('<div class="page-title">Talent Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">How UVU Africa is closing the digital skills gap — '
        'tracking graduates, placements, and in-demand skills year by year.</div>',
        unsafe_allow_html=True,
    )

    if talent.empty:
        st.warning("No talent data found. Check data/talent_programs.csv.")
        st.stop()

    # ── KPIs ──
    total_grads  = int(talent["graduates"].sum())
    total_placed = int(talent["job_placements"].sum())
    avg_rate     = round(talent["placement_rate"].mean() * 100, 1)
    num_programs = talent["program_name"].nunique()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Graduates", f"{total_grads:,}")
    k2.metric("Total Placements", f"{total_placed:,}")
    k3.metric("Avg Placement Rate", f"{avg_rate}%")
    k4.metric("Training Programmes", num_programs)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graduates & placements over time (by program) ──
    st.markdown('<div class="section-header">Graduates & Placements Over Time — by Programme</div>', unsafe_allow_html=True)
    yr_prog = talent.groupby(["year", "program_name"]).agg(
        graduates=("graduates", "sum"),
        placed=("job_placements", "sum"),
    ).reset_index()

    fig = px.line(
        yr_prog, x="year", y="graduates",
        color="program_name",
        markers=True,
        color_discrete_sequence=COLOR_SEQ,
        labels={"graduates": "Graduates", "year": "Year", "program_name": "Programme"},
    )
    fig.update_layout(PLOTLY_THEME, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # ── Placement rate + Skills demand ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Placement Rate by Programme</div>', unsafe_allow_html=True)
        prog_rate = talent.groupby("program_name")["placement_rate"].mean().reset_index()
        prog_rate["placement_pct"] = (prog_rate["placement_rate"] * 100).round(1)
        fig2 = go.Figure(go.Bar(
            x=prog_rate["program_name"],
            y=prog_rate["placement_pct"],
            marker=dict(
                color=prog_rate["placement_pct"],
                colorscale=[[0, "#0d2040"], [1, "#00e5a0"]],
                line=dict(width=0),
            ),
            text=prog_rate["placement_pct"].astype(str) + "%",
            textposition="outside",
            textfont=dict(color="#8b9ab5"),
            hovertemplate="<b>%{x}</b><br>Placement rate: %{y:.1f}%<extra></extra>",
        ))
        fig2.update_layout(PLOTLY_THEME, height=300, yaxis_title="Placement Rate (%)")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Top Skills Trained</div>', unsafe_allow_html=True)
        if "top_skill" in talent.columns:
            skill_df = talent["top_skill"].value_counts().reset_index()
            skill_df.columns = ["skill", "count"]
            fig3 = go.Figure(go.Bar(
                x=skill_df["count"],
                y=skill_df["skill"],
                orientation="h",
                marker=dict(
                    color=skill_df["count"],
                    colorscale=[[0, "#0d2040"], [1, "#7b61ff"]],
                    line=dict(width=0),
                ),
                text=skill_df["count"],
                textposition="outside",
                textfont=dict(color="#8b9ab5"),
                hovertemplate="<b>%{y}</b><br>%{x} programme runs<extra></extra>",
            ))
            fig3.update_layout(PLOTLY_THEME, height=300)
            st.plotly_chart(fig3, use_container_width=True)

    # ── Hiring sectors ──
    st.markdown('<div class="section-header">Where Graduates Are Hired</div>', unsafe_allow_html=True)
    if "hiring_sector" in talent.columns:
        hire_df = talent["hiring_sector"].value_counts().reset_index()
        hire_df.columns = ["sector", "count"]
        fig4 = px.pie(
            hire_df, names="sector", values="count",
            hole=0.5,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig4.update_traces(
            textinfo="label+percent",
            textfont=dict(color="#8b9ab5", size=11),
            hovertemplate="<b>%{label}</b>: %{value} programme runs<extra></extra>",
        )
        fig4.update_layout(PLOTLY_THEME, height=320, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Insight ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="insight-card"><strong>Pipeline Impact:</strong> UVU Africa\'s training '
        f'programmes have collectively produced <strong>{total_grads:,} graduates</strong>, with '
        f'<strong>{total_placed:,}</strong> successfully placed in tech roles — an average '
        f'placement rate of <strong>{avg_rate}%</strong> that reflects both programme quality '
        f'and strong corporate demand for African digital talent.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — ECOSYSTEM PARTNERS
# ═══════════════════════════════════════════════════════════════════════════════

elif isinstance(page, str) and "Ecosystem Partners" in page:

    st.markdown('<div class="page-title">Ecosystem Partners</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">The network of corporates, universities, and governments '
        'that power the UVU Africa innovation ecosystem.</div>',
        unsafe_allow_html=True,
    )

    if partners.empty:
        st.warning("No partner data found. Check data/partners.csv.")
        st.stop()

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Partners", len(partners))
    k2.metric("Corporate Partners", int((partners["partner_type"] == "Corporate").sum()))
    k3.metric("Academic Partners",  int((partners["partner_type"] == "University").sum()))
    k4.metric("Government Partners",int((partners["partner_type"] == "Government").sum()))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Partners by Type</div>', unsafe_allow_html=True)
        type_df = partners["partner_type"].value_counts().reset_index()
        type_df.columns = ["type", "count"]
        fig = go.Figure(go.Pie(
            labels=type_df["type"],
            values=type_df["count"],
            hole=0.6,
            marker=dict(colors=COLOR_SEQ, line=dict(color="#0a0f1e", width=2)),
            textinfo="label+percent",
            textfont=dict(color="#8b9ab5", size=11),
        ))
        fig.update_layout(PLOTLY_THEME, height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Partners by Sector</div>', unsafe_allow_html=True)
        sec_df = partners["sector"].value_counts().reset_index()
        sec_df.columns = ["sector", "count"]
        fig2 = go.Figure(go.Bar(
            x=sec_df["count"],
            y=sec_df["sector"],
            orientation="h",
            marker=dict(
                color=sec_df["count"],
                colorscale=[[0, "#0d2040"], [1, "#ffd166"]],
                line=dict(width=0),
            ),
            text=sec_df["count"],
            textposition="outside",
            textfont=dict(color="#8b9ab5"),
        ))
        fig2.update_layout(PLOTLY_THEME, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Partners table ──
    st.markdown('<div class="section-header">Full Partner Directory</div>', unsafe_allow_html=True)

    # Colour-code partner types
    type_colors = {
        "Corporate":  "🟢",
        "University": "🔵",
        "Government": "🟡",
        "NGO/Donor":  "🟠",
    }

    display_partners = partners.copy()
    display_partners["Type"] = display_partners["partner_type"].map(
        lambda t: f"{type_colors.get(t, '⚪')} {t}"
    )
    st.dataframe(
        display_partners[["partner_name", "Type", "sector", "country"]]
        .rename(columns={"partner_name": "Organisation", "sector": "Sector", "country": "Country"})
        .reset_index(drop=True),
        use_container_width=True,
        height=350,
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-card"><strong>Network Strength:</strong> UVU Africa\'s partner '
        'network spans corporate technology giants, leading South African universities, and '
        'government bodies — giving the ecosystem access to funding, talent pipelines, policy '
        'influence, and market reach simultaneously.</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — INNOVATION TRENDS
# ═══════════════════════════════════════════════════════════════════════════════

elif isinstance(page, str) and "Innovation Trends" in page:

    st.markdown('<div class="page-title">Innovation Trends</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">What the ecosystem is talking about — media coverage, '
        'topic frequency, and sentiment analysis across African tech publications.</div>',
        unsafe_allow_html=True,
    )

    if news.empty:
        st.warning("No news data found. Run `scrape_uvu_news.py` first.")
        st.stop()

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Articles Tracked", len(news))
    k2.metric("Sources", news["source"].nunique())
    k3.metric("Topics Covered", news["topic"].nunique())
    pos_pct = round((news["sentiment"] == "Positive").mean() * 100, 1) if "sentiment" in news.columns else 0
    k4.metric("Positive Sentiment", f"{pos_pct}%")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ── Articles per year ──
    with col1:
        st.markdown('<div class="section-header">Media Coverage Over Time</div>', unsafe_allow_html=True)
        if "year" in news.columns:
            yr_news = news.dropna(subset=["year"])
            yr_news["year"] = yr_news["year"].astype(int)
            yr_df = yr_news.groupby("year").size().reset_index(name="articles")
            fig = go.Figure(go.Bar(
                x=yr_df["year"],
                y=yr_df["articles"],
                marker=dict(
                    color=yr_df["articles"],
                    colorscale=[[0, "#0d2040"], [1, "#00b4d8"]],
                    line=dict(width=0),
                ),
                text=yr_df["articles"],
                textposition="outside",
                textfont=dict(color="#8b9ab5"),
                hovertemplate="<b>%{x}</b>: %{y} articles<extra></extra>",
            ))
            fig.update_layout(PLOTLY_THEME, height=300)
            st.plotly_chart(fig, use_container_width=True)

    # ── Topics ──
    with col2:
        st.markdown('<div class="section-header">Most Discussed Innovation Topics</div>', unsafe_allow_html=True)
        topic_df = news["topic"].value_counts().reset_index()
        topic_df.columns = ["topic", "count"]
        fig2 = go.Figure(go.Bar(
            x=topic_df["count"],
            y=topic_df["topic"],
            orientation="h",
            marker=dict(
                color=topic_df["count"],
                colorscale=[[0, "#0d2040"], [1, "#7b61ff"]],
                line=dict(width=0),
            ),
            text=topic_df["count"],
            textposition="outside",
            textfont=dict(color="#8b9ab5"),
            hovertemplate="<b>%{y}</b><br>%{x} articles<extra></extra>",
        ))
        fig2.update_layout(PLOTLY_THEME, height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Sources + sentiment ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Coverage by Source</div>', unsafe_allow_html=True)
        src_df = news["source"].value_counts().reset_index()
        src_df.columns = ["source", "count"]
        fig3 = go.Figure(go.Pie(
            labels=src_df["source"],
            values=src_df["count"],
            hole=0.55,
            marker=dict(colors=COLOR_SEQ, line=dict(color="#0a0f1e", width=2)),
            textinfo="label+percent",
            textfont=dict(color="#8b9ab5", size=11),
        ))
        fig3.update_layout(PLOTLY_THEME, height=300, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Sentiment Distribution</div>', unsafe_allow_html=True)
        if "sentiment" in news.columns:
            sent_df = news["sentiment"].value_counts().reset_index()
            sent_df.columns = ["sentiment", "count"]
            sent_colors = {"Positive": "#00e5a0", "Neutral": "#5a6a85", "Negative": "#ff6b6b"}
            colors = [sent_colors.get(s, "#8b9ab5") for s in sent_df["sentiment"]]
            fig4 = go.Figure(go.Bar(
                x=sent_df["sentiment"],
                y=sent_df["count"],
                marker=dict(color=colors, line=dict(width=0)),
                text=sent_df["count"],
                textposition="outside",
                textfont=dict(color="#8b9ab5"),
                hovertemplate="<b>%{x}</b>: %{y} articles<extra></extra>",
            ))
            fig4.update_layout(PLOTLY_THEME, height=300)
            st.plotly_chart(fig4, use_container_width=True)

    # ── Recent headlines ──
    st.markdown('<div class="section-header">Recent Headlines</div>', unsafe_allow_html=True)
    recent = news.dropna(subset=["date"]).sort_values("date", ascending=False).head(10)
    for _, row in recent.iterrows():
        date_str = str(row.get("date", ""))[:10]
        topic    = row.get("topic", "")
        source   = row.get("source", "")
        title    = row.get("title", "No title")
        st.markdown(
            f'<div class="insight-card">'
            f'<strong>{title}</strong><br>'
            f'<span style="color:#3d4f6b;">{source} &nbsp;·&nbsp; {date_str} &nbsp;·&nbsp; '
            f'<span style="color:#00e5a0;">{topic}</span></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-card"><strong>Narrative Shift:</strong> Analysis of media coverage '
        'shows a clear shift from general "innovation hub" stories toward specific themes of '
        '<strong>Digital Skills, AI/ML, and FinTech</strong> — signalling UVU Africa\'s growing '
        'influence in Africa\'s most strategic technology sectors.</div>',
        unsafe_allow_html=True,
    )