"""
Engine D: Unresolved Topics & Unassigned Tasks Detector.
Groups messages into topics and identifies open questions, unconfirmed proposals, or unassigned tasks.
"""

import re
import pandas as pd
from typing import List, Dict, Any
from src.schema import Finding


UNASSIGNED_TASK_PATTERNS = [
    r"\b(we need someone to|someone needs to|someone should|who can take|who will|needs to be done|who is handling)\b",
    r"\b(prepare the demo|prepare slides|fix the bug|deploy|review code|write docs|organize)\b"
]

ASSIGNMENT_ACCEPTANCE_PATTERNS = [
    r"\b(i can|i will|i'll|take care of|on it|assign to me|i'm on it|i have started|i'll prepare|i'll fix|i'll do)\b"
]


def is_unassigned_task(text: str) -> bool:
    """Check if text proposes a task without assigning an owner."""
    text_lower = text.strip().lower()
    for pat in UNASSIGNED_TASK_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True
    return False


def is_task_accepted(text: str) -> bool:
    """Check if text indicates acceptance/ownership of a task."""
    text_lower = text.strip().lower()
    for pat in ASSIGNMENT_ACCEPTANCE_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True
    return False


def detect_unresolved(df: pd.DataFrame, window_size: int = 6) -> List[Finding]:
    """
    Detect unresolved topics and unassigned tasks in conversation DataFrame.
    """
    findings = []
    if df.empty or len(df) == 0:
        return findings

    n = len(df)
    messages = df['message'].astype(str).tolist()
    speakers = df['speaker'].astype(str).tolist()
    timestamps = df['timestamp'].tolist()

    for i in range(n):
        msg = messages[i]
        speaker = speakers[i]
        timestamp = timestamps[i]

        if not is_unassigned_task(msg):
            continue

        window_end = min(n, i + 1 + window_size)
        subsequent_indices = list(range(i + 1, window_end))

        accepted = False
        owner_speaker = None

        for j in subsequent_indices:
            r_msg = messages[j]
            r_speaker = speakers[j]

            if is_task_accepted(r_msg):
                accepted = True
                owner_speaker = r_speaker
                break

        if not accepted:
            checked_count = len(subsequent_indices)
            findings.append(Finding(
                id=f"UNRESOLVED-{i}",
                type="Unresolved Topic",
                speaker=speaker,
                message=msg,
                timestamp=timestamp,
                message_index=i,
                evidence=[
                    f"Task or action proposed by {speaker} remains unassigned.",
                    f"No participant accepted ownership in the following {checked_count} message(s)."
                ],
                confidence=0.88,
                status="Needs review",
                topic="Unassigned Action Item",
                related_message_indices=subsequent_indices
            ))

    return findings
