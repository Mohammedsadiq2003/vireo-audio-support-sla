# Vireo Audio — SLA Breach Analyzer

## Purpose
A small working AI-assisted support analytics tool for the Vireo Audio Set D assignment.

It calculates first-response SLA breaches, joins the correct agent roster assignment by ticket date, summarizes results by shift/agent/channel, and quantifies SLA-credit exposure.

## SLA rules
- Chat: 15 minutes
- Voice: 2 hours
- Social: 4 hours
- Email: 8 hours
- SLA breach credit: Rs 350

## Run on Windows / Anaconda

```bash
conda create -n vireo-sla python=3.11 -y
conda activate vireo-sla
pip install -r requirements.txt
streamlit run app.py
```

Then upload `tickets.csv` and `agents.csv`.

## Validation

Run:

```bash
pytest -q
```

The included test checks that a chat response at 16 minutes is correctly classified as an SLA breach.

## Important implementation decisions
1. SLA is measured from `created_at` to `first_response_at`.
2. Roster is matched by `agent_id` AND the ticket creation date falling within the roster assignment dates.
3. Tier 2 agents are not ranked with Tier 1 on volume metrics because the supplied policy explicitly says Tier 2 should not be compared with Tier 1 on volume.
4. The application works without a paid LLM/API. The AI Assistant is deliberately deterministic for reliability and reproducibility; an optional LLM layer can be added later.
5. The analysis uses the policy's Rs 350 breach credit.

## Known limitations
- It does not model staffing changes or queue arrivals.
- It does not claim that correlation proves the cause of breaches.
- It does not calculate financial savings beyond SLA-credit exposure unless the assignment provides enough evidence for a staffing/business case.
