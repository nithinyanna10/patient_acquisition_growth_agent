# Stakeholder Map
## Patient Acquisition & Growth Agent — Meridian Health System

---

## Stakeholder Grid

| Stakeholder | Role | Influence | Interest | Engagement Mode |
|-------------|------|-----------|----------|-----------------|
| CTO | Executive sponsor, go-live authority | High | Medium | Weekly steering; escalation only |
| CMO / Chief Medical Officer | Clinical sign-off, physician alignment | High | High | Bi-weekly; owns validation gate |
| Physician Champion (Dr. Joffe) | Clinical validation, peer credibility | High | High | Weekly; co-owns model review |
| Scheduling Coordinators | Day-to-day users of AI recommendations | Medium | High | Change management; early pilot |
| IT / InfoSec | Infrastructure, credentials, firewall | High | Low | Tactical; unblock credentials |
| EHR Team (Epic Liaison) | API access, sandbox, rate limits | High | Low | Managed; tracked as dependency |
| Compliance / Privacy Officer | HIPAA, BAA, data governance | High | Medium | Bi-weekly; owns compliance gate |
| Legal Counsel | Liability agreement, DPA | Medium | Low | Async until contract execution |
| Clinical Operations Lead | Journey mapping, workflow design | Medium | High | Weekly; owns 38 patient touchpoints |
| Program Manager (Sarah Okonkwo) | Delivery coordination, steering comms | — | — | Accountable for all of the above |
| Patients | Indirect; consent and opt-out rights | Low | Low | One-way: consent workflow only |

---

## Influence / Interest Map

```
HIGH INFLUENCE
     │
     │  IT/InfoSec          CTO
     │  EHR Team            CMO
     │  Compliance          Physician Champion
     │
     │  Legal               Clinical Ops Lead
     │                      Scheduling Coordinators
     │
LOW  │──────────────────────────────────────────
     │  Patients
     │
     LOW INTEREST                     HIGH INTEREST
```

**Manage closely (high influence, high interest):** CMO, Physician Champion, Clinical Ops Lead
**Keep satisfied (high influence, lower interest):** CTO, IT/InfoSec, EHR Team, Compliance
**Keep informed (lower influence, high interest):** Scheduling Coordinators
**Monitor (low influence, low interest):** Legal (until contract), Patients

---

## Engagement Risks

**Scheduling coordinators** are the highest adoption risk. They are high-interest but have no formal power — meaning resistance shows up as workarounds, not objections. Mitigation: embed change champions from this group in the pilot, position the AI as decision-support with a visible override mechanism, not automation.

**IT/InfoSec** are high-influence but have low intrinsic interest in the project succeeding. Their blockers (credentials, firewall approval) are process blockers, not opposition. Mitigation: CTO escalation for procurement fast-track; pre-approved infrastructure templates for future requests.

**CMO** is both a gate and a champion. If clinical validation surfaces issues the CMO is not comfortable with (bias results, consent workflow gaps), they will block launch. Mitigation: involve CMO early in model card review, not just at the sign-off stage.

---

## Communication Cadence

| Audience | Format | Frequency | Owner |
|----------|--------|-----------|-------|
| CTO + CMO | Written status update (this format) | Weekly | PM |
| Steering committee | Go/no-go readiness review | Every 2 weeks | PM |
| Clinical team | Validation workshop | Weekly (Wk 4–6) | Physician Champion |
| IT / InfoSec | Tactical sync | As needed | Technical Lead |
| Scheduling coordinators | Change readiness check-in | Weekly (Wk 5–7) | Change Manager |
