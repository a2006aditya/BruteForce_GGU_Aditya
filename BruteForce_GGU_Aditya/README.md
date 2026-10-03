# ConvoSense AI — Conversation Intelligence & Communication Gap Analysis

> **CEREBRO Hackathon Project**  
> An end-to-end, local, evidence-based application that analyzes multi-person conversations and detects communication gaps.

---

## 🌟 Key Features

1. **Multi-Format Ingestion Engine**
   - Direct text paste (`HH:MM Speaker: Message` or raw transcripts).
   - CSV / TXT file upload with flexible column auto-detection.
   - WhatsApp chat export parser supporting multiline messages, date variations, and `<Media omitted>` placeholders.
   - Automatic fallback for missing timestamps (`has_timestamp = False`).

2. **Four Specialized NLP Detection Engines**
   - **Engine A: Unanswered Questions** — Identifies question messages that receive no plausible answer within a configurable lookahead window using NLP heuristics & TF-IDF cosine similarity.
   - **Engine B: Ignored Responses** — Detects unacknowledged proposals, commitments, or action requests.
   - **Engine C: Repeated Clarification** — Identifies semantically similar queries or repeated requests across the conversation timeline.
   - **Engine D: Unresolved Topics** — Flags unassigned action items, open proposals, or unresolved conversation threads.

3. **Evidence-Based & Interactive Review Controls**
   - Full evidence trace attached to every finding (original message, speaker, timestamp, confidence score, related messages).
   - Interactive review status controls (`Needs review`, `Resolved`, `False positive`) persisted across dashboard interactions.

4. **Rich Streamlit Dashboard**
   - **Overview & KPIs**: Summary cards and Plotly distribution charts.
   - **Evidence Explorer**: Deep-dive into each flagged issue.
   - **Interactive Timeline**: Plotly chronological chart mapping conversation flow and gap flags.
   - **Unresolved Topics**: Summary list of outstanding action items.
   - **Data Export**: Download modified findings in **JSON** or **CSV** format.

---

## 📁 Project Architecture

```
convosense-ai/
├── app.py                     # Streamlit Interactive Dashboard Application
├── requirements.txt           # Dependency Manifest
├── README.md                  # Comprehensive Documentation
├── data/
│   └── sample_conversation.csv # Benchmark Conversation Dataset
├── src/
│   ├── parser.py              # Multi-format Ingestion & WhatsApp Parser
│   ├── preprocessing.py       # Text Cleaning & Normalization
│   ├── schema.py              # Structured Finding Data Classes
│   ├── unanswered.py          # Engine A: Unanswered Question Detector
│   ├── ignored.py             # Engine B: Ignored Response Detector
│   ├── clarification.py       # Engine C: Repeated Clarification Detector
│   ├── unresolved.py          # Engine D: Unresolved Topic Detector
│   ├── semantic_analysis.py   # Analysis Pipeline Orchestrator
│   └── reporting.py           # JSON & CSV Exporters
└── tests/
    └── test_detection.py      # Pytest Verification Suite (8 Test Cases)
```

---

## 🚀 Quickstart & Installation

### 1. Environment Setup
```bash
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install streamlit pandas scikit-learn plotly pytest
```

### 3. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Verification

Run the automated test suite covering all 4 detection engines and edge cases:
```bash
pytest tests/test_detection.py
```

### Verified Test Cases:
- **Engine A**: `"When is the meeting?"` followed by `"At 4 PM"` is **not** flagged as unanswered (passed).
- **Engine A**: Unanswered questions with no reply within lookahead window are correctly flagged (passed).
- **Engine B**: `"I'll book the room for 3 PM."` followed by `"Confirmed, thanks!"` is **not** flagged (passed).
- **Engine B**: Unacknowledged proposals are flagged with confidence score and evidence log (passed).
- **Engine C**: `"Which file format is required?"` and `"Should we submit PDF or DOCX?"` are linked as repeated requests with reciprocal evidence (passed).
- **Engine D**: `"We need someone to prepare the demo."` with no owner acceptance is flagged as an unassigned task (passed).
- **Parser**: WhatsApp multiline logs and missing timestamp fallbacks verified (passed).

---

## 💡 Methodology & Model Limitations

- **Baseline Matching**: Uses TF-IDF vectorization with n-gram extraction and Cosine Similarity to compute semantic relevance locally without paid API keys.
- **Explainability**: Confidence scores represent similarity / pattern heuristics rather than black-box probabilities.
- **Human-in-the-Loop**: Judges and reviewers can override model classifications, mark false positives, or mark issues as resolved directly from the UI.
