
import string, sys, traceback

import scraft
from scraft import engine as oE
import guiaux

class Image(guiaux.GuiObject):
    def __init__(self, host, parent, node, ego):
        self.ego = ego
        self.host = host
        
        #self.klassName = guiaux.GenerateUniqueKlassName()
        #oE.SstDefKlass(self.klassName, node.GetTag("sprite"))
        #self.sprite = oE.NewSprite_(self.klassName, parent.layer)
        #oE.SstUndefKlass(self.klassName)
        
        self.klassName = node.GetStrAttr("sprite")
        self.sprite = oE.NewSprite_(self.klassName, parent.layer)
        
        self.sprite.parent = parent
        self.sprite.x, self.sprite.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.sprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer")
        
    def Dispose(self):
        self.sprite.Dispose()
        
    def Show(self, flag):
        self.sprite.visible = flag
        
    def UpdateView(self, data):
        try:
            klassName = data.get(self.ego+"#klass")
            frno = data.get(self.ego+"#frno")
            if klassName != None:
                self.sprite.ChangeKlassTo(klassName)
            if frno != None:
                self.sprite.frno = int(frno)
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
