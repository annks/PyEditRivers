import wx, sys
from numpy import empty

class GetData(wx.Dialog):
    DIRECTIONS = ['north', 'south', 'east', 'west']
    def __init__(self, parent, tmp):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Edit River number {}".format(int(tmp.riverno[0])), size= (360,270))

        self.panel = wx.Panel(self,wx.ID_ANY)
        self.tmp = tmp

        self.infowestsouth  = wx.StaticText(self.panel, label = 'West and southwards flowing rivers   ->   on land', pos=(20,20))
        self.infoeastnorth  = wx.StaticText(self.panel, label = 'East and northwards flowing rivers    ->   on water', pos=(20,40))
        self.infodir  = wx.StaticText(self.panel, label = '(directions are according to model grid)', pos=(30,70))


        self.lblxpos = wx.StaticText(self.panel, label="Xpos", pos=(50,100))
        self.xpos = wx.TextCtrl(self.panel, value=str(tmp.xpos[0]), pos=(20,120), size=(100,-1))

        self.lblypos = wx.StaticText(self.panel, label="Ypos", pos=(160,100))
        self.ypos = wx.TextCtrl(self.panel, value=str(tmp.ypos[0]), pos=(130,120), size=(100,-1))

        direction, sign, retning = determine_dir(tmp.direction[0], tmp.sign[0])
        self.lbldir = wx.StaticText(self.panel, label="Direction", pos=(260,100))
        #self.direction = wx.TextCtrl(self.panel, value=retning, pos=(240,120), size=(100,-1))
        self.direction = wx.Choice(self.panel, choices=self.DIRECTIONS, pos=(240,120), size=(100,-1))
        self.direction.SetSelection(self.DIRECTIONS.index(retning))

        self.saveButton =wx.Button(self.panel, label="Save", pos=(80,180))
        self.closeButton =wx.Button(self.panel, label="Cancel", pos=(180,180))
        self.saveButton.Bind(wx.EVT_BUTTON, self.SaveConnString)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Show()

    def OnQuit(self, event):
        self.result_xpos = None
        self.result_ypos = None
        self.result_direction = None
        self.result_sign = None
        self.Destroy()

    def SaveConnString(self, event):
        self.result_xpos = self.xpos.GetValue()
        self.result_ypos = self.ypos.GetValue()
        i = self.direction.GetSelection()
        retning = self.DIRECTIONS[i]
        self.result_direction, self.result_sign, retn = determine_dir(retning=retning)
        self.Destroy()

class SplitRiverDlg(wx.Dialog):
    DIRECTIONS = ['north', 'south', 'east', 'west']

    varnames = ['result_xpos', 'result_ypos', 'result_direction', 'result_sign']
    def __init__(self, parent, tmp):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Spit River number {}".format(int(tmp.riverno[0])), size= (360,470))

        direction, sign, retning = determine_dir(tmp.direction[0], tmp.sign[0])

        self.panel = wx.Panel(self,wx.ID_ANY)
        self.tmp = tmp


        self.infowestsouth  = wx.StaticText(self.panel, label = 'West and southwards flowing rivers   ->   on land', pos=(20,20))
        self.infoeastnorth  = wx.StaticText(self.panel, label = 'East and northwards flowing rivers    ->   on water', pos=(20,40))
        self.infodir  = wx.StaticText(self.panel, label = '(directions are according to model grid)', pos=(30,70))


        self.lblxpos1 = wx.StaticText(self.panel, label="Xpos", pos=(50,100))
        self.xpos1 = wx.TextCtrl(self.panel, value=str(tmp.xpos[0]), pos=(20,120), size=(100,-1))

        self.lblypos1 = wx.StaticText(self.panel, label="Ypos", pos=(160,100))
        self.ypos1 = wx.TextCtrl(self.panel, value=str(tmp.ypos[0]), pos=(130,120), size=(100,-1))

        self.lbldir1 = wx.StaticText(self.panel, label="Direction", pos=(260,100))
        self.direction1 = wx.Choice(self.panel, choices=self.DIRECTIONS, pos=(240,120), size=(100,-1))
        self.direction1.SetSelection(self.DIRECTIONS.index(retning))


        self.xpos2 = wx.TextCtrl(self.panel, value='', pos=(20,155), size=(100,-1))

        self.ypos2 = wx.TextCtrl(self.panel, value='', pos=(130,155), size=(100,-1))

        self.direction2 = wx.Choice(self.panel, choices=self.DIRECTIONS, pos=(240,155), size=(100,-1))
        self.direction2.SetSelection(self.DIRECTIONS.index(retning))


        self.xpos3 = wx.TextCtrl(self.panel, value='', pos=(20,190), size=(100,-1))

        self.ypos3 = wx.TextCtrl(self.panel, value='', pos=(130,190), size=(100,-1))

        self.direction3 = wx.Choice(self.panel, choices=self.DIRECTIONS, pos=(240,190), size=(100,-1))
        self.direction3.SetSelection(self.DIRECTIONS.index(retning))

        self.xpos4 = wx.TextCtrl(self.panel, value='', pos=(20,225), size=(100,-1))

        self.ypos4 = wx.TextCtrl(self.panel, value='', pos=(130,225), size=(100,-1))

        self.direction4 = wx.Choice(self.panel, choices=self.DIRECTIONS, pos=(240,225), size=(100,-1))
        self.direction4.SetSelection(self.DIRECTIONS.index(retning))

        self.xpos5 = wx.TextCtrl(self.panel, value='', pos=(20,260), size=(100,-1))

        self.ypos5 = wx.TextCtrl(self.panel, value='', pos=(130,260), size=(100,-1))

        self.direction5 = wx.Choice(self.panel, choices=self.DIRECTIONS, pos=(240,260), size=(100,-1))
        self.direction5.SetSelection(self.DIRECTIONS.index(retning))


        self.saveButton =wx.Button(self.panel, label="Save", pos=(80,310))
        self.closeButton =wx.Button(self.panel, label="Cancel", pos=(200,310))
        self.saveButton.Bind(wx.EVT_BUTTON, self.SaveConnString)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Show()

    def OnQuit(self, event):

        me = self.__dict__

        for key in self.varnames:
            me[key] = empty([5], dtype=object)
            me[key][:] = None

        self.Destroy()

    def SaveConnString(self, event):

        varnames = ['result_xpos', 'result_ypos']
        #, 'result_direction', 'result_sign']

        me = self.__dict__
        for key in self.varnames:
            me[key] = empty([5,], dtype=object)

        for n in range(0,5):
            if  me['xpos'+str(n+1)].GetValue() and me['ypos'+str(n+1)].GetValue():

                me['result_xpos'][n] = me['xpos'+str(n+1)].GetValue()
                me['result_ypos'][n] = me['ypos'+str(n+1)].GetValue()

                i = me['direction'+str(n+1)].GetSelection()
                retning = self.DIRECTIONS[i]

                me['result_direction'][n], me['result_sign'][n], retn = determine_dir(retning=retning)

        self.Destroy()

def determine_dir(direction=None, sign=None, retning=''):
    if not retning:
        # match direction and sign with the appropriate direction SaveConnString
        if direction == 1:
            if sign == -1:
                retning = 'south'
            elif sign == 1:
                retning = 'north'
            else:
                print('Invalid sign value!')
                return direction, sign, retning
        elif direction == 0:
            if sign == -1:
                retning = 'west'
            elif sign == 1:
                retning = 'east'
            else:
                print('Invalid sign value!')
                return direction, sign, retning
        else:
            print('Invalid direction value!')
            return direction, sign, retning

    else:
        if 'north' in retning.lower():
            sign = 1
            direction = 1
        elif 'west' in retning.lower():
            sign = -1
            direction = 0
        elif 'south' in retning.lower():
            sign = -1
            direction = 1
        elif 'east' in retning.lower():
            sign = 1
            direction = 0
        else:
            print('Invalid direction string!')
            return direction, sign, retning
    return direction, sign, retning

def get_arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return None
    else:
        return sys.argv[index]
