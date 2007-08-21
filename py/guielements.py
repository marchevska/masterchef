#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Элементы ГУИ: кнопка, слайдер и т.п.
"""

import scraft
from scraft import engine as oE
from configconst import *
from constants import *
from guiconst import *
import config
import globalvars
import string

RefStates = { ButtonState_Up: ButtonState_Up, ButtonState_Roll: ButtonState_Roll,
             ButtonState_Down: ButtonState_Down, ButtonState_Inert: ButtonState_Up,
             ButtonState_Selected: ButtonState_Up }

#--------------------------------
# Кнопка с текстом
# Состоит из dummy-4-hit-area,
# кнопки и текстового спрайта (опционально - без текста)
#--------------------------------

class PushButton(scraft.Dispatcher):
    def __init__(self, name, whose, cmd, when, newKlass, frames, 
                 newLayer, newX, newY, newXSize, newYSize,
                 text = "", klasses = [], textDX = 0, textDY = 0, sound = "gui.click"):
        
        #dummy используется как hit area
        self.Dummy = MakeDummySprite(self, cmd, newX, newY, newXSize, newYSize, newLayer)
        
        #спрайт кнопки
        self.ButtonSprite = oE.NewSprite_(newKlass, newLayer)
        self.ButtonSprite.sublayer = 1
        self.ButtonSprite.hotspot = scraft.HotspotCenter
        self.ButtonSprite.x, self.ButtonSprite.y = newX, newY
        #текст на кнопке
        if klasses == []:
            self.HasText = False
        else:
            self.HasText = True
            self.TextSprite = MakeTextSprite(klasses[ButtonState_Up], newLayer,
                                        newX + textDX, newY + textDY,
                                        scraft.HotspotCenter, text)
            self.TextSprite.sublayer = 0
        
        self.ButtonFrames = frames
        self.TextKlasses = klasses
        self.ActiveWhen = when
        self.Whose = whose
        self.Sound = sound
        self.SetState(ButtonState_Up)
        
    def MoveTo(self, newX, newY):
        self.Dummy.x, self.Dummy.y = newX, newY
        self.ButtonSprite.x, self.ButtonSprite.y = newX, newY
        if self.HasText:
            self.TextSprite.x, self.TextSprite.y = newX, newY
        
    def SetButtonKlass(self, newKlass):
        self.ButtonSprite.ChangeKlassTo(newKlass)
        self.ButtonSprite.hotspot = scraft.HotspotCenter
        
    def SetSound(self, sound = "gui.click"):
        self.Sound = sound
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.ButtonSprite.visible = flag
        if self.HasText:
            self.TextSprite.visible = flag
        
    def SetText(self, newText):
        self.TextSprite.text = newText
        
    def SetState(self, state):
        self.State = state
        self.ButtonSprite.frno = self.ButtonFrames[state]
        if self.HasText:
            self.TextSprite.ChangeKlassTo(self.TextKlasses[state])
            self.TextSprite.hotspot = scraft.HotspotCenter
        #if self.ButtonSprite.mouseOver:
        #    globalvars.BlackBoard.Update(BBTag_Cursor, {"button": RefStates[state]})
        globalvars.BlackBoard.Update(BBTag_Cursor, {"button": RefStates[state]})
        
    def _OnMouseOver(self, sprite, flag):
        if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
            if flag and globalvars.StateStack[-1] == self.ActiveWhen:
                #if globalvars.LastCookie == sprite.cookie:
                #    self.SetState(ButtonState_Down)
                #else:
                    self.SetState(ButtonState_Roll)
            else:
                self.SetState(ButtonState_Up)
        
    def _OnMouseDown(self, sprite, x, y, button):
        if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
            if button == 1 and globalvars.StateStack[-1] == self.ActiveWhen:
                globalvars.LastCookie = sprite.cookie
                self.SetState(ButtonState_Down)
        
    def _OnMouseUp(self, sprite, x, y, button):
        if button == 1 and globalvars.StateStack[-1] == self.ActiveWhen:
            if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
                self.SetState(ButtonState_Roll)
                if globalvars.LastCookie == sprite.cookie and globalvars.StateStack[-1] == self.ActiveWhen:
                    globalvars.Musician.PlaySound(self.Sound)
                    self.Whose.SendCommand(sprite.cookie)
            globalvars.LastCookie = Cmd_None
        
    #def _OnMouseClick(self, sprite, x, y, button):
    #    if globalvars.StateStack[-1] == self.ActiveWhen and button == 1:
    #        if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
    #            globalvars.Musician.PlaySound("gui.click")
    #            self.Whose.SendCommand(sprite.cookie)
        
    def Kill(self):
        self.Dummy.Dispose()
        self.ButtonSprite.Dispose()
        if self.HasText:
            self.TextSprite.Dispose()
    
#--------------------------------
# Регулятор-слайдер
# Состоит из dummy-4-hit-area,
# фонового рисунка и бегунка
#--------------------------------

class Slider(scraft.Dispatcher):
    def __init__(self, name, whom, paramName, when, newKlass, frames, 
                 newLayer, newX, newY, newXSize, newYSize,
                 newXRange, newYRange, bgKlass = ""):
        #dummy используется как hit area
        self.Dummy = MakeDummySprite(self, Cmd_SliderDummy, newX, newY,
                                     newXSize, newYSize, newLayer, 2)
        
        #фоновый спрайт
        if bgKlass != "":
            self.BgSprite = oE.NewSprite_(bgKlass, newLayer)
            self.BgSprite.sublayer = 1
            self.BgSprite.hotspot = scraft.HotspotCenter
            self.BgSprite.x, self.BgSprite.y = newX, newY
            self.HasBg = True
        else:
            self.HasBg = False
        
        #спрайт бегунка
        self.SliderSprite = oE.NewSprite_(newKlass, newLayer)
        self.SliderSprite.sublayer = 0
        self.SliderSprite.hotspot = scraft.HotspotCenter
        self.SliderSprite.x, self.SliderSprite.y = newX, newY
        self.SliderSprite.cookie = Cmd_Slider
        self.SliderSprite.dispatcher = self
        
        self.XRange = newXRange
        self.YRange = newYRange
        self.SliderFrames = frames
        self.ActiveWhen = when
        self.Whom = whom
        self.Param = paramName
        self.SetState(ButtonState_Up)
        self.Dragging = False
        self.QueNo = oE.executor.Schedule(self)
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.SliderSprite.visible = flag
        if self.HasBg:
            self.BgSprite.visible = flag
        
    def SetState(self, state):
        self.State = state
        self.SliderSprite.frno = self.SliderFrames[state]
        if self.SliderSprite.mouseOver:
            globalvars.BlackBoard.Update(BBTag_Cursor, {"button": RefStates[state]})
        
    def SetValue(self, value):
        self.SliderSprite.x = self.XRange[0] + int(value*(self.XRange[1] - self.XRange[0])/100)
        self.SliderSprite.y = self.YRange[0] + int(value*(self.YRange[1] - self.YRange[0])/100)
        
    def _OnMouseOver(self, sprite, flag):
        if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
            if flag:
                if sprite.cookie == Cmd_Slider:
                    if not self.Dragging:
                        self.SetState(ButtonState_Roll)
            elif not flag:
                if sprite.cookie == Cmd_Slider:
                    if not self.Dragging:
                        self.SetState(ButtonState_Up)
                elif sprite.cookie == Cmd_SliderDummy:
                    if oE.mouseX not in range(self.XRange[0]-15, self.XRange[1]+15) \
                        or oE.mouseY not in range(self.YRange[0]-15, self.YRange[1]+15):
                        self.SetState(ButtonState_Up)
                        self.Dragging = False
        
    def _OnMouseDown(self, sprite, x, y, button):
        if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
            if button == 1 and sprite.cookie == Cmd_Slider:
                globalvars.LastCookie = sprite.cookie
                self.SetState(ButtonState_Down)
                self.Dragging = True
        
    def _OnMouseUp(self, sprite, x, y, button):
        if button == 1:
            self.Dragging = False
            globalvars.LastCookie = Cmd_None
            if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
                if sprite.cookie == Cmd_Slider:
                    self.SetState(ButtonState_Roll)
                else:
                    self.SetState(ButtonState_Up)
                    
    def _OnExecute(self, que):
        if self.Dragging:
            self.SliderSprite.x = Nearest(oE.mouseX, self.XRange)
            self.SliderSprite.y = Nearest(oE.mouseY, self.YRange)
            if self.XRange[0] == self.XRange[1]:
                tmpValue = int((self.SliderSprite.y - self.YRange[0])*100/(self.YRange[1] - self.YRange[0]))
            else:
                tmpValue = int((self.SliderSprite.x - self.XRange[0])*100/(self.XRange[1] - self.XRange[0]))
            self.Whom.SetIntAttr(self.Param, tmpValue)
            config.ApplyOptions()
        return scraft.CommandStateRepeat

#--------------------------------
# Текстовая область заданного размера
# с автоматическим переносом строк 
#--------------------------------

class TextArea:
    def __init__(self, font, layer, x0=0, y0=0, width=1, height=1):
        self.TextSprite = MakeSimpleSprite(font, layer, x0, y0, scraft.HotspotLeftTop)
        self.Width, self.Height = width, height
        
    def SetText(self, str):
        tmpStr = MakeSprite(self.TextSprite.klass, Layer_Tmp)
        self.TextSprite.text = ""
        tmpStrings = string.split(str)
        for tmp in tmpStrings:
            tmpStr.text = string.lstrip(self.TextSprite.text+" "+tmp)
            if tmpStr.width <= self.Width:
                self.TextSprite.text = string.lstrip(self.TextSprite.text+" "+tmp)
            else:
                self.TextSprite.text = string.lstrip(self.TextSprite.text+"\n"+tmp)
        
    def SetParams(self, params = {}):
        if params.has_key("klass"):
            self.TextSprite.ChangeKlassTo(params["klass"])
        if params.has_key("x") and params.has_key("y"):
            self.TextSprite.x, self.TextSprite.y = params["x"], params["y"]
        if params.has_key("xy"):
            self.TextSprite.x, self.TextSprite.y = params["xy"]
        if params.has_key("width") and params.has_key("height"):
            self.Width, self.Height = params["width"], params["height"]
        if params.has_key("area"):
            self.Width, self.Height = params["area"]
        if params.has_key("hotspot"):
            self.TextSprite.hotspot = params["hotspot"]
        if params.has_key("cfilt-color"):
            self.TextSprite.cfilt.color = params["cfilt-color"]

    def Show(self, flag):
        self.TextSprite.visible = flag
        
#--------------------------------
# Прочие функции
#--------------------------------
def MakeButton(whose, cmd, newKlass, newLayer, newX, newY,
               frUp, frRl, frDn, frIn = -1, frSl = -1):
    tmpButton = oE.NewSprite_(newKlass, newLayer)
    tmpButton.x = newX
    tmpButton.y = newY
    tmpButton.cookie = cmd
    tmpButton.SetItem(Frame_Up, frUp)
    tmpButton.SetItem(Frame_Rl, frRl)
    tmpButton.SetItem(Frame_Dn, frDn)
    tmpButton.SetItem(Frame_In, frIn)
    tmpButton.SetItem(Frame_Sl, frSl)
    tmpButton.visible = True
    tmpButton.dispatcher = whose
    tmpButton.frno = frUp
    return tmpButton

def MakeTextSprite(newKlass, newLayer, newX, newY,
                   newHotspot = scraft.HotspotCenter, newText = ""):
    tmpSpr = oE.NewSprite_(newKlass, newLayer)
    tmpSpr.x = newX
    tmpSpr.y = newY
    tmpSpr.hotspot = newHotspot
    tmpSpr.text = newText
    return tmpSpr
    
def MakeSimpleSprite(newKlass, newLayer, newX = FieldMaxX/2, newY = FieldMaxY/2,
                     newHotspot = scraft.HotspotCenter, newFrno = 0):
    tmpSpr = oE.NewSprite_(newKlass, newLayer)
    tmpSpr.x = newX
    tmpSpr.y = newY
    tmpSpr.hotspot = newHotspot
    tmpSpr.frno = newFrno
    return tmpSpr
    
def MakeDummySprite(whose, cmd, newX, newY, newXSize, newYSize, newLayer,
                    newSubLayer = 0, newHotspot = scraft.HotspotCenter, newName = ""):
    tmpSpr = oE.NewDummy(newName)
    tmpSpr.layer = newLayer
    tmpSpr.sublayer = newSubLayer
    tmpSpr.hotspot = newHotspot
    tmpSpr.x, tmpSpr.y = newX, newY
    tmpSpr.xSize, tmpSpr.ySize = newXSize, newYSize
    tmpSpr.cookie = cmd
    tmpSpr.dispatcher = whose
    return tmpSpr
    
# Создает спрайт по словарю параметров
# klass и layer - обязательные параметры
def MakeSprite(newKlass, newLayer, param = {}):
    tmpSpr = oE.NewSprite_(newKlass, newLayer)
    if param.has_key("x") and param.has_key("y"):
        tmpSpr.x = param["x"]
        tmpSpr.y = param["y"]
    elif param.has_key("xy"):
        tmpSpr.x, tmpSpr.y = param["xy"]
    if param.has_key("text"):
        tmpSpr.text = param["text"]
    if param.has_key("frno"):
        tmpSpr.frno = param["frno"]
    if param.has_key("hotspot"):
        tmpSpr.hotspot = param["hotspot"]
    if param.has_key("sublayer"):
        tmpSpr.sublayer = param["sublayer"]
    if param.has_key("cfilt-color"):
        tmpSpr.cfilt.color = param["cfilt-color"]
    if param.has_key("cookie"):
        tmpSpr.cookie = param["cookie"]
    if param.has_key("dispatcher"):
        tmpSpr.dispatcher = param["dispatcher"]
    if param.has_key("parent"):
        tmpSpr.parent = param["parent"]
    return tmpSpr
    

def ApplyTextLayout(sprite, layout):
    if layout.HasAttr("textFont"):
        sprite.ChangeKlassTo(layout.GetStrAttr("textFont"))
    if layout.HasAttr("textXY"):
        sprite.x, sprite.y = eval(layout.GetStrAttr("textXY"))
    if layout.HasAttr("textColor"):
        sprite.cfilt.color = eval(layout.GetStrAttr("textColor"))
    if layout.HasAttr("hotspot"):
        sprite.hotspot = eval(layout.GetStrAttr("hotspot"))
   

def Nearest(x, range):
    return min(max(x, range[0]), range[1])

