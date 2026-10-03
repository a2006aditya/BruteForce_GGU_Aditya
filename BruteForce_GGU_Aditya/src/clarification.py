"""
Engine C: Repeated Clarification Requests Detector.
Identifies semantically similar questions or clarification requests repeated across the conversation.
"""

import pandas as pd
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.schema import Finding
from src.unanswered import is_question


# Topic keyword triggers for common clarification subjects
CLARIFICATION_KEYWORDS = {
    'format': {'format', 'pdf', 'docx', 'csv', 'txt', 'file', 'type', 'extension', 'submit', 'submission'},
    'deadline': {'deadline', 'time', 'date', 'due', 'when', 'tomorrow', 'today', 'pm', 'am', 'schedule'},
    'venue': {'room', 'venue', 'link', 'meet', 'zoom', 'teams', 'location', 'where'}
}


def get_topic_category(text: str) -> str:
    """Identify matching domain topic category for a message if any."""
    words = set(text.lower().split())
    for category, cat_words in CLARIFICATION_KEYWORDS.items():
        if len(words.intersection(cat_words)) >= 2:
            return category
    return "general"


def detect_clarification(df: pd.DataFrame, similarity_threshold: float = 0.35) -> List[Finding]:
    """
    Detect repeated clarification requests using TF-IDF cosine similarity and topic overlap.
    """
    findings = []
    if df.empty or len(df) < 2:
        return findings

    n = len(df)
    messages = df['message'].astype(str).tolist()
    speakers = df['speaker'].astype(str).tolist()
    timestamps = df['timestamp'].tolist()

    # Identify candidate question or clarification indices
    question_indices = [i for i in range(n) if is_question(messages[i])]

    if len(question_indices) < 2:
        return findings

    q_texts = [messages[i] for i in question_indices]

    # Compute TF-IDF matrix for all questions
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(q_texts)
        sim_matrix = cosine_similarity(tfidf_matrix)
    except Exception:
        sim_matrix = None

    flagged_pairs = set()

    for idx1 in range(len(question_indices)):
        i = question_indices[idx1]
        msg1 = messages[i]
        cat1 = get_topic_category(msg1)

        for idx2 in range(idx1 + 1, len(question_indices)):
            j = question_indices[idx2]
            msg2 = messages[j]
            cat2 = get_topic_category(msg2)

            if (i, j) in flagged_pairs:
                continue

            sim_val = sim_matrix[idx1, idx2] if sim_matrix is not None else 0.0
            
            # Check topic overlap match
            same_topic_match = (cat1 != "general" and cat1 == cat2)

            if sim_val >= similarity_threshold or same_topic_match:
                flagged_pairs.add((i, j))
                
                evidence_text = f"Semantically similar question asked at message #{j} by {speakers[j]} (Timestamp: {timestamps[j]}): \"{msg2}\""
                conf = min(0.95, round(0.60 + float(sim_val) * 0.35, 2)) if sim_matrix is not None else 0.75

                findings.append(Finding(
                    id=f"CLARIFY-{j}",
                    type="Repeated Clarification",
                    speaker=speakers[j],
                    message=msg2,
                    timestamp=timestamps[j],
                    message_index=j,
                    evidence=[
                        f"Original question by {speakers[i]} (Message #{i}): \"{msg1}\"",
                        evidence_text
                    ],
                    confidence=conf,
                    status="Needs review",
                    topic=cat1 if cat1 != "general" else "Repeated Request",
                    related_message_indices=[i, j]
                ))

    return findings
