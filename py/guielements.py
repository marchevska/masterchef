#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
�������� ���: ������, ������� � �.�.
"""

import scraft
from scraft import engine as oE
from configconst import *
from constants import *
from guiconst import *
import config
import globalvars

#--------------------------------
# ������ � �������
# ������� �� dummy-4-hit-area,
# ������ � ���������� ������� (����������� - ��� ������)
#--------------------------------

class PushButton(scraft.Dispatcher):
    def __init__(self, name, whose, cmd, when, newKlass, frames, 
                 newLayer, newX, newY, newXSize, newYSize,
                 text = "", klasses = [], textDX = 0, textDY = 0):
        
        #dummy ������������ ��� hit area
        self.Dummy = MakeDummySprite(self, cmd, newX, newY, newXSize, newYSize, newLayer)
        
        #������ ������
        self.ButtonSprite = oE.NewSprite_(newKlass, newLayer)
        self.ButtonSprite.sublayer = 1
        self.ButtonSprite.hotspot = scraft.HotspotCenter
        self.ButtonSprite.x, self.ButtonSprite.y = newX, newY
        #����� �� ������
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
        self.SetState(ButtonState_Up)
        
    def MoveTo(self, newX, newY):
        self.Dummy.x, self.Dummy.y = newX, newY
        self.ButtonSprite.x, self.ButtonSprite.y = newX, newY
        if self.HasText:
            self.TextSprite.x, self.TextSprite.y = newX, newY
        
    def SetButtonKlass(self, newKlass):
        self.ButtonSprite.ChangeKlassTo(newKlass)
        self.ButtonSprite.hotspot = scraft.HotspotCenter
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.ButtonSprite.visible = flag
        if self.HasText:
            self.TextSprite.visible = flag
        
    def SetText(self, newText):
        self.TextSprite.text = unicode(newText)
        
    def SetState(self, state):
        self.State = state
        self.ButtonSprite.frno = self.ButtonFrames[state]
        if self.HasText:
            self.TextSprite.ChangeKlassTo(self.TextKlasses[state])
            self.TextSprite.hotspot = scraft.HotspotCenter
        globalvars.BlackBoard.Update(BBTag_Cursor, {"button": state})
        
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
                    oE.PlaySound(u"click", Channel_Default)
                    self.Whose.SendCommand(sprite.cookie)
            globalvars.LastCookie = Cmd_None
        
    #def _OnMouseClick(self, sprite, x, y, button):
    #    if globalvars.StateStack[-1] == self.ActiveWhen and button == 1:
    #        if self.State in (ButtonState_Up, ButtonState_Roll, ButtonState_Down):
    #            oE.PlaySound(u"click", Channel_Default)
    #            self.Whose.SendCommand(sprite.cookie)
        
    def Kill(self):
        self.Dummy.Dispose()
        self.ButtonSprite.Dispose()
        if self.HasText:
            self.TextSprite.Dispose()
    
#--------------------------------
# ���������-�������
# ������� �� dummy-4-hit-area,
# �������� ������� � �������
#--------------------------------

class Slider(scraft.Dispatcher):
    def __init__(self, name, whom, paramName, when, newKlass, frames, 
                 newLayer, newX, newY, newXSize, newYSize,
                 newXRange, newYRange, bgKlass = ""):
        #dummy ������������ ��� hit area
        self.Dummy = MakeDummySprite(self, Cmd_SliderDummy, newX, newY,
                                     newXSize, newYSize, newLayer, 2)
        
        #������� ������
        if bgKlass != "":
            self.BgSprite = oE.NewSprite_(bgKlass, newLayer)
            self.BgSprite.sublayer = 1
            self.BgSprite.hotspot = scraft.HotspotCenter
            self.BgSprite.x, self.BgSprite.y = newX, newY
            self.HasBg = True
        else:
            self.HasBg = False
        
        #������ �������
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
        globalvars.BlackBoard.Update(BBTag_Cursor, {"button": state})
        
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
    tmpSpr.text = unicode(newText)
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
                    newSubLayer = 0, newHotspot = scraft.HotspotCenter, newName = u""):
    tmpSpr = oE.NewDummy(newName)
    tmpSpr.layer = newLayer
    tmpSpr.sublayer = newSubLayer
    tmpSpr.hotspot = newHotspot
    tmpSpr.x, tmpSpr.y = newX, newY
    tmpSpr.xSize, tmpSpr.ySize = newXSize, newYSize
    tmpSpr.cookie = cmd
    tmpSpr.dispatcher = whose
    return tmpSpr
    
# ������� ������ �� ������� ����������
# klass � layer - ������������ ���������
def MakeSprite(newKlass, newLayer, param = {}):
    tmpSpr = oE.NewSprite_(newKlass, newLayer)
    if param.has_key("x") and param.has_key("y"):
        tmpSpr.x = param["x"]
        tmpSpr.y = param["y"]
    elif param.has_key("xy"):
        tmpSpr.x, tmpSpr.y = param["xy"]
    if param.has_key("text"):
        tmpSpr.text = unicode(param["text"])
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
    
def Nearest(x, range):
    return min(max(x, range[0]), range[1])

