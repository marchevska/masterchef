import scraft

__klassNameCounter = 0

def GenerateUniqueKlassName():
    global __klassNameCounter
    __klassNameCounter += 1
    return "$teggo$GUIUnqueKlass$"+str(__klassNameCounter)

class GuiObject(object):
    def __init__(self):
        pass
    def Dispose(self):
        pass
    def UpdateModel(self, data):
        pass
    def UpdateView(self, data = {}):
        pass
    def Show(self, flag):
        pass
    def Activate(self, flag):
        pass
    
    
def GetHotspotValue(str):
    allHotspots = {
            "LeftTop": scraft.HotspotLeftTop,
            "LeftCenter": scraft.HotspotLeftCenter,
            "LeftBottom": scraft.HotspotLeftBottom,
            "CenterTop": scraft.HotspotCenterTop,
            "Center": scraft.HotspotCenter,
            "CenterBottom": scraft.HotspotCenterBottom,
            "RightTop": scraft.HotspotRightTop,
            "RightCenter": scraft.HotspotRightCenter,
            "RightBottom": scraft.HotspotRightBottom
        }
    if str in allHotspots.keys():
        return allHotspots[str]
    else:
        return 0

    
