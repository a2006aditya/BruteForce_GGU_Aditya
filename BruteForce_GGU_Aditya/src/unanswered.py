"""
Engine A: Unanswered Questions Detector.
Flags question messages that receive no plausible answer within a configurable lookahead window.
"""

import re
import pandas as pd
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.schema import Finding


QUESTION_PATTERNS = [
    r'\?$',  # ends with question mark
    r'^\s*(who|what|when|where|why|how|which|can|could|will|would|should|is|are|am|do|does|did|has|have|had|is there|are there)\b',
]

# Time/date/direct answer regex patterns to catch short answers like "At 4 PM", "Tomorrow", "PDF", etc.
DIRECT_ANSWER_PATTERNS = [
    r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b',  # time e.g. 4 PM, 10:30
    r'\b(today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(yes|no|yeah|nope|sure|okay|ok|done|pdf|docx|txt|csv)\b',
    r'\b(at|on|by|in)\s+\d+',
]


def is_question(text: str) -> bool:
    """Check if message is a question based on regex and punctuation."""
    text_clean = text.strip().lower()
    if '?' in text_clean:
        return True
    for pat in QUESTION_PATTERNS:
        if re.search(pat, text_clean, re.IGNORECASE):
            return True
    return False


def is_direct_answer(text: str) -> bool:
    """Check if text matches common short direct answer patterns (times, dates, simple confirmations)."""
    text_lower = text.strip().lower()
    for pat in DIRECT_ANSWER_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return True
    return False


def detect_unanswered(df: pd.DataFrame, window_size: int = 5, similarity_threshold: float = 0.15) -> List[Finding]:
    """
    Detect unanswered questions in a conversation DataFrame.
    """
    findings = []
    if df.empty or len(df) == 0:
        return findings

    n = len(df)
    messages = df['message'].astype(str).tolist()
    speakers = df['speaker'].astype(str).tolist()
    timestamps = df['timestamp'].tolist()

    for i in range(n):
        q_msg = messages[i]
        q_speaker = speakers[i]
        q_timestamp = timestamps[i]

        if not is_question(q_msg):
            continue

        # Inspect subsequent window
        window_end = min(n, i + 1 + window_size)
        subsequent_indices = list(range(i + 1, window_end))
        
        if not subsequent_indices:
            # End of conversation question with no subsequent messages
            findings.append(Finding(
                id=f"UNANSWERED-{i}",
                type="Unanswered Question",
                speaker=q_speaker,
                message=q_msg,
                timestamp=q_timestamp,
                message_index=i,
                evidence=["Question asked at end of conversation with no subsequent replies."],
                confidence=0.90,
                status="Needs review",
                related_message_indices=[]
            ))
            continue

        has_answer = False
        evidence_logs = []

        # Check subsequent messages for plausible answers
        candidate_replies = []
        candidate_indices = []

        for j in subsequent_indices:
            r_msg = messages[j]
            r_speaker = speakers[j]

            # Direct answer pattern check (e.g., "At 4 PM" or "Tomorrow")
            if is_direct_answer(r_msg) and r_speaker != q_speaker:
                has_answer = True
                break

            # If reply from different speaker isn't another question, add to TF-IDF candidates
            if r_speaker != q_speaker:
                candidate_replies.append(r_msg)
                candidate_indices.append(j)

        if not has_answer and candidate_replies:
            # TF-IDF Cosine Similarity test between question and candidate replies
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([q_msg] + candidate_replies)
                sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

                for idx, sim in enumerate(sims):
                    if sim >= similarity_threshold or is_direct_answer(candidate_replies[idx]):
                        has_answer = True
                        break
            except Exception:
                # Fallback if TF-IDF vocabulary is empty (short stopword-only messages)
                # If there's any non-question reply by another speaker within window, consider answered
                for r_idx, r_msg in zip(candidate_indices, candidate_replies):
                    if not is_question(r_msg):
                        has_answer = True
                        break

        if not has_answer:
            checked_count = len(subsequent_indices)
            evidence_msg = f"No plausible answer detected in the following {checked_count} message(s)."
            findings.append(Finding(
                id=f"UNANSWERED-{i}",
                type="Unanswered Question",
                speaker=q_speaker,
                message=q_msg,
                timestamp=q_timestamp,
                message_index=i,
                evidence=[evidence_msg],
                confidence=0.82 if '?' in q_msg else 0.70,
                status="Needs review",
                related_message_indices=subsequent_indices
            ))

    return findings
