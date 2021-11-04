"""
Settings for configuring the application general behavior, plugging collection and other
aspects of the tool.
"""
from typing import List

from pyguitemp.plugins import collect_builtin_extensions

APP_LONG_NAME: str = "Python GUI Template"
"""Long, human meaningful app name."""

PLUGINS: List[str] = ["BrainChartGUI.extensions.load_data"]
"""Explicit list of plugins that will be loaded in the order provided."""

AUTO_PLUGINS: List[str] = collect_builtin_extensions()
"""Plugins collected from the given locations. See `plugins.collect_plugins`"""

NOTEBOOK_LAYOUT: bool = True
"""Indicate if a notebook layout should be used in contrast to a central widget only."""

TAB_STYLE: str = "top"
"""Location of the tabs. Valid values are `top`, `bottom`, `left` and `right`."""
