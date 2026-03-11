from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Somalia Drought Crisis",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# VISITOR COUNTER
# =========================================================
COUNTER_FILE = Path("visitor_counter.json")


def load_visitor_count() -> int:
    """Load total visitor count from local JSON file."""
    if COUNTER_FILE.exists():
        try:
            with open(COUNTER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return int(data.get("total_visitors", 0))
        except (json.JSONDecodeError, OSError, ValueError):
            return 0
    return 0


def save_visitor_count(count: int) -> None:
    """Save total visitor count to local JSON file."""
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump({"total_visitors": count}, f)


def get_ordinal(n: int) -> str:
    """Convert integer to ordinal string."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def register_visitor_once_per_session() -> int:
    """
    Register one visit per Streamlit session.
    Prevents reruns from incrementing the counter repeatedly.
    """
    if "visitor_number" not in st.session_state:
        total = load_visitor_count() + 1
        save_visitor_count(total)
        st.session_state["visitor_number"] = total
    return st.session_state["visitor_number"]


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #fef9e7 0%, #fdf3e0 100%);
        color: #2d2d2d;
    }
    .main-header {
        background: linear-gradient(135deg, #b33a3a 0%, #8b2c2c 100%);
        padding: 2rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        color: white;
    }
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    .visitor-card {
        background: #ffffff;
        border-left: 8px solid #2e86c1;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    .metric-card-critical {
        background: #ffffff;
        border-left: 8px solid #b33a3a;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .metric-card-warning {
        background: #ffffff;
        border-left: 8px solid #e68a2e;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .metric-card-info {
        background: #ffffff;
        border-left: 8px solid #2e86c1;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 1.1rem;
        color: #5f5f5f;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-context {
        font-size: 0.95rem;
        color: #7f7f7f;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px dashed #e0e0e0;
    }
    .callout-box {
        background: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        font-size: 1.1rem;
    }
    .testimonial-box {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin: 1rem 0;
        font-style: italic;
        border: 1px solid #f0f0f0;
    }
    .testimonial-author {
        font-weight: 600;
        margin-top: 1rem;
        color: #b33a3a;
        font-style: normal;
    }
    .funding-gap {
        background: linear-gradient(90deg, #b33a3a 0%, #e68a2e 50%, #2e86c1 100%);
        height: 30px;
        border-radius: 15px;
        margin: 1rem 0;
    }
    div[data-testid="stExpander"] {
        background: white;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA SOURCES & CONFIG
# =========================================================
DROUGHT_DATA = {
    "hunger": {
        "total_affected": 6500000,
        "crisis_level": 4500000,
        "emergency_level": 1800000,
        "catastrophe_level": 200000,
        "source": "UN OCHA / IPC FSNWG",
        "date": "February 2026",
        "trend": [
            {"month": "Oct 2025", "value": 4200000},
            {"month": "Dec 2025", "value": 5300000},
            {"month": "Feb 2026", "value": 6500000},
        ]
    },
    "malnutrition": {
        "total_children_affected": 1800000,
        "severe_malnutrition": 480000,
        "moderate_malnutrition": 1320000,
        "source": "UNICEF / WFP",
        "date": "January 2026",
    },
    "funding": {
        "wfp_recipients_2025": 2200000,
        "wfp_recipients_current": 600000,
        "wfp_funding_needed": 95000000,
        "un_response_plan": 852000000,
        "funding_received_pct": 16,
        "source": "WFP / UN OCHA",
        "date": "March 2026",
    },
    "displacement": {
        "total_displaced": 278000,
        "period": "July-Dec 2025",
        "source": "UNHCR / PRMN",
        "daily_new": 1500,
    },
    "water": {
        "distance_km": 30,
        "percent_livestock_loss": 60,
        "crop_failure_pct": 70,
        "source": "FAO / SWALIM",
    },
    "regions": [
        {"region": "Bay", "affected_pct": 85, "population_affected": 850000, "severity": "Emergency"},
        {"region": "Bakool", "affected_pct": 82, "population_affected": 420000, "severity": "Emergency"},
        {"region": "Gedo", "affected_pct": 78, "population_affected": 520000, "severity": "Crisis"},
        {"region": "Lower Shabelle", "affected_pct": 80, "population_affected": 950000, "severity": "Emergency"},
        {"region": "Middle Shabelle", "affected_pct": 70, "population_affected": 480000, "severity": "Crisis"},
        {"region": "Hiran", "affected_pct": 75, "population_affected": 350000, "severity": "Crisis"},
        {"region": "Mudug", "affected_pct": 65, "population_affected": 280000, "severity": "Crisis"},
        {"region": "Nugaal", "affected_pct": 60, "population_affected": 220000, "severity": "Stress"},
        {"region": "Bari", "affected_pct": 55, "population_affected": 380000, "severity": "Stress"},
        {"region": "Sool", "affected_pct": 62, "population_affected": 190000, "severity": "Crisis"},
        {"region": "Sanaag", "affected_pct": 58, "population_affected": 210000, "severity": "Stress"},
        {"region": "Togdheer", "affected_pct": 68, "population_affected": 320000, "severity": "Crisis"},
        {"region": "Woqooyi Galbeed", "affected_pct": 52, "population_affected": 450000, "severity": "Stress"},
        {"region": "Awdal", "affected_pct": 48, "population_affected": 280000, "severity": "Stress"},
    ]
}

TESTIMONIALS = [
    {
        "quote": "Our farms were destroyed, our livestock died, and water sources became too far away. We have nothing left to bring with us. We walked for days to reach this camp.",
        "author": "Abdiyo Ali",
        "location": "Mother displaced from Lower Shabelle",
        "source": "UNHCR Interview, January 2026"
    },
    {
        "quote": "Before the drought became severe, our animals were healthy and strong. Now they are weak and dying. We've lost 40 of our 50 goats. I don't know how we will survive.",
        "author": "Xaawo Maxamed Jama",
        "location": "Central Somalia",
        "source": "FAO Assessment, February 2026"
    },
    {
        "quote": "My children haven't eaten properly in days. There is no work, no food, no hope. We need help before it's too late.",
        "author": "Ahmed Nur",
        "location": "IDP Camp, Baidoa",
        "source": "Save the Children, March 2026"
    }
]

SOMALIA_CENTER = {"lat": 5.1521, "lon": 46.1996}
REGION_COORDS = {
    "Bay": {"lat": 2.85, "lon": 43.85},
    "Bakool": {"lat": 4.0, "lon": 43.5},
    "Gedo": {"lat": 3.0, "lon": 42.5},
    "Lower Shabelle": {"lat": 2.5, "lon": 44.5},
    "Middle Shabelle": {"lat": 3.5, "lon": 45.5},
    "Hiran": {"lat": 4.5, "lon": 45.5},
    "Mudug": {"lat": 6.5, "lon": 48.5},
    "Nugaal": {"lat": 8.0, "lon": 49.5},
    "Bari": {"lat": 10.5, "lon": 50.5},
    "Sool": {"lat": 8.5, "lon": 47.5},
    "Sanaag": {"lat": 10.0, "lon": 47.5},
    "Togdheer": {"lat": 9.0, "lon": 45.5},
    "Woqooyi Galbeed": {"lat": 9.5, "lon": 44.5},
    "Awdal": {"lat": 10.5, "lon": 43.5},
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def format_number(num: int) -> str:
    """Format large numbers with commas and M/K suffixes"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:,}"


def create_severity_map():
    """Create a choropleth map of drought severity by region"""
    df = pd.DataFrame(DROUGHT_DATA["regions"])

    df["lat"] = df["region"].map(lambda x: REGION_COORDS.get(x, {"lat": None})["lat"])
    df["lon"] = df["region"].map(lambda x: REGION_COORDS.get(x, {"lon": None})["lon"])

    severity_colors = {
        "Emergency": "#b33a3a",
        "Crisis": "#e68a2e",
        "Stress": "#f1c40f",
    }
    df["color"] = df["severity"].map(severity_colors)

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size="population_affected",
        color="severity",
        color_discrete_map=severity_colors,
        hover_name="region",
        hover_data={
            "affected_pct": ":.0f",
            "population_affected": True,
            "severity": True,
            "lat": False,
            "lon": False,
        },
        zoom=4.5,
        center=SOMALIA_CENTER,
        title="Drought Severity by Region",
        size_max=50,
        opacity=0.8,
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            title="Severity Level",
            orientation="h",
            yanchor="bottom",
            y=0.98,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
    )

    return fig


def create_trend_chart():
    """Create line chart showing hunger trend"""
    df = pd.DataFrame(DROUGHT_DATA["hunger"]["trend"])

    fig = px.line(
        df,
        x="month",
        y="value",
        markers=True,
        title="Rising Hunger: People Facing Crisis or Worse (IPC Phase 3+)",
        labels={"value": "People Affected", "month": ""},
    )

    fig.update_traces(
        line=dict(color="#b33a3a", width=4),
        marker=dict(size=10, color="#b33a3a"),
    )

    fig.update_layout(
        yaxis_tickformat=",.0f",
        yaxis_title="Number of People",
        plot_bgcolor="white",
        hovermode="x",
        margin=dict(l=60, r=20, t=60, b=40),
    )

    fig.update_yaxes(tickprefix=" ")

    return fig


def create_funding_chart():
    """Create funding gap visualization"""
    fig = go.Figure()

    received = DROUGHT_DATA["funding"]["un_response_plan"] * (
        DROUGHT_DATA["funding"]["funding_received_pct"] / 100
    )
    needed = DROUGHT_DATA["funding"]["un_response_plan"]
    gap = needed - received

    fig.add_trace(go.Bar(
        x=["Funds Needed", "Funds Received", "Funding Gap"],
        y=[needed, received, gap],
        marker_color=["#2e86c1", "#28b463", "#b33a3a"],
        text=[f"${needed/1e6:.0f}M", f"${received/1e6:.0f}M", f"${gap/1e6:.0f}M"],
        textposition="outside",
        textfont=dict(size=14),
    ))

    fig.update_layout(
        title="2026 Humanitarian Response Plan: Critical Funding Gap",
        yaxis_title="USD (Millions)",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=60, r=20, t=60, b=40),
        yaxis=dict(tickformat="$,.0f"),
    )

    return fig


def create_wfp_timeline():
    """Show WFP assistance cuts over time"""
    fig = go.Figure()

    categories = ["Early 2025", "Current (March 2026)"]
    values = [
        DROUGHT_DATA["funding"]["wfp_recipients_2025"],
        DROUGHT_DATA["funding"]["wfp_recipients_current"],
    ]

    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=["#2e86c1", "#b33a3a"],
        text=[f"{v/1e6:.1f}M" for v in values],
        textposition="outside",
        textfont=dict(size=14),
    ))

    fig.update_layout(
        title="WFP Food Assistance: Drastic Cuts Due to Funding Shortfalls",
        yaxis_title="People Receiving Assistance",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=60, r=20, t=60, b=40),
        yaxis=dict(tickformat=",.0f"),
    )

    return fig


# =========================================================
# MAIN APP
# =========================================================
def main():
    visitor_number = register_visitor_once_per_session()

    st.markdown("""
    <div class="main-header">
        <h1>💧 ABAARTII OOMAAN</h1>
        <h1>Somalia Drought Crisis</h1>
        <p>When a drought is given a name, it signals historic severity. "Abaartii Oomaan" or "Biyo La'aan ba'an" — the severe waterless drought.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="visitor-card">
        <div class="metric-label">Visitor Counter</div>
        <div class="metric-value">You are the {get_ordinal(visitor_number)} visitor</div>
        <div class="metric-context">Thank you for opening the dashboard and helping raise awareness.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Crisis at a Glance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card-critical">
            <div class="metric-label">People Facing Hunger</div>
            <div class="metric-value">{format_number(DROUGHT_DATA['hunger']['total_affected'])}</div>
            <div class="metric-context">IPC Phase 3+ (Crisis or worse)<br>↑ Double from 2025</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card-critical">
            <div class="metric-label">Children Malnourished</div>
            <div class="metric-value">{format_number(DROUGHT_DATA['malnutrition']['total_children_affected'])}</div>
            <div class="metric-context">{format_number(DROUGHT_DATA['malnutrition']['severe_malnutrition'])} severely malnourished</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card-warning">
            <div class="metric-label">Displaced People</div>
            <div class="metric-value">{format_number(DROUGHT_DATA['displacement']['total_displaced'])}</div>
            <div class="metric-context">July-Dec 2025 only<br>↑ 1,500 new displacements daily</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card-info">
            <div class="metric-label">Funding Gap</div>
            <div class="metric-value">${DROUGHT_DATA['funding']['un_response_plan']/1e6:.0f}M</div>
            <div class="metric-context">Only {DROUGHT_DATA['funding']['funding_received_pct']}% funded<br>WFP needs ${DROUGHT_DATA['funding']['wfp_funding_needed']/1e6:.0f}M urgently</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-box">
        <strong>🚨 URGENT: The window to prevent famine is closing.</strong><br>
        Without immediate funding, humanitarian operations will grind to a halt.
        WFP has already been forced to cut food assistance from <strong>2.2 million to just 600,000 people</strong>.
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.plotly_chart(create_severity_map(), use_container_width=True)

    with col_right:
        st.plotly_chart(create_trend_chart(), use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.plotly_chart(create_funding_chart(), use_container_width=True)

    with col_b:
        st.plotly_chart(create_wfp_timeline(), use_container_width=True)

    st.markdown("## Regional Impact")

    region_df = pd.DataFrame(DROUGHT_DATA["regions"])
    region_df["population_affected"] = region_df["population_affected"].apply(lambda x: f"{x/1000:.0f}K")
    region_df["affected_pct"] = region_df["affected_pct"].apply(lambda x: f"{x}%")

    st.dataframe(
        region_df.rename(columns={
            "region": "Region",
            "affected_pct": "Population Affected %",
            "population_affected": "People Affected",
            "severity": "IPC Severity Level",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("## 🗣️ Voices from the Drought")

    cols = st.columns(3)
    for i, testimonial in enumerate(TESTIMONIALS):
        with cols[i]:
            st.markdown(f"""
            <div class="testimonial-box">
                "{testimonial['quote']}"
                <div class="testimonial-author">— {testimonial['author']}</div>
                <div style="font-size:0.9rem; color:#7f7f7f;">{testimonial['location']}</div>
                <div style="font-size:0.8rem; color:#9f9f9f; margin-top:0.5rem;">{testimonial['source']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## 💧 Water Access & Livelihoods")

    col_w1, col_w2, col_w3 = st.columns(3)

    with col_w1:
        st.markdown(f"""
        <div class="metric-card-warning">
            <div class="metric-label">Distance to Water</div>
            <div class="metric-value">{DROUGHT_DATA['water']['distance_km']} km</div>
            <div class="metric-context">Families walk up to 30km (18.6 miles) for water</div>
        </div>
        """, unsafe_allow_html=True)

    with col_w2:
        st.markdown(f"""
        <div class="metric-card-critical">
            <div class="metric-label">Livestock Loss</div>
            <div class="metric-value">{DROUGHT_DATA['water']['percent_livestock_loss']}%</div>
            <div class="metric-context">of herds have died - the backbone of rural livelihoods</div>
        </div>
        """, unsafe_allow_html=True)

    with col_w3:
        st.markdown(f"""
        <div class="metric-card-critical">
            <div class="metric-label">Crop Failure</div>
            <div class="metric-value">{DROUGHT_DATA['water']['crop_failure_pct']}%</div>
            <div class="metric-context">of agricultural land affected</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #fef9e7 0%, #fdf3e0 100%); border-radius: 20px; margin: 2rem 0;">
        <h2 style="color: #b33a3a; font-size: 2.2rem; margin-bottom: 1rem;">🇸🇴 ACT NOW</h2>
        <p style="font-size: 1.3rem; max-width: 800px; margin: 0 auto 2rem auto;">
            The people of Somalia cannot wait. Every day of inaction costs lives.
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <a href="https://sharethemeal.org/en-us/campaigns/somalia1" target="_blank">
                <button style="background: #b33a3a; color: white; border: none; padding: 1rem 2.5rem; border-radius: 50px; font-size: 1.2rem; font-weight: 600; cursor: pointer; box-shadow: 0 8px 20px rgba(179,58,58,0.3);">
                    DONATE TO WFP →
                </button>
            </a>
            <a href="https://www.unicef.org/somalia/take-action" target="_blank">
                <button style="background: #2e86c1; color: white; border: none; padding: 1rem 2.5rem; border-radius: 50px; font-size: 1.2rem; font-weight: 600; cursor: pointer; box-shadow: 0 8px 20px rgba(46,134,193,0.3);">
                    SUPPORT UNICEF →
                </button>
            </a>
            <a href="https://www.savethechildren.org/us/where-we-work/somalia" target="_blank">
                <button style="background: #e68a2e; color: white; border: none; padding: 1rem 2.5rem; border-radius: 50px; font-size: 1.2rem; font-weight: 600; cursor: pointer; box-shadow: 0 8px 20px rgba(230,138,46,0.3);">
                    HELP SAVE THE CHILDREN →
                </button>
            </a>
        </div>
        <p style="margin-top: 2rem; color: #5f5f5f;">
            Share this dashboard to raise awareness: <strong>#SomaliaDrought2026 #ActNow</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(" Data Sources & Methodology"):
        st.markdown("""
        **All data is sourced from official humanitarian organizations (March 2026):**

        - **IPC FSNWG (Food Security and Nutrition Working Group):** Hunger estimates and projections
        - **UN OCHA:** Humanitarian Response Plan and funding tracking
        - **WFP (World Food Programme):** Food assistance data and funding requirements
        - **UNICEF:** Child malnutrition statistics
        - **FAO / SWALIM:** Water access, livestock, and crop data
        - **UNHCR / PRMN:** Displacement tracking
        - **Somalia Disaster Management Agency (SoDMA):** Regional impact assessments

        *Last updated: March 11, 2026*

        **Methodology Note:** Regional severity levels are based on IPC classifications:
        - **Emergency (IPC Phase 4):** Extreme food gaps, excess mortality
        - **Crisis (IPC Phase 3):** Significant food gaps, acute malnutrition
        - **Stress (IPC Phase 2):** Minimal adequate food consumption
        """)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8f8f8f; font-size: 0.9rem; padding: 1rem;">
        Built with 💔 for the people of Somalia • Data visualizations for advocacy • Use freely to raise awareness
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()