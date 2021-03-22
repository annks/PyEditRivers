import numpy as np
import wx
from .plot_tools import plot_river, remove_river_from_plot
from .romsnc import river
def check_rivers(riv, M, H):
    river_status =''
    for n in range(len(riv.riverno)):

        i = int(riv.xpos[n])
        j = int(riv.ypos[n])

        if riv.direction[n] == 0: # U point
            if riv.sign[n] > 0: # from left
                # Må ha (i-1,j) på land og (i,j) = sjø¸
                if M[j,i-1]: river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j,i]: river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % ( riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
            else:
                # Må ha (i,j) på land og (i-1,j) på sjø¸
                if M[j,i]:   river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j,i-1]: river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % (riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
        else: # V-point
            if riv.sign[n] > 0: # "up"-wards
                # Må ha (i,j-1) på land og (i,j) på sjø¸
                if M[j-1,i]:    river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j,i]: river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % (riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
            else:
                # Må ha (i,j) på land og (i,j-1) på sjø¸
                if M[j,i]:       river_status =  '\n'.join([river_status,  "Error with river, source {} from sea cell".format(riv.riverno[n])])
                if not M[j-1,i]:  river_status = '\n'.join([river_status, "Error with river, source {} to land cell".format(riv.riverno[n])])
                river_status = '\n'.join([river_status, "grid cell: %6d %7d %8s %7d %8s %10.1f %6d %6d\n" % ( riv.riverno[n], i,"", j,"", H[j,i], riv.direction[n], riv.sign[n])])
    return river_status

def getRiver(self,riv, x, y):
    xind = np.argmin(np.abs(riv.xpos - x))
    yind = np.argmin(np.abs(riv.ypos -y))

    if not xind == yind:
        print('Chosen position is ambigous, enter river number.')
        dlg = wx.TextEntryDialog(self.parent, 'Enter river number to edit', value='')
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            riverno = int(dlg.GetValue())
            if riverno in riv.riverno:
                return riv[np.where(riv.riverno == riverno)]
            else:
                print('Invalid river number, try again')
                dlg.Destroy()
                return None
        else:
            dlg.Destroy()
            return None
    else:
        return riv[xind]

def updateRiver(self, tmp):
    remove_river_from_plot(self,tmp)
    remove_river_from_plot(self, self.riv, np.where(self.riv.riverno == tmp.riverno)[0][0] )

    self.riv[np.where(self.riv.riverno == tmp.riverno)[0]] = tmp
    plot_river(self, self.riv, index = np.where(self.riv.riverno == tmp.riverno)[0][0])

    self.riv.backup(np.where(self.riv.riverno == tmp.riverno)[0])
    return

def mergeRivers(riv):
    unique_pos = set()

    for n in range(len(riv.riverno)):
        unique_pos.add((riv.xpos[n], riv.ypos[n], riv.direction[n]))
    unique_pos = list(unique_pos)
    print(len(unique_pos), len(riv.riverno))
    newriv = river()
    newriv.time = riv.time[:]
    newriv.salt = np.zeros([len(newriv.time), riv.salt.shape[1], 0])
    newriv.temp = np.zeros([len(newriv.time), riv.salt.shape[1], 0])
    newriv.transport = np.zeros([len(newriv.time),  0])
    newriv.Vshape = np.zeros([riv.salt.shape[1],  0])




    for n in range(len(unique_pos)):
        index = np.where((riv.xpos == unique_pos[n][0]) & (riv.ypos == unique_pos[n][1]) & (riv.direction == unique_pos[n][2]) )[0]
        if len(index) == 1:
            newriv.riverno = np.insert(newriv.riverno, len(newriv.riverno), values = riv.riverno[index].squeeze(), axis = 0)
            newriv.xpos = np.insert(newriv.xpos, len(newriv.xpos), values = riv.xpos[index].squeeze(), axis = 0)
            newriv.ypos = np.insert(newriv.ypos, len(newriv.ypos), values = riv.ypos[index].squeeze(), axis = 0)
            newriv.direction = np.insert(newriv.direction, len(newriv.direction), values = riv.direction[index].squeeze(), axis = 0)
            newriv.flag = np.insert(newriv.flag, len(newriv.flag), values = riv.flag[index].squeeze(), axis = 0)
            newriv.sign = np.insert(newriv.sign, len(newriv.sign), values = riv.sign[index].squeeze(), axis = 0)
            newriv.transport = np.insert(newriv.transport, newriv.transport.shape[-1], values= np.abs(riv.transport[:, index].squeeze())*riv.sign[index].squeeze() , axis=-1)
            newriv.Vshape = np.insert(newriv.Vshape, newriv.Vshape.shape[-1], values= riv.Vshape[:, index].squeeze(), axis=-1)
            newriv.temp = np.insert(newriv.temp, newriv.temp.shape[-1], values= riv.temp[:,:, index].squeeze(), axis=-1)
            newriv.salt = np.insert(newriv.salt, newriv.salt.shape[-1], values= riv.salt[:,:, index].squeeze(), axis=-1)
        else:
            if len(np.unique(riv.direction[index])) != 1:
                print('ERROR: Attempting to merge rivers running in different directions')
                print(np.unique(riv.riverno[index]))
                return None
            if len(np.unique(riv.sign[index])) != 1:
                print('ERROR: Attempting to merge rivers running in opposite directions')
                print(np.unique(riv.riverno[index]))
                return None

            newriv.riverno = np.insert(newriv.riverno, len(newriv.riverno), values = np.min(riv.riverno[index].squeeze()), axis = 0)
            newriv.orgriverno = np.insert(newriv.orgriverno, len(newriv.orgriverno), values = list(riv.riverno[index].squeeze()), axis = 0)
            newriv.xpos = np.insert(newriv.xpos, len(newriv.xpos), values = riv.xpos[index[0]].squeeze(), axis = 0)
            newriv.ypos = np.insert(newriv.ypos, len(newriv.ypos), values = riv.ypos[index[0]].squeeze(), axis = 0)
            newriv.direction = np.insert(newriv.direction, len(newriv.direction), values = riv.direction[index[0]].squeeze(), axis = 0)
            newriv.flag = np.insert(newriv.flag, len(newriv.flag), values = riv.flag[index[0]].squeeze(), axis = 0)
            newriv.sign = np.insert(newriv.sign, len(newriv.sign), values = riv.sign[index[0]].squeeze(), axis = 0)
            newriv.transport = np.insert(newriv.transport, newriv.transport.shape[-1], values= np.sum(np.abs(riv.transport[:, index]).squeeze(), axis=-1)*riv.sign[index[0]] , axis=-1)
            newriv.Vshape = np.insert(newriv.Vshape, newriv.Vshape.shape[-1], values= np.mean(riv.Vshape[:, index],axis=-1).squeeze(), axis=-1)
            newriv.temp = np.insert(newriv.temp, newriv.temp.shape[-1], values= np.mean(riv.temp[:,:, index],axis=-1).squeeze(), axis=-1)
            newriv.salt = np.insert(newriv.salt, newriv.salt.shape[-1], values= np.mean(riv.salt[:,:, index], axis=-1).squeeze(), axis=-1)
    return newriv
