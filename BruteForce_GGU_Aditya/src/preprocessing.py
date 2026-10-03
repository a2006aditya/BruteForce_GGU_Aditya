"""
Preprocessing utilities for conversation datasets.
"""

import re
import pandas as pd
from typing import List


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess canonical conversation DataFrame.
    """
    df_clean = df.copy()
    if 'message' in df_clean.columns:
        df_clean['cleaned_message'] = df_clean['message'].astype(str).apply(clean_text)
    return df_clean


def clean_text(text: str) -> str:
    """
    Standardize text for NLP vectorization:
    - remove media placeholders
    - normalize whitespace
    - lowercase
    """
    if not text:
        return ""
    # Remove media placeholders
    text = re.sub(r'<media\s+omitted>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'image\s+omitted', '', text, flags=re.IGNORECASE)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
