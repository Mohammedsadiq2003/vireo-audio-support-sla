# Submission Form Draft

## What did you build, and what business outcome does it move?
Built a working Streamlit SLA Breach Analyzer that calculates first-response breaches from ticket timestamps, joins the correct agent roster assignment, and reports breach concentration by agent, shift and channel. The observed breach rate is 21.62%. The target is 15%, which would mean approximately 783 fewer breaches and about Rs 274,050 lower SLA-credit exposure at Rs 350 per breach.

## What does one run cost, and what would a month cost at Vireo's volume?
The core tool uses pandas/Streamlit locally and no paid API calls, so the marginal run cost is Rs 0. At roughly 650 tickets/week, it can be run locally without per-ticket model charges. If an external LLM is later added, its API cost must be measured separately.

## How do you know it works?
The SLA calculation is validated against explicit policy thresholds. An automated test checks a 16-minute chat response as a breach against the 15-minute target. The analysis also exposes the calculated response time, SLA target and breach flag so outputs are auditable.

## Did you change, narrow, or push back on the client's ask?
Yes. I kept the scope to first-response SLA breaches by agent, shift and channel, because the brief asks for a breach report and the five-hour cap rewards a small working tool. I did not build a large forecasting or staffing optimization system.

## What is wrong with what you are handing us?
The tool identifies concentration, not root cause. It does not prove that staffing caused the Morning shift's higher breach rate. It also uses the supplied export as-is and does not attempt to reconstruct missing historical events beyond the provided timestamps.

## What did you deliberately leave out, and why?
I left out a complex LLM agent, predictive staffing model, and automated workflow integration. They add failure modes without being necessary to answer the client's immediate question.

## Anything you built or found that nobody asked for?
I added a simple validation test and an auditable analyzed-ticket export so a reviewer can inspect the SLA target, response time and breach flag.

## What did you use AI for?
AI assistance was used for project structure, code drafting and review. The delivered core calculation is deterministic and does not depend on a paid API, which keeps the tool reproducible.

## Someone picks this up on Monday and you are unreachable — three things to know
1. Run `pip install -r requirements.txt`, then `streamlit run app.py`.
2. Upload `tickets.csv` and `agents.csv`; the roster is matched by agent ID and assignment dates.
3. The main business finding is the Morning shift concentration; use the Agent and Shift tabs before making staffing decisions.

## Honest hours spent
5

## GitHub Repo Link
[ADD PUBLIC GITHUB URL]
