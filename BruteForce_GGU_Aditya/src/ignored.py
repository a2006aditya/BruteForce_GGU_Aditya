"""
Engine B: Ignored Responses / Unacknowledged Proposals Detector.
Flags proposals, commitments, or action requests that receive no acknowledgment or response.
"""

import re
import pandas as pd
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.schema import Finding


PROPOSAL_PATTERNS = [
    r"\b(i'll|i will|let's|lets|we should|i can|please|could you|would you|can someone)\b",
    r"\b(proposal|suggestion|idea|draft|submit|prepare|book|schedule)\b"
]

ACK_PATTERNS = [
    r"\b(confirmed|thanks|thank you|got it|agreed|will do|sounds good|great|perfect|ok|okay|done|noted|awesome|cool|sure)\b",
    r"\b(approved|accepted|copied)\b"
]


def is_proposal_or_request(text: str) -> bool:
    """Check if message is a proposal, action item, or direct request."""
    text_lower = text.strip().lower()
    for pat in PROPOSAL_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True
    return False


def is_acknowledgment(text: str) -> bool:
    """Check if message contains acknowledgment keywords."""
    text_lower = text.strip().lower()
    for pat in ACK_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True
    return False


def detect_ignored(df: pd.DataFrame, window_size: int = 5) -> List[Finding]:
    """
    Detect unacknowledged proposals or ignored action requests in conversation DataFrame.
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

        if not is_proposal_or_request(msg):
            continue

        window_end = min(n, i + 1 + window_size)
        subsequent_indices = list(range(i + 1, window_end))

        if not subsequent_indices:
            findings.append(Finding(
                id=f"IGNORED-{i}",
                type="Ignored Response",
                speaker=speaker,
                message=msg,
                timestamp=timestamp,
                message_index=i,
                evidence=["Proposal made at end of conversation with no subsequent replies."],
                confidence=0.85,
                status="Needs review",
                related_message_indices=[]
            ))
            continue

        is_ack = False

        for j in subsequent_indices:
            r_msg = messages[j]
            r_speaker = speakers[j]

            # Acknowledgment from a different speaker
            if r_speaker != speaker:
                if is_acknowledgment(r_msg):
                    is_ack = True
                    break
                
                # Check semantic relevance via TF-IDF cosine similarity
                try:
                    vectorizer = TfidfVectorizer(stop_words='english')
                    tfidf = vectorizer.fit_transform([msg, r_msg])
                    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
                    if sim >= 0.15:
                        is_ack = True
                        break
                except Exception:
                    pass

        if not is_ack:
            checked_count = len(subsequent_indices)
            findings.append(Finding(
                id=f"IGNORED-{i}",
                type="Ignored Response",
                speaker=speaker,
                message=msg,
                timestamp=timestamp,
                message_index=i,
                evidence=[f"Proposal or request received no explicit acknowledgment in the following {checked_count} message(s)."],
                confidence=0.75,
                status="Needs review",
                related_message_indices=subsequent_indices
            ))

    return findings
