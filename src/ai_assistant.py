def answer_question(question, df, summary):
    q = question.lower().strip()

    # -------------------------
    # SHIFT QUESTIONS
    # -------------------------
    if "shift" in q:
        data = (
            df.groupby("shift")
            .agg(
                tickets=("ticket_id", "count"),
                breaches=("sla_breach", "sum")
            )
            .reset_index()
        )

        data["breach_rate"] = (
            data["breaches"] / data["tickets"] * 100
        )

        # Highest breach rate
        if "highest" in q and "breach" in q:
            row = data.sort_values(
                "breach_rate", ascending=False
            ).iloc[0]

            return (
                f"{row['shift']} shift has the highest breach rate: "
                f"{int(row['breaches'])} breaches out of "
                f"{int(row['tickets'])} tickets "
                f"({row['breach_rate']:.2f}%)."
            )

        # Specific shift ticket count
        for shift in data["shift"].dropna().unique():
            if str(shift).lower() in q:
                row = data[
                    data["shift"].astype(str).str.lower() == str(shift).lower()
                ].iloc[0]

                if "ticket" in q:
                    return (
                        f"{shift} shift has "
                        f"{int(row['tickets'])} tickets."
                    )

                if "breach" in q:
                    return (
                        f"{shift} shift has "
                        f"{int(row['breaches'])} SLA breaches "
                        f"({row['breach_rate']:.2f}%)."
                    )

    # -------------------------
    # CHANNEL QUESTIONS
    # -------------------------
    if "channel" in q:
        data = (
            df.groupby("channel")
            .agg(
                tickets=("ticket_id", "count"),
                breaches=("sla_breach", "sum")
            )
            .reset_index()
        )

        data["breach_rate"] = (
            data["breaches"] / data["tickets"] * 100
        )

        if "highest" in q and "breach" in q:
            row = data.sort_values(
                "breach_rate", ascending=False
            ).iloc[0]

            return (
                f"{str(row['channel']).title()} has the highest breach rate: "
                f"{int(row['breaches'])} breaches out of "
                f"{int(row['tickets'])} tickets "
                f"({row['breach_rate']:.2f}%)."
            )

    # -------------------------
    # TOTAL SLA QUESTIONS
    # -------------------------
    if (
        ("total" in q or "how many" in q)
        and ("breach" in q or "breaches" in q)
    ):
        return (
            f"There are {summary['breaches']} SLA breaches "
            f"out of {summary['tickets']} tickets, "
            f"with an overall breach rate of "
            f"{summary['breach_rate'] * 100:.2f}%."
        )

    # -------------------------
    # AGENT QUESTIONS
    # -------------------------
    if "agent" in q:
        data = (
            df.groupby(["agent_id", "agent_name"])
            .agg(
                tickets=("ticket_id", "count"),
                breaches=("sla_breach", "sum")
            )
            .reset_index()
        )

        data["breach_rate"] = (
            data["breaches"] / data["tickets"] * 100
        )

        if "highest" in q and "breach" in q:
            row = data.sort_values(
                "breach_rate", ascending=False
            ).iloc[0]

            return (
                f"{row['agent_name']} ({row['agent_id']}) has "
                f"the highest breach rate: "
                f"{int(row['breaches'])} breaches out of "
                f"{int(row['tickets'])} tickets "
                f"({row['breach_rate']:.2f}%)."
            )

    return (
        "I can answer questions about SLA breaches, "
        "shifts, channels and agents."
    )