"""
Reporting and Export Module for ConvoSense AI findings.
Exports findings to JSON or CSV formats.
"""

import json
import pandas as pd
from typing import List, Dict, Any
from src.schema import Finding


def export_findings_to_json(findings: List[Finding]) -> str:
    """Export findings list to formatted JSON string."""
    data = [f.to_dict() if isinstance(f, Finding) else f for f in findings]
    return json.dumps(data, indent=2)


def export_findings_to_csv(findings: List[Finding]) -> str:
    """Export findings list to CSV string."""
    if not findings:
        return "id,type,speaker,message,timestamp,message_index,confidence,status,evidence"
    
    records = []
    for f in findings:
        d = f.to_dict() if isinstance(f, Finding) else f
        d['evidence'] = " | ".join(d.get('evidence', []))
        d['related_message_indices'] = ",".join(map(str, d.get('related_message_indices', [])))
        records.append(d)
        
    df = pd.DataFrame(records)
    return df.to_csv(index=False)
