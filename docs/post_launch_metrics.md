# Post-Launch Metrics Framework
## Patient Acquisition & Growth Agent — Meridian Health System

The goal post-launch is not to prove the model works. It is to detect when it stops working, understand why, and act before the clinical team loses trust in it. These metrics are grouped by what they tell you, not by where the data comes from.

---

## 1. Model Performance (Is the AI still accurate?)

| Metric | Target | Alert Threshold | Cadence |
|--------|--------|-----------------|---------|
| Overall AUC on live predictions | ≥ 0.85 | < 0.80 | Weekly |
| Recall by demographic cohort (Hispanic, Black) | Within 5% of overall | > 8% gap | Weekly |
| Prediction confidence distribution | Stable vs. baseline | Shift > 10% | Weekly |
| Feature drift score | < 0.1 PSI | > 0.2 PSI | Weekly |

**Why these:** AUC tells you global accuracy. Cohort recall catches fairness degradation before it becomes a regulatory issue. Confidence distribution and feature drift catch data pipeline changes that silently corrupt predictions without triggering errors.

The demographic recall gap is the metric I would never let slip past an alert. A 12-point gap at baseline was already a known risk — any widening post-launch is a patient harm risk, not just a model quality issue.

---

## 2. Business Outcomes (Is the AI creating value?)

| Metric | Baseline (pre-AI) | Target | Cadence |
|--------|-------------------|--------|---------|
| Appointment conversion rate (referral → booked) | Establish in pilot | +15% | Monthly |
| Patient no-show rate | Establish in pilot | −20% | Monthly |
| Time to first appointment (referral → seen) | Establish in pilot | −2 days | Monthly |
| Referral pipeline volume (new patients identified) | Establish in pilot | +10% | Monthly |
| Revenue per AI-assisted scheduling slot | Establish in pilot | Positive | Quarterly |

**Why these:** These are the metrics the CTO will ask about in the 90-day review. Model accuracy is a means. Conversion rate, no-show reduction, and time-to-appointment are the ends. If accuracy holds but business metrics don't move, the problem is adoption, not the model.

---

## 3. System Reliability (Is the infrastructure holding?)

| Metric | Target | Alert Threshold | Cadence |
|--------|--------|-----------------|---------|
| API uptime | ≥ 99.9% | < 99.5% | Real-time |
| Inference latency P95 | < 2 seconds | > 3 seconds | Real-time |
| EHR sync error rate | < 0.1% | > 0.5% | Daily |
| Failed appointment recommendations (EHR rejection) | < 1% | > 2% | Daily |

**Why these:** Latency and uptime are hygiene. The EHR rejection rate is the one that matters operationally — if the model is recommending slots the EHR rejects as unavailable, coordinators see errors on every use. That erodes trust faster than any accuracy gap.

---

## 4. Clinical Adoption (Are people actually using it?)

| Metric | Target | Watch Level | Cadence |
|--------|--------|-------------|---------|
| AI recommendation acceptance rate | ≥ 70% | < 50% | Weekly |
| Override rate with documented reason | Track only | Spike > 30% | Weekly |
| Active users / total trained staff | ≥ 90% | < 70% | Weekly |
| Time spent per recommendation review | Establish baseline | +50% vs. baseline | Monthly |

**Why these:** Acceptance rate below 50% means coordinators are routing around the AI — the system is running but not working. Override rate with reason codes is more valuable than raw overrides: it tells you whether staff are disagreeing with the model intelligently (good signal) or ignoring it habitually (adoption failure).

The time-per-review metric catches a subtler problem: if coordinators are spending more time reviewing AI recommendations than they spent making decisions manually, the tool is creating work, not reducing it.

---

## 5. Patient & Privacy (Are we operating safely and ethically?)

| Metric | Target | Cadence |
|--------|--------|---------|
| PHI exposure incidents | 0 | Real-time |
| Patient consent opt-out rate | < 5% | Monthly |
| Patient satisfaction score (AI-assisted scheduling) | ≥ 4.0 / 5.0 | Quarterly |
| HIPAA audit findings | 0 critical | Per audit |

---

## Review Cadence

| Review | Audience | Frequency |
|--------|----------|-----------|
| Operational health | PM + Technical Lead | Weekly |
| Model performance + fairness | Data science + CMO | Bi-weekly |
| Business outcomes | CTO + Clinical Ops | Monthly |
| Full post-launch review | Steering committee | 30 / 60 / 90 days |

**The 30-day review is the most important one.** It is the first real signal of whether the model is performing in production conditions, whether adoption is happening, and whether the EHR integration is stable under real load. Any metric in alert state at 30 days needs a remediation plan before the 60-day review — not after.
