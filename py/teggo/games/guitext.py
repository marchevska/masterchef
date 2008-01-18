#!/usr/bin/env python
# -*- coding: cp1251 -*-

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
        self.styleDefault = self.style
        if node.GetStrAttr("textDefault") != "": #None:
            self.textDefault = localizer.GetGameString(node.GetStrAttr("textDefault"))
        else:
            self.textDefault = ""
        
        self.sprite = oE.NewSprite_("$spritecraft$font$", parent.layer)
        self.sprite.parent = parent
        self.sprite.x, self.sprite.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.sprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer")
        
        self._UpdateTextStyle()
        
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
                self.sprite.text = self.textDefault
            style = data.get(self.ego+"#style")
            if style != None:
                self.style = style
            else:
                self.style = self.styleDefault
            self._UpdateTextStyle()
            #cfilt = data.get(self.ego+"#cfilt")
            #if cfilt != None:
            #    self.sprite.cfilt.color = cfilt
            #else:
            #    if self.style.GetStrAttr("cfilt-color") != "":
            #        self.sprite.cfilt.color = eval(self.style.GetStrAttr("cfilt-color"))
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def _UpdateTextStyle(self):
        if self.style.GetStrAttr("cfilt-color") != "":
            self.sprite.cfilt.color = eval(self.style.GetStrAttr("cfilt-color"))
        self.sprite.ChangeKlassTo(self.style.GetStrAttr("font"))
        self.sprite.hotspot = guiaux.GetHotspotValue(self.style.GetStrAttr("hotspot"))
        

class TextEntry(guiaux.GuiObject, scraft.Dispatcher):
    def __init__(self, host, parent, node, styles, ego):
        self.ego = ego
        self.host = host
        self.statehost = host
        self.style = styles.GetSubtag(node.GetStrAttr("style"))
        self.textDefault = localizer.GetGameString(node.GetStrAttr("textDefault"))
        self.text = ""
        self.HasFocus = node.GetBoolAttr("focus")
        
        self.Dummy = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Dummy.parent = parent
        self.Dummy.x, self.Dummy.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.Dummy.xSize, self.Dummy.ySize = self.style.GetTag("HitArea").GetIntAttr("width"), self.style.GetTag("HitArea").GetIntAttr("height")
        self.Dummy.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("HitArea").GetIntAttr("sublayer")
        self.Dummy.dispatcher = scraft.Dispatcher(self)
        
        self.Background = oE.NewSprite_(self.style.GetTag("Background").GetStrAttr("sprite"), parent.layer)
        self.Background.parent = self.Dummy
        self.Background.hierarchy.xScale, self.Background.hierarchy.yScale = False, False
        self.Background.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Background").GetIntAttr("sublayer")
        self.Background.x, self.Background.y = self.style.GetTag("Background").GetIntAttr("x"), self.style.GetTag("Background").GetIntAttr("y")
        
        self.TextSprite = oE.NewSprite_(self.style.GetTag("Text").GetStrAttr("font"), parent.layer)
        self.TextSprite.parent = self.Dummy
        self.TextSprite.hierarchy.xScale, self.TextSprite.hierarchy.yScale = False, False
        self.TextSprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Text").GetIntAttr("sublayer")
        self.TextSprite.x, self.TextSprite.y = self.style.GetTag("Text").GetIntAttr("x"), self.style.GetTag("Text").GetIntAttr("y") 
        self.MaxLen = self.style.GetTag("Text").GetIntAttr("length")
        
        self.Cursor = oE.NewSprite_(self.style.GetTag("Cursor").GetStrAttr("sprite"), parent.layer)
        self.Cursor.parent = self.Dummy
        self.Cursor.hierarchy.xScale, self.Cursor.hierarchy.yScale = False, False
        self.Cursor.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Cursor").GetIntAttr("sublayer")
        self.CursorTextDX, self.CursorTextDY = self.style.GetTag("Cursor").GetIntAttr("textDX"), self.style.GetTag("Cursor").GetIntAttr("textDY")
        self.CursorFps = self.style.GetTag("Cursor").GetIntAttr("fps")
        
        if self.HasFocus:
            self.statehost.SetFocusTo(self)
        
    #активирует поле ввода, когда родительский диалог становится активным
    def Activate(self, flag):
        if flag:
            self.Dummy.dispatcher = self
        else:
            self.Dummy.dispatcher = None
        
    def GetFocus(self):
        self.HasFocus = True
        self.Cursor.visible = True
        self.Cursor.AnimateLoop(self.CursorFps)
        
    def LoseFocus(self):
        self.HasFocus = True
        self.Cursor.visible = False
        self.Cursor.StopAnimation()
    
    def UpdateView(self, data):
        try:
            text = data.get(self.ego+"#text")
            if text != None:
                self.TextSprite.text = text
            if self.HasFocus:
                self.Cursor.x = self.TextSprite.x + self.TextSprite.width + self.CursorTextDX
                self.Cursor.y = self.TextSprite.x + self.CursorTextDY
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))

    def _OnMouseDown(self, sprite, x, y, button):
        if button == 1:
            self.statehost.LastButtonPressed = self.ego
        
    def _OnMouseUp(self, sprite, x, y, button):
        if button == 1 and self.statehost.LastButtonPressed == self.ego:
            self.statehost.SetFocusTo(self)
            self.statehost.LastButtonPressed = None
            
    #-------------------------------------
    # обработка клавиатурного ввода
    # предполагается наличие ввода и
    # фокуса ввода у данного элемента
    #-------------------------------------
    def ProcessInput(self, data):
        tmpProcessed = False
        try:
            if not data.get(self.ego+"#text"):
                data[self.ego+"#text"] = ""
            tmpText = data[self.ego+"#text"]
            if oE.EvtKey() in eval(localizer.GetGameString("Str_KeyCodes")).keys():
                if oE.IsKeyPressed(scraft.Key_SHIFT) or oE.IsKeyPressed(scraft.Key_RSHIFT):
                    tmpLetter = str(eval(str(localizer.GetGameString("Str_KeyCodesShift")))[oE.EvtKey()])
                else:
                    tmpLetter = str(eval(str(localizer.GetGameString("Str_KeyCodes")))[oE.EvtKey()])
                tmpText += tmpLetter
                tmpProcessed = True
            elif oE.EvtKey() == scraft.Key_BACKSPACE:
                tmpText = tmpText[0:len(tmpText)-1]
                tmpProcessed = True
            if len(tmpText) > self.MaxLen:
                tmpText = tmpText[0:len(tmpText)-1]
            data[self.ego+"#text"] = tmpText
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        return tmpProcessed
    

class TextArea(guiaux.GuiObject):
    def __init__(self, host, parent, node, styles, ego):
        self.ego = ego
        self.host = host
        self.style = styles.GetSubtag(node.GetStrAttr("style"))
        if node.GetStrAttr("textDefault") != "": #None:
            self.textDefault = localizer.GetGameString(node.GetStrAttr("textDefault"))
        else:
            self.textDefault = ""
        self.text = self.textDefault
        self.parent = parent
        
        self.Dummy = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Dummy.parent = parent
        self.Dummy.x, self.Dummy.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.Dummy.sublayer = parent.sublayer + node.GetIntAttr("sublayer")
        
        self.Sprites = []
        
    def UpdateView(self, data):
        try:
            x = data.get(self.ego+"#x")
            if x != None:
                self.Dummy.x = x
            y = data.get(self.ego+"#y")
            if y != None:
                self.Dummy.y = y
            style = data.get(self.ego+"#style")
            if style != None:
                self.style = style
            text = data.get(self.ego+"#text")
            if text != None:
                self.text = text
            else:
                self.text = self.textDefault
            self._UpdateText()
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def _UpdateText(self):
        for spr in self.Sprites:
            spr.Dispose()
        self.Sprites = []
        self.hotspot = guiaux.GetHotspotValue(self.style.GetStrAttr("hotspot"))
        for i in range(self.style.GetIntAttr("height")/self.style.GetIntAttr("lineheight")):
            spr = oE.NewSprite_(self.style.GetStrAttr("font"), self.parent.layer)
            spr.text = ""
            spr.parent = self.Dummy
            spr.x, spr.y = 0, 0
            spr.sublayer = self.Dummy.sublayer
            spr.hotspot = self.hotspot
            spr.cfilt.color = eval(self.style.GetStrAttr("cfilt-color"))
            if self.style.GetStrAttr("cfilt-color") != "":
                self.Sprites.append(spr)
        
        #делим текст на строки. что не входит - отбрасываем
        i = 0
        tmpStr = oE.NewSprite_(self.style.GetStrAttr("font"), self.parent.layer)
        tmpStr.text = ""
        tmpStrings = string.split(self.text)
        for tmp in tmpStrings:
            tmpStr.text = string.lstrip(self.Sprites[i].text+" "+tmp)
            if tmpStr.width > self.style.GetIntAttr("width"):
                i+=1
            if i >= len(self.Sprites):
                break
            self.Sprites[i].text = self.Sprites[i].text+" "+tmp
        
        #y-координата первой строки зависит от общего числа непустых строк
        tmpTotalStrings = len(filter(lambda x: x.width>0, self.Sprites))
        if self.style.GetStrAttr("hotspot") in ("LeftTop", "CenterTop", "RightTop"):
            tmpY0 = 0
        elif self.style.GetStrAttr("hotspot") in ("LeftBottom", "CenterBottom", "RightBottom"):
            tmpY0 = -tmpTotalStrings * self.style.GetIntAttr("lineheight")
        else:
            tmpY0 = -tmpTotalStrings * self.style.GetIntAttr("lineheight")/2
        for i in range(tmpTotalStrings):
            self.Sprites[i].y = tmpY0 + i*self.style.GetIntAttr("lineheight")
        
    def Dispose(self):
        for spr in self.Sprites+[self.Dummy]:
            spr.Dispose()
        self.Sprites = []
        
    def Show(self, flag):
        self.Dummy.visible = flag
        
 