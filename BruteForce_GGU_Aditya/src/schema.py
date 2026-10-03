"""
Data structures and schema definitions for ConvoSense AI findings and evidence.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any


@dataclass
class Finding:
    id: str
    type: str  # "Unanswered Question", "Ignored Response", "Repeated Clarification", "Unresolved Topic"
    speaker: str
    message: str
    timestamp: Optional[str]
    message_index: int
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.80
    status: str = "Needs review"  # "Needs review", "Resolved", "False positive"
    topic: Optional[str] = None
    related_message_indices: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
