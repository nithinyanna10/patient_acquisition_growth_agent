from dataclasses import dataclass, field
from typing import List


@dataclass
class Milestone:
    id: str
    name: str
    due_week: int
    status: str  # Complete | On Track | At Risk | Slipped
    owner: str
    workstream_id: str
    depends_on: List[str] = field(default_factory=list)

    def has_prerequisites(self) -> bool:
        return bool(self.depends_on)

    def is_at_risk(self) -> bool:
        return self.status in ("At Risk", "Slipped")
