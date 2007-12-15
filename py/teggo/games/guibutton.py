#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE
import guiaux
import localizer

class PushButton(guiaux.GuiObject, scraft.Dispatcher):
    def __init__(self, host, parent, node, styles, ego):
        self.ego = ego
        self.host = host
        self.style = styles.GetSubtag(node.GetStrAttr("style"))
        self.textDefault = localizer.GetGameString(node.GetStrAttr("textDefault"))
        self.text = ""
        if node.GetStrAttr("command") != "":
            self.command = node.GetStrAttr("command")
        else:
            self.command = None
        self.state = None
        
        self.Dummy = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Dummy.parent = parent
        self.Dummy.x, self.Dummy.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.Dummy.xSize, self.Dummy.ySize = self.style.GetTag("HitArea").GetIntAttr("width"), self.style.GetTag("HitArea").GetIntAttr("height")
        self.Dummy.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("HitArea").GetIntAttr("sublayer")
        self.Dummy.dispatcher = scraft.Dispatcher(self)
        
        self.Background = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Background.parent = self.Dummy
        self.Background.hierarchy.xScale, self.Background.hierarchy.yScale = False, False
        self.Background.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Background").GetIntAttr("sublayer")
        self.Background.x, self.Background.y = 0, 0 
        
        self.TextSprite = oE.NewSprite_("$spritecraft$font$", parent.layer)
        self.TextSprite.parent = self.Dummy
        self.TextSprite.hierarchy.xScale, self.TextSprite.hierarchy.yScale = False, False
        self.TextSprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Text").GetIntAttr("sublayer")
        self.TextSprite.x, self.TextSprite.y = 0, 0 
        self._SetHotspot()
        
    def _SetState(self, state = "Up"):
        try:
            self.state = state
            if self.style.GetTag("Background").GetSubtag(state) != None and \
                    self.style.GetTag("Background").GetSubtag(state).HasAttr("sprite"):
                backgroundKlass = self.style.GetTag("Background").GetSubtag(state).GetStrAttr("sprite")
            elif self.style.GetTag("Background").GetSubtag("Default") != None and \
                    self.style.GetTag("Background").GetSubtag("Default").HasAttr("sprite"):
                backgroundKlass = self.style.GetTag("Background").GetSubtag("Default").GetStrAttr("sprite")
            else:
                backgroundKlass = "$spritecraft$dummy$"
            self.Background.ChangeKlassTo(backgroundKlass)
            if self.style.GetTag("Background").GetSubtag(state) != None:
                self.Background.frno = self.style.GetTag("Background").GetSubtag(state).GetIntAttr("frno")
            else:
                self.Background.frno = self.style.GetTag("Background").GetSubtag("Default").GetIntAttr("frno")
            
            if self.style.GetTag("Text").GetSubtag(state) != None and \
                    self.style.GetTag("Text").GetSubtag(state).HasAttr("font"):
                textKlass = self.style.GetTag("Text").GetSubtag(state).GetStrAttr("font")
            elif self.style.GetTag("Text").GetSubtag("Default") != None and \
                    self.style.GetTag("Text").GetSubtag("Default").HasAttr("font"):
                textKlass = self.style.GetTag("Text").GetSubtag("Default").GetStrAttr("font")
            else:
                textKlass = "$spritecraft$dummy$"
            self.TextSprite.ChangeKlassTo(textKlass)
            self.TextSprite.text = self.text
            self._SetHotspot()
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
            
        
    def _SetHotspot(self):
        self.Dummy.hotspot = scraft.HotspotCenter
        self.Background.hotspot = scraft.HotspotCenter
        self.TextSprite.hotspot = scraft.HotspotCenter
        
    def UpdateView(self, data):
        try:
            text = data.get(self.ego+"#text")
            if text != None:
                self.text = text
            else:
                self.text = self.textDefault
            if data.get(self.ego+"#disabled"):
                self._SetState("Inert")
            else:
                self._SetState("Up")
            if data.get(self.ego+"#hidden"):
                self.Show(False)
            else:
                self.Show(True)
            if self.command == None:
                self.command = data.get(self.ego+"#action")
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def Dispose(self):
        self.TextSprite.Dispose()
        self.Background.Dispose()
        self.Dummy.Dispose()
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.Background.visible = flag
        self.TextSprite.visible = flag
        
    #активирует кнопку, когда ее диалог становится активным
    def Activate(self, flag):
        if flag:
            self.Dummy.dispatcher = self
        else:
            self.Dummy.dispatcher = None
        
    def _OnMouseOver(self, sprite, flag):
        if self.state != "Inert":
            if flag:
                self._SetState("Roll")
            else:
                self._SetState("Up")
        
    def _OnMouseDown(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1:
                self.host.LastButtonPressed = self.ego
                self._SetState("Down")
        
    def _OnMouseUp(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1 and self.host.LastButtonPressed == self.ego:
                self._SetState("Roll")
                if callable(self.command):
                    self.command(self.ego)
                else:
                    self.host.ButtonAction(self.command)
                #globalvars.Musician.PlaySound(self.style.GetStrAttr("sound"))
            self.host.LastButtonPressed = None

class RadioButton(PushButton):
    def __init__(self, host, parent, node, styles, ego):
        PushButton.__init__(self, host, parent, node, styles, ego)
        self.host = node.GetStrAttr("group")

    def UpdateView(self, data):
        try:
            PushButton.UpdateView(self, data)
            if data.get(self.ego+"#selected"):
                self._SetState("Select")
            else:
                self._SetState("Up")
        except:
            pass
        
        
    
class RadioButtonsGroup(guiaux.GuiObject):
    def __init__(self):
        pass
    
