import string, sys, traceback

import scraft
from scraft import engine as oE
import guiaux
import localizer

class TextLabel(guiaux.GuiObject):
    def __init__(self, host, parent, node, styles, ego):
        self.ego = ego
        self.host = host
        self.style = styles.GetSubtag(node.GetStrAttr("style"))
        if node.GetStrAttr("text") != "": #None:
            self.defaultText = localizer.GetGameString(node.GetStrAttr("text"))
        else:
            self.defaultText = "-empty-" #""
        
        self.sprite = oE.NewSprite_("$spritecraft$font$", parent.layer)
        self.sprite.parent = parent
        self.sprite.x, self.sprite.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.sprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer")
        
        self.sprite.cfilt.color = 0xCCCCCC
        
        self.sprite.ChangeKlassTo(self.style.GetStrAttr("font"))
        self.sprite.hotspot = guiaux.GetHotspotValue(self.style.GetStrAttr("hotspot"))
        
    def Dispose(self):
        self.sprite.Dispose()
        
    def Show(self, flag):
        self.sprite.visible = flag
        
    def UpdateView(self, data):
        try:
            text = data.get(self.ego+"#text")
            if text != None:
                self.sprite.text = text
            else:
                self.sprite.text = self.defaultText
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        