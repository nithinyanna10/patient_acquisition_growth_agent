from dataclasses import dataclass


@dataclass
class RAIDItem:
    id: str
    category: str   # Risk | Assumption | Issue | Dependency
    title: str
    description: str
    severity: str   # Critical | High | Medium | Low
    urgency: str    # Immediate | This Week | This Sprint | Monitor
    owner: str
    mitigation: str
    status: str     # Open | Mitigated | Closed
