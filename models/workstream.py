from dataclasses import dataclass
from typing import Optional

_STATUS_MULTIPLIERS = {
    "Complete": 1.0,
    "On Track": 1.0,
    "At Risk": 0.7,
    "Blocked": 0.4,
}


@dataclass
class Workstream:
    id: str
    name: str
    owner: str
    status: str  # Complete | On Track | At Risk | Blocked
    progress: int  # 0-100
    priority: str  # Critical | High | Medium | Low
    blocker: Optional[str] = None

    def effective_progress(self) -> float:
        """Progress dampened by status — At Risk loses 30%, Blocked loses 60%."""
        return self.progress * _STATUS_MULTIPLIERS.get(self.status, 0.5)
