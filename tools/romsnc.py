from netCDF4 import Dataset
from numpy import array, sign, where, round, argmin, abs, ones_like,squeeze, concatenate, delete, arange, unique, sum

import os
import matplotlib.pyplot as plt

from globalvars import *
from .obs_ijpos import obs_ijpos



class RomsGrid(object):
    """
    Stores and manipulates netcdf ROMS grid file information
    """
    def __init__(self,filename):
        self.filename = filename
        self.ncfile = Dataset(filename, mode='r')
        self.lonr  = self.ncfile.variables['lon_rho'][:]
        self.latr  = self.ncfile.variables['lat_rho'][:]
        try:
            self.xir  = self.ncfile.variables['xi_rho'][:]
            self.etar  = self.ncfile.variables['eta_rho'][:]
        except KeyError:
            self.xir = arange(self.lonr.shape[1])
            self.etar = arange(self.lonr.shape[0])

        self.lonu  = self.ncfile.variables['lon_u'][:]
        self.latu  = self.ncfile.variables['lat_u'][:]
        self.lonv  = self.ncfile.variables['lon_v'][:]
        self.latv  = self.ncfile.variables['lat_v'][:]
        self.h     = self.ncfile.variables['h'][:]
        self.maskr = self.ncfile.variables['mask_rho'][:]
        self.masku = self.ncfile.variables['mask_u'][:]
        self.maskv = self.ncfile.variables['mask_v'][:]


class river(object):
    """
    Stores netcdf river information
    """
    def __init__(self, filename=None, rivergrid=None, gridfile=None):
        self.filename = filename
        if filename:
            self.ncfile = Dataset(filename, mode='r')
            if rivergrid:
                tmp  = Dataset(rivergrid, 'r')
                lons = []
                lats = []
                xposi = self.ncfile.variables['river_Xposition'][:]
                yposi = self.ncfile.variables['river_Eposition'][:]

                for n in range(len(xposi)):
                    lons.append(tmp.variables['lon_rho'][yposi[n], xposi[n]])
                    lats.append(tmp.variables['lat_rho'][yposi[n], xposi[n]])

                self.xpos, self.ypos = obs_ijpos(gridfile, array(lons), array(lats), 'r')
            else:
                self.xpos  = self.ncfile.variables['river_Xposition'][:]
                self.ypos  = self.ncfile.variables['river_Eposition'][:]

            if len(where(self.xpos > -999)[0]):
                print('\n{} river(s) from the input file falls outside the domain, \nand have been removed from river object.'.format(len(self.xpos) - len(where(self.xpos > -999)[0])) )
                print('\nPlot rivers on original grid to see which rivers were removed.')
            self.direction  = self.ncfile.variables['river_direction'][where(self.xpos > -999)[0]]
            self.riverno = self.ncfile.variables['river'][where(self.xpos > -999)[0]]
            self.transport = self.ncfile.variables['river_transport'][:,where(self.xpos > -999)[0]]
            self.sign = sign(sum(self.transport, axis=0))
            self.flag = self.ncfile.variables['river_flag'][where(self.xpos > -999)[0]]
            self.temp = self.ncfile.variables['river_temp'][:,:,where(self.xpos > -999)[0]]
            self.salt = self.ncfile.variables['river_salt'][:,:,where(self.xpos > -999)[0]]
            self.Vshape = self.ncfile.variables['river_Vshape'][:,where(self.xpos > -999)[0]]
            self.time = self.ncfile.variables['river_time'][:]

            self.ypos  = round(self.ypos[where(self.xpos > -999)[0]])
            self.xpos  = round(self.xpos[where(self.xpos > -999)[0]])
            self.pltid = ones_like(self.xpos, dtype=object)
            self.txtid = ones_like(self.xpos, dtype=object)
            self.backupfile = None
            self.orgriverno = array( self.riverno[:], dtype=object)

        else:
            names = self.allvarnames()
            for key in names:
                if ('pltid' in key) or ('txtid' in key):
                    self.__dict__[key] = []
                else:
                    self.__dict__[key] = array([])

    def allvarnames(self):
        rivervars = {'time' : [1,'river_time'], 'xpos' : [1,'river_Xposition'],
		           'ypos' : [1,'river_Eposition'],'riverno' : [1,'river'],
				   'direction' : [1,'river_direction'], 'temp' : [1,'river_temp'],
				   'salt' : [1,'river_salt'] , 'flag' :[1,'river_flag'],
				   'transport' : [1,'river_transport'],'sign' : [0,'sign'] ,
				   'Vshape' : [1,'river_Vshape'],'pltid' : [0,'pltid'],
				   'txtid' : [0,'txtid'], 'orgriverno' : [0, 'orgriverno']  }
        return rivervars

    def __getitem__(self, index):
        names = self.allvarnames()
        S = river()

        me = self.__dict__
        new = S.__dict__
        if isinstance(index, tuple):
            assert len(index) == 1
            index = index[0]

        try:
            index = int(index)
            index = array([index], dtype=int)
        except TypeError:
            index = array([index], dtype=int).squeeze()
        except ValueError:
            pass # index could not be turned into an int

        for key in names:
            if 'time' in key:
                new[key] = me[key]
            else:
                new[key] = me[key][...,index]
        return S

    def __setitem__(self, index, S):
        names = self.allvarnames()
        for key in names:
            if ('pltid' in key) or ('txtid' in key):
                self.__dict__[key][squeeze(index)] = 0
            elif ('time' in key):
                continue
            else:
                if (len(self.__dict__[key].shape) == 1 ):
                    self.__dict__[key][index] = S.__dict__[key][:]
                elif  (len(self.__dict__[key].shape) == 2 ):
                    self.__dict__[key][:,index] = S.__dict__[key][:]
                elif  (len(self.__dict__[key].shape) == 3 ):
                    self.__dict__[key][:,:,index] = S.__dict__[key][:]

    def insert(self, S):

        names = self.allvarnames()

        me = self.__dict__
        new = S.__dict__


        for key in names:
            if 'time' not in key:
                me[key] = concatenate((me[key],new[key]), axis = -1)

    def delete(self, index):

        names = self.allvarnames()

        me = self.__dict__

        if isinstance(index, tuple):
            assert len(index) == 1
            index = index[0]

        try:
            index = int(index)
            index = array([index], dtype=int)
        except TypeError:
            index = array([index], dtype=int).squeeze()
        except ValueError:
            pass # index could not be turned into an int

        for key in names:
            if 'time' not in key:
                me[key] = delete(me[key], index, axis = -1)

    def save(self, outputfile):

        file_structure(outputfile, len(self.riverno), len(self.time), self.temp.shape[1])
        fid  = Dataset(outputfile, 'r+')
        rivervars = self.allvarnames()

        for key in rivervars:
            if rivervars[key][0] == 1:
                var = fid.variables[rivervars[key][1]]
                if 'transport' in key:
                    var[:] = abs(self.__dict__[key][:])*self.sign[:]
                else:
                    var[:] = self.__dict__[key][:]
            else:
                continue

        fid.close()
        for n in range(len(self.riverno)):
            print('River no {} consists of river(s) {} in the original file'.format(self.riverno[n], self.orgriverno[n]))

    def backup(self, index = None):

        rivervars = self.allvarnames()
        if index is None:
            file_structure(self.backupfile, len(self.riverno), len(self.time), self.temp.shape[1])
            fid  = Dataset(self.backupfile, 'r+')

            for key in rivervars:
                if rivervars[key][0] == 1:
                    var = fid.variables[rivervars[key][1]]
                    if 'transport' in key:
                        var[:] = abs(self.__dict__[key][:])*self.sign[:]
                    else:
                        var[:] = self.__dict__[key][:]
                else:
                    continue
            fid.close()
        else:
            fid  = Dataset(self.backupfile, 'r+')
            for key in rivervars:
                if rivervars[key][0] == 1:
                    var = fid.variables[rivervars[key][1]]
                    if 'transport' in key:
                        if (len(self.__dict__[key].shape) == 1 ):
                            var[index] = abs(self.__dict__[key][index])*self.sign[index]
                        elif  (len(self.__dict__[key].shape) == 2 ):
                            var[:,index] = abs(self.__dict__[key][:,index])*self.sign[index]
                        elif  (len(self.__dict__[key].shape) == 3 ):
                            var[:,:,index] = abs(self.__dict__[key][:,:,index])*self.sign[:,index]
                    else:
                        if (len(self.__dict__[key].shape) == 1 ):
                            var[index] = self.__dict__[key][index]
                        elif  (len(self.__dict__[key].shape) == 2 ):
                            var[:,index] = self.__dict__[key][:,index]
                        elif  (len(self.__dict__[key].shape) == 3 ):
                            var[:,:,index] = self.__dict__[key][:,:,index]
                else:
                    continue
            fid.close()
        return


def file_structure(outputfile, riverno, ntime, srho):

    fid = Dataset(outputfile,  'w')

    fid.createDimension('river', riverno)
    fid.createDimension('river_time', ntime)
    fid.createDimension('s_rho', srho)

    var = fid.createVariable('river', 'f4',  ('river',))
    var.long_name = "river runoff identification number"
    var.units = "nondimensional"
    var.field = "river, scalar"

    var = fid.createVariable('river_time', 'f4',  ('river_time',))
    var.long_name = "river runoff time"
    var.units = "day"
    var.field = "river_time, scalar, series"
    var.cycle_length = 365.25

    var = fid.createVariable('river_Xposition', 'f4',  ('river',))
    var.long_name = "river XI-position at RHO-points"
    var.units = "nondimensional"
    var.field = "river_Xposition, scalar"

    var = fid.createVariable('river_Eposition',  'f4', ('river',))
    var.long_name = "river ETA-position at RHO-points"
    var.units = "nondimensional"
    var.field = "river_Eposition, scalar"

    var = fid.createVariable('river_direction',  'f4', ('river',))
    var.long_name = "river runoff direction"
    var.units = "nondimensional"
    var.field = "river_direction, scalar"

    var = fid.createVariable('river_flag',  'f4', ('river',))
    var.long_name = "river runoff tracer flag"
    var.units = "nondimensional"
    var.field = "river_flag, scalar"
    var.option_0 = "all tracers are off"
    var.option_1 = "only temperature is on"
    var.option_2 = "only salinity is on"
    var.option_3 = "both temperature and salinity are on"

    var = fid.createVariable('river_Vshape',  'f4', ('s_rho','river',))
    var.long_name = "river runoff mass transport vertical profile"
    var.units = "nondimensional"
    var.field = "river_Vshape, scalar"

    var = fid.createVariable('river_transport',  'f4', ('river_time','river',))
    var.long_name = "river runoff vertically integrated mass transport"
    var.units = "meter3 second-1"
    var.field = "river_transport, scalar, series"
    var.time = "river_time"

    var = fid.createVariable('river_temp',  'f4', ('river_time','s_rho','river',))
    var.long_name = "river runoff potential temperature"
    var.units = "Celsius"
    var.field = "river_temp, scalar, series"
    var.time = "river_time"

    var = fid.createVariable('river_salt',  'f4', ('river_time','s_rho','river',))
    var.long_name = "river runoff salinity"
    var.units = "PSU"
    var.field = "river_salt, scalar, series"
    var.time = "river_time"

    fid.close()
