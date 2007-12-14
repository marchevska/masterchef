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
        self.defaultText = localizer.GetGameString(node.GetStrAttr("textDefault"))
        self.text = ""
        self.command = node.GetStrAttr("command")
        self.state = None
        
        self.Dummy = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Dummy.parent = parent
        self.Dummy.x, self.Dummy.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.Dummy.xSize, self.Dummy.ySize = self.style.GetTag("HitArea").GetIntAttr("width"), self.style.GetTag("HitArea").GetIntAttr("height")
        self.Dummy.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("HitArea").GetIntAttr("sublayer")
        self.Dummy.dispatcher = self
        
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
        self.state = state
        if self.style.GetTag("Background").GetSubtag(state).HasAttr("sprite"):
            backgroundKlass = self.style.GetTag("Background").GetSubtag(state).GetStrAttr("sprite")
        else:
            backgroundKlass = self.style.GetTag("Background").GetSubtag("Default").GetStrAttr("sprite")
        self.Background.ChangeKlassTo(backgroundKlass)
        self.Background.frno = self.style.GetTag("Background").GetSubtag(state).GetIntAttr("frno")
        if self.style.GetTag("Text").GetSubtag(state).HasAttr("font"):
            textKlass = self.style.GetTag("Text").GetSubtag(state).GetStrAttr("font")
        else:
            textKlass = self.style.GetTag("Text").GetSubtag("Default").GetStrAttr("font")
        self.TextSprite.ChangeKlassTo(textKlass)
        self.TextSprite.text = self.text
        self._SetHotspot()
        
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
                self.text = self.defaultText
            if data.get(self.ego+"#disabled"):
                self._SetState("Inert")
            else:
                self._SetState("Up")
        except:
            pass
        
    def Dispose(self):
        self.TextSprite.Dsipose()
        self.Background.Dispose()
        self.Dummy.Dispose()
        
    def Show(self, flag):
        self.Dummy.vsible = flag
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
                host.LastButtonPressed = self.command
                self.SetState(ButtonState_Down)
        
    def _OnMouseUp(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1:
                self._SetState("Roll")
                self.host.ButtonAction(self.command)
                globalvars.Musician.PlaySound(self.style.GetStrAttr("sound"))
            host.LastButtonPressed = None
