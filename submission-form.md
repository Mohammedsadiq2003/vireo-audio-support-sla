Vireo Audio Support SLA — Submission Form

1. What did you build, and what business outcome does it move?

I built a working Streamlit-based SLA Breach Analyzer for Vireo Audio. It calculates first-response SLA breaches and shows where breaches are concentrated by shift, channel, agent, and week.

The analysis covers 11,816 tickets. The observed breach rate is 21.62%, with 2,555 breaches.

At ₹350 SLA credit per breach, the current SLA-credit exposure is approximately ₹894,250.

The target is to reduce the breach rate to 15%. This would mean approximately 783 fewer breaches and about ₹274,050 lower SLA-credit exposure.

2. What does one run cost, and what would a month cost at Vireo's volume?

The core application runs locally using Python, pandas, and Streamlit and makes no paid API calls.

- Cost per run: ₹0 in API/model charges
- Volume: approximately 650 tickets/week
- Approximate monthly volume: 650 × 52 ÷ 12 ≈ 2,817 tickets/month
- Monthly API/model cost: ₹0

Local electricity/computing cost is not included.

3. How do you know it works?

The analysis was run against 11,816 tickets.

Validation includes:

- SLA thresholds are applied according to the supplied policy.
- A 16-minute Chat response is correctly classified as a breach against the 15-minute Chat SLA.
- The output exposes response time, SLA target, and breach status for auditability.
- Automated testing was added for the SLA calculation.

I do not have an independently labelled ground-truth dataset, so I am not claiming a statistical error rate.

A known limitation is that unusual source-data cases such as migrated/duplicate records or incomplete timestamps require data-quality review.

4. Did you change, narrow, or push back on the client's ask?

Yes. I narrowed the solution to first-response SLA breaches by agent, shift, channel, and week.

I deliberately avoided building a larger forecasting or staffing-optimization system because the immediate business question could be answered with a smaller, reproducible working tool within the assignment time limit.

5. What is wrong with what you are handing us?

The tool identifies where breaches are concentrated, but it does not prove root cause.

For example, the higher Morning-shift breach rate does not by itself prove that staffing caused the problem.

The analysis also depends on the quality of the supplied ticket timestamps and roster data.

6. What did you deliberately leave out, and why?

I deliberately left out:

- Predictive staffing models
- A complex LLM agent
- Automated workflow/ticketing integration
- Production deployment infrastructure

These were outside the immediate requirement and would introduce additional complexity and failure modes without being necessary to answer the core SLA question.

7. Anything you built or found that nobody asked for?

I added:

- Automated SLA validation
- An auditable analyzed-ticket output
- Breakdown by shift, channel, and agent
- A clear business-impact calculation linking breaches to SLA-credit exposure

8. What did you use AI for?

I used ChatGPT for project structure, code drafting, debugging, and code review.

AI was useful for accelerating implementation and reviewing the approach. I deliberately kept the core SLA calculation deterministic rather than depending on an LLM.

No paid AI/API calls were used in the delivered application.

Recording:

https://drive.google.com/file/d/1VxT-cVaXQDNzn9LUEc8m0P48NkY-TZq0/view?usp=sharing

9. Public Google Drive link

https://drive.google.com/file/d/1VxT-cVaXQDNzn9LUEc8m0P48NkY-TZq0/view?usp=sharing

10. Someone picks this up Monday and you are unreachable — three things to know

1. Install dependencies with "pip install -r requirements.txt", then run "streamlit run app.py".
2. Upload "tickets.csv" and "agents.csv"; the application applies the SLA policy and matches the effective roster assignment.
3. The main business finding is the high Morning-shift breach concentration. Use the Shift, Channel, and Agent views before making staffing decisions.

11. Honest hours spent

5 hours

12. GitHub Repo Link

https://github.com/Mohammedsadiq2003/vireo-audio-support-sla