import pandas as pd
import numpy as np
from io import StringIO

def parse_csv(file_stream, separator=','):
    """
    Parses a CSV file from an uploaded file stream using the given separator.
    Skips bad lines to avoid crashing on malformed CSVs.
    """
    try:
        stream = StringIO(file_stream.read().decode("utf-8"))
        df = pd.read_csv(stream, sep=separator, on_bad_lines='skip')
        return df
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")

def count_nulls(data_frame):
    return data_frame.isnull().sum()

def percent_nulls(data_frame, missing_values_count):
    total_cells = np.product(data_frame.shape)
    total_missing = missing_values_count.sum()
    return (total_missing/total_cells)*100

def count_duplicates(data_frame):
    df_copy = data_frame.copy()
    for col in df_copy.select_dtypes(include='object').columns:
        df_copy[col] = df_copy[col].str.lower()

    duplicate_counts = {}
    for col in df_copy.columns:
        duplicate_counts[col] = df_copy.duplicated(subset=[col]).sum()

    return pd.Series(duplicate_counts, name='Duplicate Count')