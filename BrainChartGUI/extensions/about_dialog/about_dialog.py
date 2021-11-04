from pathlib import Path
from typing import List

import wx
import wx.adv

from pyguitemp.plugins import MenuTool, PluginBase

from ... import VERSION


class AboutDialogPlugin(PluginBase):
    def menu_entries(self) -> List[MenuTool]:
        return [
            MenuTool(
                menu="About",
                id=wx.ID_ABOUT,
                text="About",
                description="Some info about this app",
                callback=self.OnAboutBox,
            ),
        ]

    def OnAboutBox(self, e):
        with (Path(__file__).parent / "description").open("r") as f:
            description = f.read()

        with (Path(__file__).parent / "LICENSE").open("r") as f:
            licence = f.read()

        info = wx.adv.AboutDialogInfo()

        info.SetIcon(
            wx.Icon(str(Path(__file__).parent / "logo.png"), wx.BITMAP_TYPE_PNG)
        )
        info.SetName("BrainChart")
        info.SetVersion(VERSION)
        info.SetDescription(description)
        info.SetCopyright("(C) University of Pennsylvania")
        info.SetWebSite("https://github.com/CBICA/iSTAGING-Tools")
        info.SetLicence(licence)
        info.AddDeveloper("Ahmed Abdulkadir")
        info.AddDeveloper("Ashish Singh")
        info.AddDocWriter("Ahmed Abdulkadir")
        info.AddDocWriter("Ashish Singh")


        wx.adv.AboutBox(info)
