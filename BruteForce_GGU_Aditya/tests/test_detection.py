"""
Unit tests for ConvoSense AI parser and detection engines.
"""

import pytest
import pandas as pd
from src.parser import parse_raw_text, parse_csv
from src.unanswered import detect_unanswered
from src.ignored import detect_ignored
from src.clarification import detect_clarification
from src.unresolved import detect_unresolved
from src.semantic_analysis import analyze_conversation


def test_engine_a_answered_question_negative():
    """Test case: 'When is the meeting?' followed by 'At 4 PM' should NOT be flagged as unanswered."""
    raw_text = """
10:00 Rahul: When is the meeting?
10:02 Priya: At 4 PM
"""
    df = parse_raw_text(raw_text)
    findings = detect_unanswered(df, window_size=5)
    unanswered_ids = [f.id for f in findings]
    assert len(findings) == 0, f"Expected 0 unanswered questions, got: {findings}"


def test_engine_a_unanswered_question_positive():
    """Test case: 'What is the submission deadline?' with no answer should be flagged."""
    raw_text = """
10:00 Rahul: Who will prepare the slides?
10:02 Priya: I can prepare the introduction.
10:04 Amit: What is the submission deadline?
10:06 Rahul: Good luck team!
"""
    df = parse_raw_text(raw_text)
    findings = detect_unanswered(df, window_size=5)
    assert len(findings) == 1
    assert findings[0].speaker == "Amit"
    assert "submission deadline" in findings[0].message


def test_engine_b_acknowledged_response_negative():
    """Test case: 'I'll book the room for 3 PM.' followed by 'Confirmed, thanks!' should NOT be flagged."""
    raw_text = """
10:00 Rahul: I'll book the room for 3 PM.
10:01 Priya: Confirmed, thanks!
"""
    df = parse_raw_text(raw_text)
    findings = detect_ignored(df, window_size=5)
    assert len(findings) == 0, f"Expected 0 ignored proposals, got: {findings}"


def test_engine_b_ignored_response_positive():
    """Test case: Proposal with no reaction should be flagged as ignored response."""
    raw_text = """
10:00 Rahul: I will send the proposal by 2 PM.
10:05 Priya: Let's discuss marketing budget.
10:10 Amit: Anyone seen my glasses?
"""
    df = parse_raw_text(raw_text)
    findings = detect_ignored(df, window_size=5)
    assert len(findings) == 2
    assert any(f.speaker == "Rahul" for f in findings)
    assert any(f.speaker == "Priya" for f in findings)


def test_engine_c_repeated_clarification_positive():
    """Test case: 'Which file format is required?' and 'Should we submit PDF or DOCX?' should be flagged."""
    raw_text = """
10:00 Rahul: Which file format is required?
10:05 Priya: Let's start typing.
10:10 Amit: Should we submit PDF or DOCX format?
"""
    df = parse_raw_text(raw_text)
    findings = detect_clarification(df, similarity_threshold=0.30)
    assert len(findings) >= 1
    assert any("PDF or DOCX" in f.message for f in findings)
    # Verify evidence contains original question
    assert any("Which file format" in e for f in findings for e in f.evidence)


def test_engine_d_unassigned_task_positive():
    """Test case: 'We need someone to prepare the demo.' followed by unrelated messages should be flagged."""
    raw_text = """
10:00 Rahul: We need someone to prepare the demo.
10:02 Priya: Weather is nice today.
10:04 Amit: See you all later.
"""
    df = parse_raw_text(raw_text)
    findings = detect_unresolved(df, window_size=5)
    assert len(findings) == 1
    assert findings[0].speaker == "Rahul"
    assert "prepare the demo" in findings[0].message


def test_parser_whatsapp_and_multiline():
    """Test WhatsApp export parser with multiline message and media placeholder."""
    raw_text = """
[01/10/26, 10:00:15 AM] Rahul: Hello team
Here is the multiline message continuation.
[01/10/26, 10:01:20 AM] Priya: <Media omitted>
[01/10/26, 10:02:00 AM] Amit: Okay noted
"""
    df = parse_raw_text(raw_text)
    assert len(df) == 3
    assert df.iloc[0]["speaker"] == "Rahul"
    assert "multiline message continuation" in df.iloc[0]["message"]
    assert df.iloc[1]["speaker"] == "Priya"


def test_parser_missing_timestamps():
    """Test handling input without timestamps."""
    raw_text = """
Rahul: Who will lead the design?
Priya: I can handle UI UX design.
"""
    df = parse_raw_text(raw_text)
    assert len(df) == 2
    assert df.iloc[0]["has_timestamp"] == False
    assert df.iloc[0]["timestamp"] == "Unavailable"
