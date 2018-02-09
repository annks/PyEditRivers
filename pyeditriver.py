#!/usr/bin/env python
######################################################
## Edits ROMS masks using a GUI
## Nov 2014
## rsoutelino@gmail.com
######################################################
import os, sys
import wx
import wx.lib.mixins.inspection as WIT
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as Navbar
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import	wx.lib.dialogs
from wx.lib.stattext import GenStaticText

import wx.lib.scrolledpanel

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path

#from mpl_toolkits.basemap import Basemap

# local imports
from tools.romsnc import RomsGrid, river
from tools.dialog import GetData, get_arg, SplitRiverDlg
from tools.river_tools import check_rivers, getRiver, updateRiver, mergeRivers
from tools.plot_tools import remove_river_from_plot, plot_grid, plot_bathy, plot_river
from globalvars import *
global currentDirectory
currentDirectory = os.getcwd()

class CanvasFrame(wx.Frame):
    def __init__(self, gridfile, riverfile):
        wx.Frame.__init__(self, None, -1,
                          'PyEditRiver', size=(1024, 800))

        self.maintoolbar = MainToolBar(self)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        self.log = wx.TextCtrl(wx.Panel(self), wx.ID_ANY, size=(400,300),style = wx.TE_MULTILINE|wx.TE_READONLY|wx.VSCROLL)
        self.add_toolbar()  # comment this out for no toolbar
        if gridfile:
            self.maintoolbar.showGrid(gridfile)
            if riverfile:
                self.maintoolbar.showRivers(riverfile)

    def add_toolbar(self):
        self.mpltoolbar = NavigationToolbar2Wx(self.canvas)
        self.mpltoolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.mpltoolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.mpltoolbar.update()

    def OnQuit(self, e):
        self.Close()
        self.Destroy()

    def OnCloseWindow(self, e):
        self.Destroy()

class MainToolBar(object):
    def __init__(self, parent):
        self.currentDirectory = os.getcwd()
        self.parent = parent
        self.toolbar = parent.CreateToolBar(style=1, id=1,
                                            name="Toolbar")
        self.tools_params ={
            'load_grid': (load_bitmap('world.png'), u"Load grid",
                        "Load ocean_grd.nc ROMS grid netcdf file"),
            'load_river': (load_bitmap('rivertest.png'), u"Load river",
                        "Load rivers.nc ROMS river netcdf file"),
            'load_bathymetry': (load_bitmap('bathy.png'), u"Load bathy",
                        "Load ocean_grd.nc ROMS bathy netcdf file"),
            'check_river': (load_bitmap('check.png'), u"Verify rivers",
                        "Verify river positions"),
            'edit_river': (load_bitmap('edit.png'), u"edit river",
                        "Edit existing river location"),
            'split_river': (load_bitmap('split.png'), u"split river",
                        "Divide river on multiple outlets"),
            'save_river': (load_bitmap('save.png'), u"Apply and save",
                        "Save new river netcdf file"),
            'quit': (load_bitmap('exit.png'), u"Quit",
                        "Quit PyEditRiver"),

        }

        self.createTool(self.toolbar, self.tools_params['load_grid'],
                        self.OnLoadGrid)
        self.createTool(self.toolbar, self.tools_params['load_river'],
                        self.OnLoadRiver)
        self.createTool(self.toolbar, self.tools_params['load_bathymetry'],
                        self.OnLoadBathymetry)
        self.createTool(self.toolbar, self.tools_params['check_river'],
                        self.OnCheckRiver)
        self.toolbar.AddSeparator()

        self.edit_river_tool = self.createTool(self.toolbar, self.tools_params['edit_river'],
                                         self.OnEditRiver, kind = wx.ITEM_CHECK)
        self.split_river_tool = self.createTool(self.toolbar,
                                              self.tools_params['split_river'],
                                              self.OnSplitRiver, kind = wx.ITEM_CHECK)

        self.toolbar.AddSeparator()

        self.createTool(self.toolbar, self.tools_params['save_river'],
            self.OnSaveRiver)
        self.createTool(self.toolbar, self.tools_params['quit'],
                        self.parent.OnQuit)

        self.toolbar.Realize()

    def createTool(self, parent, params, evt,  kind = wx.ITEM_NORMAL):
        tool = parent.AddTool(wx.NewId(), params[1], params[0], shortHelp="", kind=kind)
        self.parent.Bind(wx.EVT_TOOL, evt, id=tool.GetId())
        return tool


    def OnLoadGrid(self, evt):
        openFileDialog = wx.FileDialog(self.parent, "Open grid netcdf file [*.nc]",
                                      style= wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        gridfile = openFileDialog.GetPath()
        self.showGrid(gridfile)


    def showGrid(self,filename,CMAP=DEFAULT_CMAP):
        self.grd = RomsGrid(filename)
        plot_grid(self, self.grd, vmin = DEFAULT_VMIN, vmax= DEFAULT_VMAX, cmap = CMAP)

    def OnLoadRiver(self, evt):
        openFileDialog = wx.FileDialog(self.parent, "Open river netcdf file [*.nc]",
                                       style =wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        riverfile = openFileDialog.GetPath()
        self.showRivers(riverfile)

    def showRivers(self,filename):
        riv  = river(filename, rivergrid, gridfile)
        plot_river(self,riv)
        self.river_cid = None
        self.riv = riv
        openFileDialog =  wx.FileDialog(self.parent, "Create backup file",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind

        # save the current contents in the file
        self.riv.backupfile = openFileDialog.GetPath()
        try:
            self.riv.backup()
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % self.riv.backupfile)


    def OnLoadBathymetry(self, evt):
        plot_bathy(self)

    def OnCheckRiver(self, evt):
        # Check whether rivers are placed correctly in the land mask
        status = check_rivers(self.riv, self.grd.maskr, self.grd.h)
        self.new_window = wx.Frame(self.parent, title='river status', pos=(800,0))
        self.scroll = wx.ScrolledWindow(self.new_window, -1,size=(500,500))
        self.scroll.SetScrollbars(1, 1, 1600, 1400)
        self.new_window.Layout()
        self.new_window.Fit()
        self.new_window.Show()
        wx.TextCtrl(self.new_window, -1, status, pos=(0,0), size=(500,500),style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_CENTER)
        self.new_window.Bind(wx.EVT_CLOSE, lambda evt: self.new_window.Destroy())

        def OnCloseWindow(self, e):
            self.Destroy()
    def OnEditRiver(self, evt):
        mplpanel = self.parent

        if self.river_cid is None:
            self.river_cid = mplpanel.canvas.mpl_connect('button_press_event', self.editRiver)
        else:
            mplpanel.canvas.mpl_disconnect(self.river_cid)
            self.river_cid = None

    def editRiver(self, evt):
        if evt.inaxes != self.parent.axes: return

        x, y = evt.xdata, evt.ydata
        tmp = getRiver(self, self.riv, x, y)
        if tmp != None:
            dlg = GetData(self.parent, tmp)
            dlg.ShowModal()

            if dlg.result_xpos:
                if  ((np.float(dlg.result_xpos) < len(self.grd.xir)) & (np.float(dlg.result_ypos) < len(self.grd.etar))):
                    tmp.xpos = np.array([np.float(dlg.result_xpos)])
                    tmp.ypos = np.array([np.float(dlg.result_ypos)])
                    tmp.direction = np.array([np.float(dlg.result_direction)])
                    tmp.sign = np.array([np.float(dlg.result_sign)])

                    plot_river(self, tmp, alpha=0.5)
                    dlg2 = wx.MessageDialog(None, "Store new river location? (Old position will be deleted)",'Updater',wx.YES_NO | wx.ICON_QUESTION)
                    result = dlg2.ShowModal()

                    if result == wx.ID_YES:
                        updateRiver(self, tmp)
                    else:
                        remove_river_from_plot(self,tmp)
                        print('Discarding river edit')

                    dlg2.Destroy()
                else:
                    print('Invalid postion. Maximum x is {}, Maximum y is {}'.format(len(self.grd.xir)-1, len(self.grd.etar)-1))

            else:
                self.parent.log.AppendText("No Input found\n")

    def OnSplitRiver(self, evt):
        mplpanel = self.parent

        if self.river_cid is None:
            self.river_cid = mplpanel.canvas.mpl_connect('button_press_event', self.splitRiver)
        else:
            mplpanel.canvas.mpl_disconnect(self.river_cid)
            self.river_cid = None

    def splitRiver(self, evt):

        if evt.inaxes != self.parent.axes: return

        x, y = evt.xdata, evt.ydata
        tmp = getRiver(self, self.riv, x, y)

        if tmp != None:
            dlg = SplitRiverDlg(self.parent, tmp)
            dlg.ShowModal()

            if any(dlg.result_xpos):


                # Make tmp river object same size as  the number of new river points
                tmp =  tmp[np.zeros( [len(np.where(dlg.result_xpos)[0])] , dtype=int)]

                # Update the values to those given by the user
                new = tmp.__dict__
                old = dlg.__dict__
                fields = ['xpos', 'ypos', 'sign', 'direction']
                for key in fields:
                    for n in range(len(np.where(np.isfinite(old['result_'+key].astype(np.float)))[0])):
                        new[key][n] = float(old['result_'+key][np.where(np.isfinite(old['result_'+key].astype(np.float)))[0]][n])

                # We need to scale the transport
                tmp.transport = tmp.transport/len(np.where(dlg.result_xpos)[0])
                # and river numbers must be unique.
                # determine maximum river number in self.riv, and assign new values higher than maximum
                # First entry in splitted river may keep old river number

                for n in range(1,len(tmp.riverno)):
                    tmp.riverno[n] = self.riv.riverno.max() + n

                plot_river(self, tmp, alpha=0.5)


                dlg2 = wx.MessageDialog(None, "Store new river locations? (Old position will be deleted)",'Updater',wx.YES_NO | wx.ICON_QUESTION)
                result = dlg2.ShowModal()

                if result == wx.ID_YES:


                    remove_river_from_plot(self, self.riv, np.where(self.riv.riverno == tmp.riverno[0])[0][0] )
                    self.riv.delete(np.where(self.riv.riverno == tmp.riverno[0]))
                    self.riv.insert(tmp)

                    for n in tmp.riverno:
                        remove_river_from_plot(self,tmp[np.where(tmp.riverno==n)])
                        ind = np.where(self.riv.riverno == n)[0]
                        plot_river(self, self.riv, index = ind)


                    # Call backup to save new file
                    self.riv.backup()
                else:
                    for n in range(len(tmp.riverno)):
                        remove_river_from_plot(self,tmp, n)
                    print('Discarding river split')




            else:
                self.parent.log.AppendText("No Input found\n")

    def OnSaveRiver(self, evt):

        openFileDialog =  wx.FileDialog(self.parent, "Store new river file",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind

        # save the current contents in the file
        newriverfile = openFileDialog.GetPath()
        newriv = mergeRivers(self.riv)
        if newriv is None:
            return

        self.riv.save(newriverfile)

def load_bitmap(filename, direc=None):
    """
    Load a bitmap file from the ./icons subdirectory.
    The filename parameter should not
    contain any path information as this is determined automatically.

    Returns a wx.Bitmap object
    copied from matoplotlib resources
    """

    if not direc:
        basedir = os.path.join(PROJECT_DIR,'icons')
    else:
        basedir = os.path.join(PROJECT_DIR, direc)

    bmpFilename = os.path.normpath(os.path.join(basedir, filename))
    if not os.path.exists(bmpFilename):
        raise IOError('Could not find bitmap file "%s"; dying'%bmpFilename)

    bmp = wx.Bitmap(bmpFilename)
    return bmp


gridfile = get_arg(1)
riverfile = get_arg(2)
rivergrid = get_arg(3)

app = WIT.InspectableApp()
window = CanvasFrame(gridfile, riverfile)
print('\nUpper panel GUI options (from left to right):\n\n')
for key in window.maintoolbar.tools_params:
    print('{}: {}'.format(key.ljust(20), window.maintoolbar.tools_params[key][-1]))
print('\n')
window.Show()
app.MainLoop()
