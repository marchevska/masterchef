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
        self.statehost = host
        self.style = styles.GetSubtag(node.GetStrAttr("style"))
        self.textDefault = localizer.GetGameString(node.GetStrAttr("textDefault"))
        self.styleDefault = self.style
        self.text = ""
        self.hotspotDefault = scraft.HotspotCenter
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
        self.Background.x, self.Background.y = self.style.GetTag("Background").GetIntAttr("x"), self.style.GetTag("Background").GetIntAttr("y")
        
        self.TextSprite = oE.NewSprite_("$spritecraft$font$", parent.layer)
        self.TextSprite.parent = self.Dummy
        if self.style.GetTag("Text") != None:
            self.TextSprite.hierarchy.xScale, self.TextSprite.hierarchy.yScale = False, False
            self.TextSprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Text").GetIntAttr("sublayer")
            self.TextSprite.x, self.TextSprite.y = self.style.GetTag("Text").GetIntAttr("x"), self.style.GetTag("Text").GetIntAttr("y")
        #self._SetHotspot()
        
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
            
            if self.style.GetTag("Text") != None:
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
        if self.style.GetTag("HitArea").HasAttr("hotspot"):
            self.Dummy.hotspot = guiaux.GetHotspotValue(self.style.GetTag("HitArea").GetStrAttr("hotspot"))
        else:
            self.Dummy.hotspot = self.hotspotDefault
        if self.style.GetTag("Background").HasAttr("hotspot"):
            self.Background.hotspot = guiaux.GetHotspotValue(self.style.GetTag("Background").GetStrAttr("hotspot"))
        else:
            self.Background.hotspot = self.hotspotDefault
        if self.style.GetTag("Text") != None and self.style.GetTag("Text").HasAttr("hotspot"):
            self.TextSprite.hotspot = guiaux.GetHotspotValue(self.style.GetTag("Text").GetStrAttr("hotspot"))
        else:
            self.TextSprite.hotspot = self.hotspotDefault
        
    def UpdateView(self, data):
        try:
            style = data.get(self.ego+"#style")
            if style != None:
                self.style = style
            else:
                self.style = self.styleDefault
            text = data.get(self.ego+"#text")
            if text != None:
                self.text = text
            else:
                self.text = self.textDefault
            x = data.get(self.ego+"#x")
            if x != None:
                self.Dummy.x = x
            y = data.get(self.ego+"#y")
            if y != None:
                self.Dummy.y = y
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
                self.statehost.LastButtonPressed = self.ego
                self._SetState("Down")
        
    def _OnMouseUp(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1 and self.statehost.LastButtonPressed == self.ego:
                self._SetState("Roll")
                if callable(self.command):
                    self.command(self.ego)
                else:
                    self.host.ButtonAction(self.command)
                #globalvars.Musician.PlaySound(self.style.GetStrAttr("sound"))
            self.statehost.LastButtonPressed = None

class RadioButton(PushButton):
    def __init__(self, host, parent, node, styles, ego):
        PushButton.__init__(self, host, parent, node, styles, ego)
        self.selected = False

    def UpdateView(self, data):
        try:
            PushButton.UpdateView(self, data)
            self.selected = (data.get(self.ego+"#selected"))
            if self.selected:
                self._SetState("Select")
            elif data.get(self.ego+"#disabled"):
                self._SetState("Inert")
            else:
                self._SetState("Up")
        except:
            pass
        
    def _OnMouseOver(self, sprite, flag):
        if self.state != "Inert":
            if self.selected:
                if flag:
                    self._SetState("SelectRoll")
                else:
                    self._SetState("Select")
            else:
                if flag:
                    self._SetState("Roll")
                else:
                    self._SetState("Up")
        
    def _OnMouseDown(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1:
                self.statehost.LastButtonPressed = self.ego
                if self.selected:
                    self._SetState("SelectDown")
                else:
                    self._SetState("Down")
        
    def _OnMouseUp(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1 and self.statehost.LastButtonPressed == self.ego:
                if self.selected:
                    self._SetState("SelectRoll")
                else:
                    self._SetState("Roll")
                if callable(self.command):
                    self.command(self.ego)
                else:
                    self.host.ButtonAction(self.command)
                #globalvars.Musician.PlaySound(self.style.GetStrAttr("sound"))
            self.statehost.LastButtonPressed = None

class CheckBox(PushButton):
    def __init__(self, host, parent, node, styles, ego):
        PushButton.__init__(self, host, parent, node, styles, ego)
        self.hotspotDefault = scraft.HotspotLeftCenter
        self.CheckSprite = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.CheckSprite.parent = self.Dummy
        self.CheckSprite.hierarchy.xScale, self.CheckSprite.hierarchy.yScale = False, False
        self.CheckSprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Check").GetIntAttr("sublayer")
        self.CheckSprite.x, self.CheckSprite.y = self.style.GetTag("Check").GetIntAttr("x"), self.style.GetTag("Check").GetIntAttr("y")
        
        self.Checked = node.GetBoolAttr("checked")
        self.statehost.presenter.data[self.ego+"#checked"] = self.Checked            
        
    def _SetState(self, state = "Up"):
        self.CheckSprite.ChangeKlassTo(self.style.GetTag("Check").GetStrAttr("sprite"))
        self.CheckSprite.visible = self.Checked
        PushButton._SetState(self, state)
        if self.style.GetTag("HitArea").GetBoolAttr("adjustWidth") == True:
            self.Dummy.xSize = self.TextSprite.x + self.TextSprite.width + self.style.GetTag("HitArea").GetIntAttr("minDX")
        
    def _SetHotspot(self):
        if self.style.GetTag("Check").HasAttr("hotspot"):
            self.CheckSprite.hotspot = guiaux.GetHotspotValue(self.style.GetTag("Check").GetStrAttr("hotspot"))
        else:
            self.CheckSprite.hotspot = self.hotspotDefault
        PushButton._SetHotspot(self)
        
    def UpdateView(self, data):
        try:
            checked = data.get(self.ego+"#checked")
            if checked != None:
                self.Checked = checked
            PushButton.UpdateView(self, data)
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def Dispose(self):
        self.CheckSprite.Dispose()
        PushButton.Dispose()
        
    def _OnMouseUp(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1 and self.statehost.LastButtonPressed == self.ego:
                self.Checked = not self.Checked
                self.statehost.presenter.data[self.ego+"#checked"] = self.Checked
                self._SetState("Roll")
                #globalvars.Musician.PlaySound(self.style.GetStrAttr("sound"))
            self.statehost.LastButtonPressed = None

    
