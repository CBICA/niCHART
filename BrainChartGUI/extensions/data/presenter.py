from typing import List

from pyguitemp.plugins import PluginBase, Tab

from .model import delete_data as delete_data_
from .model import load_data as load_data_
from .view import DataLoaderTab, FileDialogCustom


class DataPlugin(PluginBase):
    def tabs(self, parent=None) -> List[Tab]:
        data_loader_tab = DataLoaderTab(parent, load_data, delete_data)
        return [Tab(page=data_loader_tab, text="Data", order=0)]


def load_data() -> None:
    """Loads a text file from disk."""
    with FileDialogCustom() as dlg:
        if not dlg.open():
            # the user changed their mind
            return

        filename = dlg.GetPath()

    load_data_(filename)


def delete_data():
    """Deletes loaded data."""
    delete_data_()
