from dataclasses import dataclass
from typing import Optional


@dataclass
class ChecklistItem:
    id: str
    category: str   # Technical | Clinical Safety | Compliance | Legal | Operations
    item: str
    status: str     # Pass | Fail | Pending
    owner: str
    evidence: Optional[str] = None
