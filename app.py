import pandas as pd
import streamlit as st

from src.analysis import (
    load_and_analyze,
    summarize,
    weekly_summary,
    weekly_shift_summary,
    weekly_agent_summary,
)
from src.ai_assistant import answer_question


st.set_page_config(
    page_title="Vireo SLA Breach Analyzer",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 Vireo Audio — SLA Breach Analyzer")
st.caption("Support SLA analysis for the Vireo Audio Set D assignment")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Data")

    tickets_file = st.file_uploader(
        "Upload tickets.csv",
        type=["csv"]
    )

    agents_file = st.file_uploader(
        "Upload agents.csv",
        type=["csv"]
    )

    st.divider()

    st.info(
        "Targets: Chat 15m · Voice 2h · Social 4h · Email 8h"
    )


# ============================================================
# FILE CHECK
# ============================================================

if not tickets_file or not agents_file:
    st.warning(
        "Upload tickets.csv and agents.csv to start."
    )
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

tickets = pd.read_csv(tickets_file)
agents = pd.read_csv(agents_file)

df = load_and_analyze(
    tickets,
    agents
)

s = summarize(df)


# ============================================================
# OVERVIEW METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Tickets",
    f"{s['tickets']:,}"
)

c2.metric(
    "SLA breaches",
    f"{s['breaches']:,}"
)

c3.metric(
    "Breach rate",
    f"{s['breach_rate'] * 100:.2f}%"
)

c4.metric(
    "SLA credit exposure",
    f"₹{s['credit_exposure']:,.0f}"
)


# ============================================================
# BUSINESS TARGET
# ============================================================

st.subheader("Business target")

target = 15

current = s["breach_rate"] * 100

reduction = max(
    0,
    s["breaches"]
    - round(s["tickets"] * target / 100)
)

saving = reduction * 350

st.write(
    f"Reduce breach rate from "
    f"*{current:.2f}% to {target}%* "
    f"→ approximately *{reduction:,} fewer breaches* "
    f"and *₹{saving:,.0f} avoided SLA-credit exposure* "
    f"at ₹350 per breach."
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Shift",
        "Agent",
        "Channel",
        "Weekly Report",
        "AI Assistant",
    ]
)


# ============================================================
# SHIFT
# ============================================================

with tab1:

    st.subheader("SLA Performance by Shift")

    shift = (
        df.groupby(
            "shift",
            dropna=False
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
            credit_exposure=("sla_credit", "sum"),
        )
        .reset_index()
    )

    shift["breach_rate_%"] = (
        shift["breaches"]
        / shift["tickets"]
        * 100
    )

    shift = shift.sort_values(
        "breach_rate_%",
        ascending=False
    )

    st.dataframe(
        shift,
        use_container_width=True
    )

    st.bar_chart(
        shift.set_index("shift")[
            "breach_rate_%"
        ]
    )


# ============================================================
# AGENT
# ============================================================

with tab2:

    st.subheader("SLA Performance by Agent")

    # Tier 1 only for volume comparison,
    # as required by the support policy.
    agent_df = df[
        df["tier"].astype(str).str.strip() == "1"
    ]

    agent = (
        agent_df.groupby(
            [
                "agent_id",
                "agent_name",
                "shift",
            ],
            dropna=False
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
            credit_exposure=("sla_credit", "sum"),
        )
        .reset_index()
    )

    agent["breach_rate_%"] = (
        agent["breaches"]
        / agent["tickets"]
        * 100
    )

    agent = agent.sort_values(
        "breach_rate_%",
        ascending=False
    )

    st.dataframe(
        agent,
        use_container_width=True
    )


# ============================================================
# CHANNEL
# ============================================================

with tab3:

    st.subheader("SLA Performance by Channel")

    channel = (
        df.groupby(
            "channel",
            dropna=False
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
            credit_exposure=("sla_credit", "sum"),
        )
        .reset_index()
    )

    channel["breach_rate_%"] = (
        channel["breaches"]
        / channel["tickets"]
        * 100
    )

    channel = channel.sort_values(
        "breach_rate_%",
        ascending=False
    )

    st.dataframe(
        channel,
        use_container_width=True
    )

    st.bar_chart(
        channel.set_index("channel")[
            "breach_rate_%"
        ]
    )


# ============================================================
# WEEKLY REPORT
# ============================================================

with tab4:

    st.subheader("Weekly SLA Report")

    st.caption(
        "Weekly reporting starts on Monday and supports "
        "management review of SLA breaches."
    )


    # --------------------------------------------------------
    # Weekly overall
    # --------------------------------------------------------

    st.markdown("### 1. Weekly Overall Performance")

    weekly = weekly_summary(df)

    weekly_display = weekly.copy()

    weekly_display["week_start"] = (
        weekly_display["week_start"]
        .dt.strftime("%Y-%m-%d")
    )

    weekly_display["breach_rate_%"] = (
        weekly_display["breach_rate"] * 100
    ).round(2)

    weekly_display = weekly_display[
        [
            "week_start",
            "tickets",
            "breaches",
            "breach_rate_%",
            "credit_exposure",
        ]
    ]

    st.dataframe(
        weekly_display,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Weekly breach-rate chart
    # --------------------------------------------------------

    st.markdown("### Weekly Breach Rate")

    weekly_chart = weekly.copy()

    weekly_chart["breach_rate_%"] = (
        weekly_chart["breach_rate"] * 100
    )

    weekly_chart = weekly_chart.set_index(
        "week_start"
    )

    st.line_chart(
        weekly_chart["breach_rate_%"]
    )


    # --------------------------------------------------------
    # Weekly + Shift
    # --------------------------------------------------------

    st.markdown("### 2. Weekly Performance by Shift")

    weekly_shift = weekly_shift_summary(df)

    weekly_shift_display = weekly_shift.copy()

    weekly_shift_display["week_start"] = (
        weekly_shift_display["week_start"]
        .dt.strftime("%Y-%m-%d")
    )

    weekly_shift_display["breach_rate_%"] = (
        weekly_shift_display["breach_rate"] * 100
    ).round(2)

    weekly_shift_display = weekly_shift_display[
        [
            "week_start",
            "shift",
            "tickets",
            "breaches",
            "breach_rate_%",
            "credit_exposure",
        ]
    ]

    st.dataframe(
        weekly_shift_display,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Weekly + Agent
    # --------------------------------------------------------

    st.markdown("### 3. Weekly Performance by Agent")

    weekly_agent = weekly_agent_summary(df)

    weekly_agent_display = weekly_agent.copy()

    weekly_agent_display["week_start"] = (
        weekly_agent_display["week_start"]
        .dt.strftime("%Y-%m-%d")
    )

    weekly_agent_display["breach_rate_%"] = (
        weekly_agent_display["breach_rate"] * 100
    ).round(2)

    weekly_agent_display = weekly_agent_display[
        [
            "week_start",
            "agent_id",
            "agent_name",
            "tickets",
            "breaches",
            "breach_rate_%",
            "credit_exposure",
        ]
    ]

    st.dataframe(
        weekly_agent_display,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Download weekly reports
    # --------------------------------------------------------

    st.markdown("### Download Reports")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.download_button(
            "Download Weekly Report",
            weekly_display.to_csv(
                index=False
            ).encode("utf-8"),
            "vireo_weekly_report.csv",
            "text/csv",
        )

    with col2:

        st.download_button(
            "Download Weekly Shift Report",
            weekly_shift_display.to_csv(
                index=False
            ).encode("utf-8"),
            "vireo_weekly_shift_report.csv",
            "text/csv",
        )

    with col3:

        st.download_button(
            "Download Weekly Agent Report",
            weekly_agent_display.to_csv(
                index=False
            ).encode("utf-8"),
            "vireo_weekly_agent_report.csv",
            "text/csv",
        )


# ============================================================
# AI ASSISTANT
# ============================================================

with tab5:

    st.subheader("AI Assistant")

    question = st.text_input(
        "Ask about the support data",
        "Which shift should management focus on?"
    )

    if st.button("Analyze"):

        st.write(
            answer_question(
                question,
                df,
                s
            )
        )


# ============================================================
# DOWNLOAD FULL ANALYZED DATA
# ============================================================

st.divider()

st.download_button(
    "Download analyzed tickets CSV",
    df.to_csv(
        index=False
    ).encode("utf-8"),
    "vireo_analyzed_tickets.csv",
    "text/csv",
)