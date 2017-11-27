
def plot_river(self, riv,  alpha = 1):

    ax = self.parent.axes
    for i in range(len(riv.xpos)):
        if riv.xpos[i] > -900:
            if riv.direction[i] == 0:
                if riv.sign[i] >0:
                    markers = '>'
                else:
                    markers = '<'
                clr = 'b'
            else:
                if riv.sign[i] > 0:
                    markers = '^'
                else:
                    markers = 'v'
                clr = 'r'
            riv.pltid[i] = ax.plot(riv.xpos[i],riv.ypos[i], color = clr, marker=markers, markersize =10, alpha=alpha)[0]
            yoffset = 1.5
            riv.txtid[i] = ax.text(riv.xpos[i],riv.ypos[i]-yoffset, str(int(riv.riverno[i])),fontsize=9, ha='center',va='top',color='r', bbox = dict(boxstyle="square",ec='None',fc=(1,1,1,0.5)))

    self.parent.canvas.draw()
def remove_river_from_plot(self, riv, index = None,):
    ax = self.parent.axes
    if index:
        ax.lines.remove(riv.pltid[index])
        ax.texts.remove(riv.txtid[index])
    else:
        ax.lines.remove(riv.pltid[0])
        ax.texts.remove(riv.txtid[0])

    self.parent.canvas.draw()

def plot_grid(self,grd , vmin= DEFAULT_VMIN, vmax= DEFAULT_VMAX, cmap=DEFAULT_CMAP):


    ax = self.parent.axes
    self.pcolor = ax.pcolormesh(range(len(grd.xir)), range(len(grd.etar)), grd.maskr,
                               vmin=vmin, vmax=vmax,
                               cmap=cmap)

    ax.set_aspect('equal')

    self.parent.canvas.draw()
    self.grd = grd
    self.grd.hmin = grd.ncfile.variables['h'][:].min()
