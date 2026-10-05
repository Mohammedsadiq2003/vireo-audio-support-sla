import pandas as pd


SLA_MINUTES = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}


def _find_column(df, names, required=True):
    """Find a column using case-insensitive matching."""
    lookup = {str(c).strip().lower(): c for c in df.columns}

    for name in names:
        if name.lower() in lookup:
            return lookup[name.lower()]

    if required:
        raise ValueError(
            f"Required column not found. Expected one of: {names}. "
            f"Available columns: {list(df.columns)}"
        )

    return None


def _normalise_channel(value):
    value = str(value).strip().lower()

    if value in {"chat", "live chat"}:
        return "chat"
    if value in {"voice", "call", "phone"}:
        return "voice"
    if value in {"social", "social media"}:
        return "social"
    if value in {"email", "e-mail"}:
        return "email"

    return value


def _prepare_agents(agents):
    agents = agents.copy()

    agent_id_col = _find_column(
        agents,
        ["agent_id", "id"]
    )

    name_col = _find_column(
        agents,
        ["agent_name", "name"],
        required=False
    )

    shift_col = _find_column(
        agents,
        ["shift"],
        required=False
    )

    tier_col = _find_column(
        agents,
        ["tier"],
        required=False
    )

    from_col = _find_column(
        agents,
        ["from_date", "effective_from", "start_date"],
        required=False
    )

    to_col = _find_column(
        agents,
        ["to_date", "effective_to", "end_date"],
        required=False
    )

    rename = {
        agent_id_col: "agent_id"
    }

    if name_col:
        rename[name_col] = "agent_name"

    if shift_col:
        rename[shift_col] = "shift"

    if tier_col:
        rename[tier_col] = "tier"

    if from_col:
        rename[from_col] = "from_date"

    if to_col:
        rename[to_col] = "to_date"

    agents = agents.rename(columns=rename)

    if "agent_name" not in agents.columns:
        agents["agent_name"] = agents["agent_id"].astype(str)

    if "shift" not in agents.columns:
        agents["shift"] = "Unknown"

    if "tier" not in agents.columns:
        agents["tier"] = 1

    if "from_date" not in agents.columns:
        agents["from_date"] = pd.Timestamp("1900-01-01")

    if "to_date" not in agents.columns:
        agents["to_date"] = pd.Timestamp("2100-12-31")

    agents["from_date"] = pd.to_datetime(
        agents["from_date"],
        errors="coerce"
    ).dt.date

    agents["to_date"] = pd.to_datetime(
        agents["to_date"],
        errors="coerce"
    ).dt.date

    return agents[
        [
            "agent_id",
            "agent_name",
            "shift",
            "tier",
            "from_date",
            "to_date",
        ]
    ]


def _match_roster(tickets, agents):
    """Match each ticket to the effective roster assignment."""
    agents = _prepare_agents(agents)

    result = tickets.copy()

    result["_ticket_date"] = result["created_at"].dt.date

    result = result.reset_index(drop=False).rename(
        columns={"index": "_original_index"}
    )

    result = result.merge(
        agents,
        on="agent_id",
        how="left",
        suffixes=("", "_roster")
    )

    valid = (
        (result["_ticket_date"] >= result["from_date"])
        & (result["_ticket_date"] <= result["to_date"])
    )

    result["_valid_roster"] = valid

    # Keep the effective roster row where available.
    result = (
        result.sort_values(
            ["_original_index", "_valid_roster"],
            ascending=[True, False]
        )
        .drop_duplicates("_original_index")
        .sort_values("_original_index")
    )

    result = result.drop(
        columns=[
            "_ticket_date",
            "_valid_roster",
            "_original_index",
            "from_date",
            "to_date",
        ],
        errors="ignore"
    )

    return result.reset_index(drop=True)


def load_and_analyze(tickets, agents):
    """
    Calculate first-response SLA breaches and join the effective agent roster.
    Ticket timestamps are interpreted as UTC and converted to IST.
    """

    tickets = tickets.copy()

    ticket_id_col = _find_column(
        tickets,
        ["ticket_id", "id"]
    )

    created_col = _find_column(
        tickets,
        ["created_at", "created", "created_time"]
    )

    response_col = _find_column(
        tickets,
        [
            "first_response_at",
            "first_response",
            "first_response_time",
        ]
    )

    channel_col = _find_column(
        tickets,
        ["channel"]
    )

    agent_id_col = _find_column(
        tickets,
        ["agent_id", "resolving_agent_id"]
    )

    tickets = tickets.rename(
        columns={
            ticket_id_col: "ticket_id",
            created_col: "created_at",
            response_col: "first_response_at",
            channel_col: "channel",
            agent_id_col: "agent_id",
        }
    )

    # Parse timestamps as UTC, then convert to IST.
    tickets["created_at"] = pd.to_datetime(
        tickets["created_at"],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Asia/Kolkata")

    tickets["first_response_at"] = pd.to_datetime(
        tickets["first_response_at"],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Asia/Kolkata")

    tickets["channel"] = tickets["channel"].apply(
        _normalise_channel
    )

    tickets["response_minutes"] = (
        (
            tickets["first_response_at"]
            - tickets["created_at"]
        ).dt.total_seconds()
        / 60
    )

    tickets["sla_target_minutes"] = (
        tickets["channel"].map(SLA_MINUTES)
    )

    tickets["sla_breach"] = (
        tickets["response_minutes"]
        > tickets["sla_target_minutes"]
    )

    tickets["sla_breach"] = tickets["sla_breach"].fillna(False)

    tickets["sla_credit"] = (
        tickets["sla_breach"].astype(int) * 350
    )

    tickets = _match_roster(
        tickets,
        agents
    )

    # Derive shift from IST ticket creation time when needed.
    def shift_from_time(ts):
        if pd.isna(ts):
            return "Unknown"

        hour = ts.hour

        if 6 <= hour < 14:
            return "Morning"
        elif 14 <= hour < 22:
            return "Day"
        else:
            return "Night"

    if "shift" not in tickets.columns:
        tickets["shift"] = tickets["created_at"].apply(
            shift_from_time
        )

    tickets["shift"] = tickets["shift"].fillna(
        tickets["created_at"].apply(shift_from_time)
    )

    return tickets


def summarize(df):
    tickets = len(df)
    breaches = int(df["sla_breach"].sum())

    breach_rate = (
        breaches / tickets
        if tickets
        else 0
    )

    credit_exposure = float(
        df["sla_credit"].sum()
    )

    return {
        "tickets": tickets,
        "breaches": breaches,
        "breach_rate": breach_rate,
        "credit_exposure": credit_exposure,
    }


def weekly_summary(df):
    data = df.copy()

    data["week_start"] = (
        data["created_at"]
        .dt.tz_localize(None)
        .dt.to_period("W-MON")
        .dt.start_time
    )

    out = (
        data.groupby("week_start")
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
            credit_exposure=("sla_credit", "sum"),
        )
        .reset_index()
    )

    out["breach_rate"] = (
        out["breaches"]
        / out["tickets"]
    )

    return out


def weekly_shift_summary(df):
    data = df.copy()

    data["week_start"] = (
        data["created_at"]
        .dt.tz_localize(None)
        .dt.to_period("W-MON")
        .dt.start_time
    )

    out = (
        data.groupby(
            ["week_start", "shift"],
            dropna=False
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
            credit_exposure=("sla_credit", "sum"),
        )
        .reset_index()
    )

    out["breach_rate"] = (
        out["breaches"]
        / out["tickets"]
    )

    return out


def weekly_agent_summary(df):
    data = df.copy()

    data["week_start"] = (
        data["created_at"]
        .dt.tz_localize(None)
        .dt.to_period("W-MON")
        .dt.start_time
    )

    out = (
        data.groupby(
            [
                "week_start",
                "agent_id",
                "agent_name",
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

    out["breach_rate"] = (
        out["breaches"]
        / out["tickets"]
    )

    return out