"""A simple script to demonstrate matplotlib."""

from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar,
)
from matplotlib.figure import Figure

import numpy as np

import wx


class CanvasFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, -1, "CanvasFrame", size=(550, 350))

        self.figure = Figure()
        self.axes = self.figure.add_subplot()
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)

        self.axes.plot(t, s)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()

        self.add_toolbar()  # comment this out for no toolbar

    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()


class App(wx.App):
    def OnInit(self):
        """Create the main window and insert the custom frame."""
        self.Init()
        frame = CanvasFrame()
        frame.Show(True)

        return True


if __name__ == "__main__":
    app = App()
    app.MainLoop()
