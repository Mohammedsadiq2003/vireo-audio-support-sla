import pandas as pd
from src.analysis import load_and_analyze

def test_chat_breach():
    tickets = pd.DataFrame([{
        "ticket_id":"T1","created_at":"2026-01-01 10:00",
        "first_response_at":"2026-01-01 10:16","channel":"chat","agent_id":"A1"
    }])
    agents = pd.DataFrame([{
        "agent_id":"A1","name":"Test","site":"Bengaluru","team":"Chat Frontline",
        "shift":"Morning","tier":1,"from_date":"2025-01-01","to_date":"2026-12-31"
    }])
    out = load_and_analyze(tickets, agents)
    assert bool(out.iloc[0]["sla_breach"]) is True
