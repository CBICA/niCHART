"""
This extension loads some experimental data and displays it into a table.

Channels:
    data.load: Triggered when new data is loaded or cleared.
        - filename (str): Path of tha data loaded or an error message.
        - data (Optional[pd.DataFrame]): Data as a pandas dataframe or None if there is
            o data.
"""
from .presenter import DataLoaderTab  # noqa
