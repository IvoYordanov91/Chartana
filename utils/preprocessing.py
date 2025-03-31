import pandas as pd
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
