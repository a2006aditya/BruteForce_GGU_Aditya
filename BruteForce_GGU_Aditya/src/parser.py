"""
Multi-format conversation parser supporting CSV, plain text, and WhatsApp export formats.
"""

import re
import pandas as pd
from typing import Union, List, Dict, Tuple


WHATSAPP_PATTERNS = [
    # [DD/MM/YY, HH:MM:SS] Speaker: Message or [DD/MM/YYYY, HH:MM:SS AM/PM] - Speaker: Message
    re.compile(r'^\[?(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM)\b)?)\]?\s*-?\s*([^:]+):\s*(.*)$', re.IGNORECASE),
    # DD/MM/YYYY, HH:MM - Speaker: Message
    re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?:\s*(?:AM|PM)\b)?)\s*-?\s*([^:]+):\s*(.*)$', re.IGNORECASE),
    # HH:MM - Speaker: Message
    re.compile(r'^(\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM)\b)?)\s*-?\s*([^:]+):\s*(.*)$', re.IGNORECASE),
    # HH:MM Speaker: Message
    re.compile(r'^(\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM)\b)?)\s+([A-Z0-9_\s]{2,20}):\s*(.*)$', re.IGNORECASE),
    # Speaker: Message (no timestamp)
    re.compile(r'^([A-Z0-9_\s]{2,20}):\s*(.*)$', re.IGNORECASE),
]


def parse_raw_text(text: str) -> pd.DataFrame:
    """
    Parse pasted plain text or TXT log line-by-line, handling multiline messages and timestamps.
    """
    lines = text.strip().splitlines()
    records = []
    
    current_timestamp = None
    current_speaker = None
    current_message_parts = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        matched = False
        for pattern in WHATSAPP_PATTERNS:
            m = pattern.match(line_str)
            if m:
                # Store previous accumulated message if present
                if current_speaker and current_message_parts:
                    records.append({
                        "timestamp": current_timestamp,
                        "speaker": current_speaker.strip(),
                        "message": "\n".join(current_message_parts).strip()
                    })
                    current_message_parts = []
                
                groups = m.groups()
                if len(groups) == 3:
                    current_timestamp, current_speaker, msg = groups
                elif len(groups) == 2:
                    current_timestamp = None
                    current_speaker, msg = groups
                else:
                    current_timestamp = None
                    current_speaker = "Unknown"
                    msg = line_str
                    
                current_message_parts.append(msg)
                matched = True
                break
                
        if not matched:
            if current_speaker is not None:
                current_message_parts.append(line_str)
            else:
                # If first line has no speaker prefix, treat whole line as message from Unknown
                current_speaker = "User"
                current_timestamp = None
                current_message_parts.append(line_str)
                
    if current_speaker and current_message_parts:
        records.append({
            "timestamp": current_timestamp,
            "speaker": current_speaker.strip(),
            "message": "\n".join(current_message_parts).strip()
        })
        
    return _build_canonical_dataframe(records)


def parse_csv(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw CSV DataFrame into canonical conversation format.
    """
    col_map = {}
    for col in df_raw.columns:
        col_lower = str(col).lower().strip()
        if col_lower in ['timestamp', 'time', 'date', 'datetime']:
            col_map['timestamp'] = col
        elif col_lower in ['speaker', 'user', 'sender', 'author', 'name', 'from']:
            col_map['speaker'] = col
        elif col_lower in ['message', 'text', 'content', 'msg', 'body']:
            col_map['message'] = col
            
    records = []
    for idx, row in df_raw.iterrows():
        timestamp = str(row[col_map['timestamp']]).strip() if 'timestamp' in col_map and pd.notna(row[col_map['timestamp']]) else None
        speaker = str(row[col_map['speaker']]).strip() if 'speaker' in col_map and pd.notna(row[col_map['speaker']]) else "Unknown"
        message = str(row[col_map['message']]).strip() if 'message' in col_map and pd.notna(row[col_map['message']]) else ""
        
        if message:
            records.append({
                "timestamp": timestamp,
                "speaker": speaker,
                "message": message
            })
            
    return _build_canonical_dataframe(records)


def parse_conversation_input(data_input: Union[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Unified entry point for parsing pasted text or CSV DataFrame.
    """
    if isinstance(data_input, pd.DataFrame):
        return parse_csv(data_input)
    elif isinstance(data_input, str):
        return parse_raw_text(data_input)
    else:
        raise ValueError("Unsupported input type. Expected pandas DataFrame or string.")


def _build_canonical_dataframe(records: List[Dict[str, str]]) -> pd.DataFrame:
    """
    Construct canonical DataFrame with message_id, timestamp, speaker, message, and has_timestamp flag.
    """
    if not records:
        return pd.DataFrame(columns=["message_id", "timestamp", "speaker", "message", "has_timestamp"])
        
    df = pd.DataFrame(records)
    df["message_id"] = range(len(df))
    df["has_timestamp"] = df["timestamp"].apply(lambda t: t is not None and str(t).strip() != "" and str(t).strip().lower() != "nan")
    df["timestamp"] = df["timestamp"].fillna("Unavailable")
    
    # Filter out empty messages
    df = df[df["message"].str.strip() != ""].reset_index(drop=True)
    df["message_id"] = range(len(df))
    return df[["message_id", "timestamp", "speaker", "message", "has_timestamp"]]
