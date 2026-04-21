# Technical Readiness Note
## Patient Acquisition & Growth Agent — Meridian Health System
**Week 4 of 8 | Prepared by: Sarah Okonkwo | April 20, 2026**

---

## Summary Verdict

| Gate | Status | Owner |
|------|--------|-------|
| Model accuracy | ✅ Pass | Dr. Priya Nair |
| EHR integration | ⚠️ At Risk | Marcus Chen |
| Load testing | ❌ Fail | Marcus Chen |
| HIPAA / compliance | ✅ Pass | James Okafor |
| Monitoring & alerting | ✅ Pass | Ravi Shankar |

**Current launch verdict: NO-GO.** Load testing gate is failing. EHR production credentials not yet received. Both must resolve before a Go decision can be issued.

---

## 1. Model Readiness

The patient acquisition model has cleared the accuracy threshold. Holdout validation returned AUC 0.87 against a required minimum of 0.85. Precision and F1 are within acceptable range.

**One open issue requires explicit sign-off before pilot launch.** Validation shows 12% lower recall for Hispanic and Black patient cohorts relative to the overall population. This is not a model failure — it reflects gaps in the training data. Remediation is in scope: stratified oversampling is underway and a retrain is planned once the historical data backfill completes. The model will not enter a live patient environment until a bias-corrected version has been reviewed by the physician panel and signed off by the CMO.

No shortcuts here. Deploying a biased acquisition model in a hospital is a regulatory and reputational risk, not just a technical one.

---

## 2. EHR Integration Readiness

Epic FHIR API sandbox integration is complete and functional. The blocker is production credentials, which are held in the hospital IT procurement queue and are now two weeks behind the original plan.

The more significant risk is not connectivity — it is logic alignment. The model may recommend appointment slots that the EHR considers unavailable due to scheduling rules (block scheduling, provider-specific constraints, resource conflicts) that were not represented in the training data. This category of failure is invisible in unit tests and only surfaces during end-to-end UAT with real EHR state.

**This is why EHR integration UAT has its own go/no-go gate.** API connectivity is necessary but not sufficient. Business rule alignment requires clinical operations in the room during testing.

Mitigation in place: request queueing and exponential backoff are built to handle Epic's 60 req/min rate limit. A mock server exists for offline development. Production UAT is blocked until credentials are received — currently targeting Week 5.

---

## 3. Infrastructure & Load Testing

Load testing at 420+ concurrent users produced a 23% timeout rate against a target of under 2 seconds at the 95th percentile for 500 users. This gate is failing.

Root cause identified: database connection pool is undersized for peak load. Fix in current sprint: pool size increase and query optimisation. A CDN caching layer is under evaluation for static inference results.

A revised load test is scheduled for Week 5. If the 2-second P95 threshold cannot be cleared, a temporary SLA relaxation to 3 seconds during the pilot phase is being evaluated with clinical operations — this requires explicit stakeholder approval before it can be accepted as a pass.

System monitoring is live. Grafana dashboards are deployed. PagerDuty alerting is configured and tested.

---

## 4. Compliance & Privacy Readiness

HIPAA Security Risk Assessment is complete. Two medium findings from the initial assessment have been remediated. No high or critical findings remain open.

PHI data flows are fully documented and approved by the DPO. The NLP-based PHI scanner is deployed on all data pipelines — this closed the critical risk of unstructured PHI in free-text EHR fields.

Business Associate Agreements are executed with all three PHI-handling vendors: Epic, Microsoft Azure, and Twilio.

One item pending: AI liability and indemnification agreement is in legal review. Expected execution by Week 5. Launch cannot proceed without it.

---

## 5. Go / No-Go Gate Status

| Category | Pass | Fail | Pending |
|----------|------|------|---------|
| Technical | 2 | 1 | 1 |
| Clinical Safety | 2 | 0 | 1 |
| Compliance | 3 | 0 | 0 |
| Legal | 1 | 0 | 1 |
| Operations | 2 | 0 | 1 |
| **Total** | **10** | **1** | **4** |

The single failing item (load testing) and the pending legal sign-off are the two conditions most likely to determine whether a Week 8 go-live is achievable. Both are being actively worked. A re-assessment is scheduled at the Week 5 steering committee.
