from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import wx
import wx.grid
from pubsub import pub

EVEN_ROW_COLOUR = "#CCE6FF"
GRID_LINE_COLOUR = "#ccc"


class DataLoaderTab(wx.Window):
    def __init__(self, parent, on_open: Callable, on_delete: Callable):
        super(DataLoaderTab, self).__init__(parent)

        self.clear_btn: wx.Button
        self.filename_lbl: wx.StaticText
        self.grid: wx.grid.Grid
        self.on_open = on_open
        self.on_delete = on_delete

        pub.subscribe(self.display_data, "data.load")

        self._init_gui()
        self.Layout()

    def _init_gui(self):
        """Initialises the GUI elements in the frame."""
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        open_btn = wx.Button(self, label="Load data file")
        self.clear_btn = wx.Button(self, label="Clear data")
        self.filename_lbl = wx.StaticText(self, label="No data loaded")
        hbox.Add(open_btn, flag=wx.EXPAND | wx.ALL, border=10)
        hbox.Add(self.clear_btn, flag=wx.EXPAND | wx.ALL, border=10)
        hbox.Add(self.filename_lbl, 2, flag=wx.EXPAND | wx.ALL, border=10)

        self.grid = wx.grid.Grid(self, -1)
        self.update_table()

        self.Bind(wx.EVT_BUTTON, lambda _: self.on_open(), source=open_btn)
        self.Bind(wx.EVT_BUTTON, lambda _: self.on_delete(), source=self.clear_btn)
        self.clear_btn.Disable()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(hbox)
        main_sizer.Add(self.grid, 0, flag=wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(main_sizer)


    def display_data(self, filename: str, data: Optional[pd.DataFrame] = None):
        """Displays the data on a table and sets the filename

        Args:
            filename: Name of the file loaded
            data: A dataframe with the data
        """
        if data is None:
            self.filename_lbl.SetLabelText(filename)
            self.filename_lbl.SetToolTip('No data loaded. Click `Looad data file` to open data from a file.')
            self.clear_btn.Disable()
            self.update_table(data)
        else:
            self.clear_btn.Enable()
            self.filename_lbl.SetLabelText(Path(filename).name)
            self.filename_lbl.SetToolTip(filename)
            self.update_table(data.head(10))


    def update_table(self, data: Optional[pd.DataFrame] = None):
        """updates the data on the table.

        Args:
            data: The data to update the table with. Can be None.
        """
        table = DataTable(data)
        self.grid.SetTable(table, takeOwnership=True)
        self.grid.AutoSizeColumns()
        self.Layout()


class FileDialogCustom(wx.FileDialog):
    def __init__(self):
        super(FileDialogCustom, self).__init__(
            None,
            "Open data file",
            wildcard="CSV files (*.CSV)|*.csv|Pickle files (*.pkl;*.pkl.gz)|*.pkl;*.pkl.gz",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )

    def open(self):
        return self.ShowModal() == wx.ID_OK


class DataTable(wx.grid.GridTableBase):
    """
    Declare DataTable to hold the wx.grid data to be displayed

    Example taken from: https://stackoverflow.com/a/65265739/3778792
    """

    def __init__(self, data=None):
        wx.grid.GridTableBase.__init__(self)
        self.headerRows = 1
        if data is None:
            data = pd.DataFrame()
        self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data.columns) + 1

    def GetValue(self, row, col):
        if col == 0:
            return self.data.index[row]
        return self.data.iloc[row, col - 1]

    def SetValue(self, row, col, value):
        self.data.iloc[row, col - 1] = value

    def GetColLabelValue(self, col):
        if col == 0:
            if self.data.index.name is None:
                return "Index"
            else:
                return self.data.index.name
        return str(self.data.columns[col - 1])

    def GetTypeName(self, row, col):
        return wx.grid.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = wx.grid.GridCellAttr()
        if row % 2 == 1:
            attr.SetBackgroundColour(EVEN_ROW_COLOUR)
        return attr
