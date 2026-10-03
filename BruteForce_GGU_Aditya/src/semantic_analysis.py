"""
Semantic Analysis Orchestrator.
Combines all 4 detection engines (Unanswered, Ignored, Clarification, Unresolved) and returns unified conversation metrics.
"""

import pandas as pd
from typing import Dict, Any, List
from src.schema import Finding
from src.unanswered import detect_unanswered
from src.ignored import detect_ignored
from src.clarification import detect_clarification
from src.unresolved import detect_unresolved


def analyze_conversation(df: pd.DataFrame, window_size: int = 5, similarity_threshold: float = 0.35) -> Dict[str, Any]:
    """
    Execute all detection engines on normalized conversation DataFrame.
    """
    if df.empty:
        return {
            "total_messages": 0,
            "unique_speakers": 0,
            "gap_counts": {
                "Unanswered Question": 0,
                "Ignored Response": 0,
                "Repeated Clarification": 0,
                "Unresolved Topic": 0
            },
            "findings": [],
            "speaker_stats": {}
        }

    unanswered_findings = detect_unanswered(df, window_size=window_size)
    ignored_findings = detect_ignored(df, window_size=window_size)
    clarification_findings = detect_clarification(df, similarity_threshold=similarity_threshold)
    unresolved_findings = detect_unresolved(df, window_size=window_size)

    all_findings: List[Finding] = unanswered_findings + ignored_findings + clarification_findings + unresolved_findings

    gap_counts = {
        "Unanswered Question": len(unanswered_findings),
        "Ignored Response": len(ignored_findings),
        "Repeated Clarification": len(clarification_findings),
        "Unresolved Topic": len(unresolved_findings)
    }

    speaker_counts = df['speaker'].value_counts().to_dict()

    return {
        "total_messages": len(df),
        "unique_speakers": df['speaker'].nunique(),
        "gap_counts": gap_counts,
        "findings": all_findings,
        "speaker_stats": speaker_counts
    }
