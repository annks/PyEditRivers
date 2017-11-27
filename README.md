PyEditRivers:
Main developer: Ann Kristin Sperrevik (annks@met.no)

An interactive tool for editing ROMS river forcing files
Requirements: wxPython, matplotlib version 2.1.0
(pip install  https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04/wxPython-4.0.0b2-cp36-cp36m-linux_x86_64.whl)

Run on command line as (command line arguments are optional):
python pyeditrivers <gridfile> <riverfile> <rivergridfile>

Features:
- Regridding of rivers from rivergridfile to gridfile - nearest location
- Edit position and direction of a river
- Verify river positions according to ROMS requirements
- Split a river between multiple (max 5) outlets (transport = transport/Noutlets)
- Merge rivers automatically (on save) if more than one river is assigned to
  the same location (transport = sum(transports) )
- Backup of progress on temporary river netcdf files
- Save: writes new river forcing files

Currently no handling of changes to number of vertical layers or vshape
