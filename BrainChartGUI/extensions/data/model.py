import pandas as pd
from pubsub import pub
import os

def load_data(filename: str) -> None:
    """Loads data from disk.

    Args:
        filename: Name of the file to load. Must contain data in CSV format.
    """
    try:
        print(filename)
        _, ext = os.path.splitext(filename)
        print(ext)
        if ext in ['.csv']:
            data = pd.read_csv(filename)
        elif (ext in ['.pkl']) | filename.endswith('.pkl.gz'):
            print('Loading ' + filename)
            data = pd.read_pickle(filename)

    except Exception as err:
        data = None
        filename = f"No data could be loaded. {err.args}"

    pub.sendMessage("data.load", filename=filename, data=data)


def delete_data() -> None:
    """Deletes data from memory."""
    pub.sendMessage("data.load", filename="No data loaded", data=None)
