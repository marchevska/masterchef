#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Вспомогательные классы
"""

import sys
import scraft
from scraft import engine as oE
import math
from random import randint, choice
from guiconst import *
from configconst import *
from constants import *
from guielements import MakeSimpleSprite, MakeTextSprite, MakeSprite
import globalvars

#----------------------------------
# Курсор с несколькими состояниями
#----------------------------------

class Cursor(scraft.Dispatcher):
    def __init__(self):
        self.Dummy = MakeSprite("$spritecraft$dummy$", Layer_Cursor)
        self.FingerSprite = MakeSprite("$spritecraft$dummy$", Layer_CursorUpper,
                { "x": 0, "y": 0, "parent": self.Dummy })
        self.UpperSprite = MakeSprite("$spritecraft$dummy$", Layer_CursorUpper,
                { "x": 35, "y": 10, "parent": self.Dummy })
        self.DownSprite = MakeSprite("$spritecraft$dummy$", Layer_CursorDown,
                { "x": 35, "y": 10, "parent": self.Dummy })
        self.CursorState = CursorState_Default
        self.QueNo = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):    
        self.Dummy.x = oE.mouseX
        self.Dummy.y = oE.mouseY
        
        if globalvars.BlackBoard.Inspect(BBTag_Cursor)["button"] == ButtonState_Up:
            self.FingerSprite.ChangeKlassTo("cursor.hand.up")
        elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["button"] == ButtonState_Roll:
            self.FingerSprite.ChangeKlassTo("cursor.hand.roll")
        elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["button"] == ButtonState_Down:
            self.FingerSprite.ChangeKlassTo("cursor.hand.down")
        #if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Default:
        #    if globalvars.BlackBoard.Inspect(BBTag_Cursor)["button"] == ButtonState_Up:
        #        self.UpperSprite.ChangeKlassTo("cursor.hand.up")
        #    elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["button"] == ButtonState_Roll:
        #        self.UpperSprite.ChangeKlassTo("cursor.hand.roll")
        #    elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["button"] == ButtonState_Down:
        #        self.UpperSprite.ChangeKlassTo("cursor.hand.down")
        #    self.DownSprite.ChangeKlassTo("$spritecraft$dummy$")
        if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Default:
            self.UpperSprite.ChangeKlassTo("$spritecraft$dummy$")
            self.DownSprite.ChangeKlassTo("$spritecraft$dummy$")
        elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
            if globalvars.BlackBoard.Inspect(BBTag_Cursor)["red"]:
                self.UpperSprite.ChangeKlassTo("cursor.box.red.up")
                self.DownSprite.ChangeKlassTo("cursor.box.red")
            else:
                self.UpperSprite.ChangeKlassTo("$spritecraft$dummy$")
                self.DownSprite.ChangeKlassTo("cursor.box.token")
        elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool:
            self.UpperSprite.ChangeKlassTo("$spritecraft$dummy$")
            #self.DownSprite.ChangeKlassTo("cursor.box.tool")
            self.DownSprite.ChangeKlassTo("$spritecraft$dummy$")
        
        return scraft.CommandStateRepeat
    
#--------------------------------------
# Внутриигровой таймер,
# может быть остановлен и снят с паузы
#--------------------------------------

class Timer(scraft.Dispatcher):
    def __init__(self):
        self.millis = 0
        self.StartTime = oE.millis
        self.Paused = False
        self.QueNo = oE.executor.Schedule(self)
        
    def Reset(self):
        self.millis = 0
        
    def Pause(self, flag):
        self.Paused = flag
        if flag:
            self.PausedAt = oE.millis
        else:
            tmpTime = oE.millis
            self.StartTime += (tmpTime - self.PausedAt)
        
    def _OnExecute(self, que):
        if not self.Paused:
            self.millis = oE.millis - self.StartTime
        return scraft.CommandStateRepeat

#---------------------------------
# Анимация спрайта с перемещением
#---------------------------------

class Anima(scraft.Dispatcher):
    """
    Анимация спрайта с перемещением, на основе списка:
    координаты точек, угол поворота, номер кадра спрайта,
    длительность задержки; также проигрывается звук
    Очередь отслеживается породившим классом
    """
    def __init__(self, sprite, animation):
        self.sprite = sprite
        self.animation = animation
        self.Stopped = False
        
    def _OnExecute(self, que):
        if len(self.animation) > 0:
            tmp = self.animation.pop(0)
            if tmp.has_key("x"):
                self.sprite.x = tmp["x"]
            if tmp.has_key("y"):
                self.sprite.y = tmp["y"]
            if tmp.has_key("degree"):
                self.sprite.degree = tmp["degree"]
            if tmp.has_key("sublayer"):
                self.sprite.sublayer = tmp["sublayer"]
            if tmp.has_key("sound") and tmp.has_key("channel"):
                globalvars.Musician.PlaySound(tmp["sound"], tmp["channel"])
            if tmp.has_key("frno"):
                self.sprite.frno = tmp["frno"]
            if self.Stopped and tmp.has_key("cue"):
                return scraft.CommandStateEnd
            else:
                return tmp["delay"]
        else:
            return scraft.CommandStateEnd
        
    def StopMotion(self):
        self.Stopped = True
    
#----------------------------------
# Управление анимациеями персонажа
#----------------------------------

class Animator(scraft.Dispatcher):
    """
    Автоматическое переключение анимаций персонажа
    на основе списка анимаций и состояний,
    для одного состояния выбор анимации
    на основе частотного списка
    После инициализации обязателен вызов SetState()
    """
    def __init__(self, sprite, states, animations):
        self.Sprite = sprite
        self.States = states
        self.Animations = animations
        self.QueNo = oE.executor.Schedule(self)
        
    def SetState(self, state):
        self.State = state
        self.NextFrameTime = 0
        self._ResetSequence()
        
    def _ResetSequence(self):
        #временный указатель на нужную анимацию
        tmpAnimation = self.Animations[RandomKeyByRates(self.States[self.State])]
        #скопируем анимацию в собственный список
        #анимация - это списко из словарей
        self.CurrentAnimation = []
        for tmpFrame in tmpAnimation:
            self.CurrentAnimation.append(dict(tmpFrame))
        
    def _OnExecute(self, que):
        if self.NextFrameTime <= 0:
            if len(self.CurrentAnimation) <= 0:
                self._ResetSequence()
            tmp = self.CurrentAnimation.pop(0)
            if tmp.has_key("x"):
                self.sprite.x = tmp["x"]
            if tmp.has_key("y"):
                self.sprite.y = tmp["y"]
            if tmp.has_key("degree"):
                self.sprite.degree = tmp["degree"]
            if tmp.has_key("sublayer"):
                self.sprite.sublayer = tmp["sublayer"]
            if tmp.has_key("sound") and tmp.has_key("channel"):
                globalvars.Musician.PlaySound(tmp["sound"], tmp["channel"])
            self.Sprite.frno = tmp["frno"]
            self.NextFrameTime += tmp["delay"]
        self.NextFrameTime -= que.delta
        return scraft.CommandStateRepeat

#-----------------------------------------
# Простой индикатор состояния типа bar
#-----------------------------------------

class BarIndicator:
    def __init__(self, newX, newY, width, height, topKlass, bgKlass, newLayer,
                 lineKlass = "$spritecraft$dummy$", isVertical = False, isReverse = False):
        self.sprite = MakeSimpleSprite(topKlass, newLayer, newX, newY, scraft.HotspotLeftTop)
        self.bgSprite = MakeSimpleSprite(bgKlass, newLayer, newX, newY, scraft.HotspotLeftTop)
        self.lineSprite = MakeSimpleSprite(lineKlass, newLayer, 0, 0, scraft.HotspotCenter)
        self.lineSprite.parent = self.bgSprite
        #self.sprite.sublayer = 1
        #self.bgSprite.sublayer = 2
        #self.lineSprite.sublayer = 0
        self.Width, self.Height = width, height
        self.IsVertical = isVertical
        self.IsReverse = isReverse #справа налево или сверху вниз
        self.Show(True)
        self.SetValue(0)
        
    def SetKlasses(self, newTopKlass, newBgKlass):
        self.sprite.ChangeKlassTo(newTopKlass)
        self.bgSprite.ChangeKlassTo(newBgKlass)
        
    def Show(self, flag):
        self.sprite.visible = flag
        self.bgSprite.visible = flag
        self.lineSprite.visible = flag
        self.sprite.sublayer = 1
        self.bgSprite.sublayer = 2
        self.lineSprite.sublayer = 0
        
    def SetValue(self, newValue):
        if newValue < 0:
            newValue = 0
        elif newValue > 1:
            newValue = 1
        if self.IsVertical:
            height0 = int(newValue*self.Height)
            width0 = self.Width
        else:
            width0 = int(newValue*self.Width)
            height0 = self.Height
        if self.IsReverse:
            tmpCoords = [(self.Width-width0, self.Height-height0), (self.Width, self.Height-height0),
                (self.Width, self.Height), (self.Width-width0, self.Height)]
        else:
            tmpCoords = [(0, 0), (width0, 0), (width0, height0), (0, height0)]
        
        self.sprite.style = scraft.StyleShape
        self.sprite.primitive.cw = True
        self.sprite.primitive.count = 4
        for i in range(4):
            self.sprite.primitive.SetXY(i, tmpCoords[i][0], tmpCoords[i][1])
        
        if self.IsVertical:
            self.lineSprite.x = self.lineSprite.width/2
            height1 = int(newValue*(self.Height+self.lineSprite.height))
            if self.IsReverse:
                self.lineSprite.y = self.Height-height1 + self.lineSprite.height/2
            else:
                self.lineSprite.y = height1 - self.lineSprite.height/2
        else:
            self.lineSprite.y = self.lineSprite.height/2
            width1 = int(newValue*(self.Width+self.lineSprite.width))
            if self.IsReverse:
                self.lineSprite.x = self.Width-width1 + self.lineSprite.width/2
            else:
                self.lineSprite.x = width1 - self.lineSprite.width/2
            
    def Kill(self):
        self.sprite.Dispose()
        self.bgSprite.Dispose()
        self.lineSprite.Dispose()

#-----------------------------------------
# Числовой индикатор с плавным изменением
#-----------------------------------------

class NumIndicator(scraft.Dispatcher):
    def __init__(self, newKlass, newLayer, newX, newY, newHotspot, value, speed):
        self.Speed = speed
        self.sprite = MakeTextSprite(newKlass, newLayer, newX, newY, newHotspot)
        self.SetValueStrict(value)
        self.QueNo = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        if self.Value != self.ValueShown:
            tmpDelta = self.Value - self.ValueShown
            tmpAbsDelta = int(min(1.0*que.delta*self.Speed/1000, abs(tmpDelta)))
            self.ValueShown += tmpAbsDelta*tmpDelta/abs(tmpDelta)
            self.sprite.text = str(self.ValueShown)
        return scraft.CommandStateRepeat
            
    def Show(self, flag):
        self.sprite.visible = flag
            
    def SetValueStrict(self, newvalue):
        self.Value = self.ValueShown = newvalue
        self.sprite.text = str(self.ValueShown)
        
    def SetValue(self, newvalue):
        self.Value = newvalue

#-------------------------------------------------------
# Круговой индикатор с пошаговым или плавным изменением
# step=0 - плавное, speed=0 - пошаговое
#-------------------------------------------------------

class CircularIndicator(scraft.Dispatcher):
    def __init__(self, newKlass, bgKlass, newLayer, newSublayer,
                 newX, newY, value, speed, step, halfsize):
        self.ClockChain = [(0,0), (0,1), (1,1), (1,-1), (-1,-1), (-1,1), (0,1)]
        self.Speed = speed
        self.Step = step
        self.HalfSize = halfsize
        self.sprite = MakeSimpleSprite(newKlass, newLayer, newX, newY)
        self.sprite.style = scraft.StyleShape
        self.sprite.primitive.cw = True
        self.sprite.sublayer = newSublayer
        self.bgSprite = MakeSimpleSprite(bgKlass, newLayer, newX, newY)
        self.bgSprite.sublayer = newSublayer+1
        self.SetValueStrict(value)
        self.Freeze(True)
        self.QueNo = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        if not self.Frozen:
            if self.Value != self.ValueShown:
                tmpDelta = self.Value - self.ValueShown
                if self.Step != 0:
                    if abs(tmpDelta) >= self.Step or self.ValueShown >= 1.0: 
                        self.ValueShown += self.Step*tmpDelta/abs(tmpDelta)
                        self._Draw()
                else:
                    tmpAbsDelta = int(min(1.0*que.delta*self.Speed/1000, abs(tmpDelta)))
                    self.ValueShown += tmpAbsDelta*tmpDelta/abs(tmpDelta)
                    self._Draw()
                
        return scraft.CommandStateRepeat
            
    def _Draw(self):
        if self.ValueShown >= 1.0:
            self.sprite.style = scraft.StylePicture
        else:
            self.sprite.style = scraft.StyleShape
            self.sprite.primitive.cw = True
            tmpPoints = int((self.ValueShown + 0.875)/0.25)
            if tmpPoints != self.sprite.primitive.count:
                self.sprite.primitive.count = tmpPoints
                for i in range(tmpPoints-1):
                    self.sprite.primitive.SetXY(i, self.HalfSize*(1 + self.ClockChain[i][0]),
                                                self.HalfSize*(1 - self.ClockChain[i][1]))
            tmpAngle = self.ValueShown*math.pi*2
            if 0.125 < self.ValueShown <= 0.375:
                tmpNewX, tmpNewY = 1, 1/math.tan(tmpAngle)
            elif 0.375 < self.ValueShown <= 0.625:
                tmpNewX, tmpNewY = -math.tan(tmpAngle), -1
            elif 0.625 < self.ValueShown <= 0.875:
                tmpNewX, tmpNewY = -1, -1/math.tan(tmpAngle)
            else:
                tmpNewX, tmpNewY = math.tan(tmpAngle), 1
            self.sprite.primitive.SetXY(tmpPoints-1, self.HalfSize*(1 + tmpNewX),
                                        self.HalfSize*(1 - tmpNewY))
        
    def Show(self, flag):
        self.sprite.visible = flag
        self.bgSprite.visible = flag
            
    def SetValueStrict(self, newvalue):
        self.Value = self.ValueShown = newvalue
        self._Draw()
        
    def SetValue(self, newvalue):
        self.Value = newvalue
        
    def Freeze(self, flag):
        self.Frozen = flag
        
#---------------------------------
# Индикатор времени из 3-х частей
#---------------------------------

class TimeBar(scraft.Dispatcher):
    def __init__(self, newKlass, newLayer, newX, newY,
                 width1, width2, width3, height, value, speed):
        self.Frozen = False
        self.Value = value
        self.ValueShown = 0
        self.Speed = speed
        self.Sprites = {}
        self.crdX, self.crdY = newX, newY
        self.Width1 = width1
        self.Width2 = width2
        self.Width3 = width3
        self.Height = height
        self.TotalLength = width1 + width2 + width3
        
        self.sprite = MakeSimpleSprite(newKlass, newLayer, newX, newY, scraft.HotspotLeftTop)
        tmpSpr.style = scraft.StyleShape
        tmpSpr.primitive.cw = True
        tmpSpr.primitive.count = 4
        self.Sprites["Left"] = tmpSpr
        
        self.sprite = MakeSimpleSprite(newKlass, newLayer, newX, newY, scraft.HotspotLeftTop)
        tmpSpr.style = scraft.StyleShape
        tmpSpr.primitive.cw = True
        tmpSpr.primitive.count = 4
        self.Sprites["Middle"] = tmpSpr
        
        self.sprite = MakeSimpleSprite(newKlass, newLayer, newX, newY, scraft.HotspotLeftTop)
        tmpSpr.style = scraft.StyleShape
        tmpSpr.primitive.cw = True
        tmpSpr.primitive.count = 4
        self.Sprites["Right"] = tmpSpr
        
        self._Draw()
        self.Freeze(True)
        oE.executor.Schedule(self)
        
    def SetValueStrict(self, newvalue):
        self.Value = self.ValueShown = newvalue
        self._Draw()
        
    def SetValue(self, newvalue):
        self.Value = newvalue
        
    def _Draw(self):
        tmpLength = int(self.ValueShown*self.TotalLength)
        if tmpLength > self.Width1 + self.Width3:
            tmpWidth1 = self.Width1
            tmpWidth2 = tmpLength - (self.Width1 + self.Width3)
            tmpWidth3 = self.Width3
        else:
            tmpWidth1 = tmpLength/2
            tmpWidth2 = 0
            tmpWidth3 = tmpLength - tmpWidth1
        tmpCoords1 = [(0, 0), (tmpWidth1, 0),
                        (tmpWidth1, self.Height), (0, self.Height)]
        tmpCoords2 = [(tmpWidth1, 0), (tmpWidth1 + tmpWidth2, 0),
                        (tmpWidth1 + tmpWidth2, self.Height), (tmpWidth1, self.Height)]
        tmpCoords3 = [(self.TotalLength - tmpWidth3, 0), (self.TotalLength, 0),
                        (self.TotalLength, self.Height), (self.TotalLength - tmpWidth3, self.Height)]
        for i in range(4):
            self.Sprites["Left"].primitive.SetXY(i, tmpCoords1[i][0], tmpCoords1[i][1])
            self.Sprites["Middle"].primitive.SetXY(i, tmpCoords2[i][0], tmpCoords2[i][1])
            self.Sprites["Right"].primitive.SetXY(i, tmpCoords3[i][0], tmpCoords3[i][1])
        self.Sprites["Right"].x = self.crdX + tmpLength - self.TotalLength
        
    def _OnExecute(self, que):
        if not self.Frozen:
            if self.Value != self.ValueShown:
                tmpDelta = self.Value - self.ValueShown
                tmpAbsDelta = min(1.0*que.delta*self.Speed/1000, abs(tmpDelta))
                self.ValueShown += tmpAbsDelta*tmpDelta/abs(tmpDelta)
                self._Draw()
        return scraft.CommandStateRepeat
        
    def Show(self, flag):
        for spr in self.Sprites.values():
            spr.visible = flag
        
    def Freeze(self, flag):
        self.Frozen = flag
        
#------------------------------------
# Спрайт всплывает по заданному пути
#------------------------------------

class Popup(scraft.Dispatcher):
    def __init__(self, sprite,
                 motionfunc, transpfunc, scalefunc, maxTime = 10000):
        self.sprite = sprite
        self.MotionFunc = motionfunc
        self.TranspFunc = transpfunc
        self.ScaleFunc = scalefunc
        self.MaxTime = maxTime
        
        #if motionfunc == "Bubble":
        #    self.MotionFunc = BubbleMotion
        #else:            
        #    self.MotionFunc = DefaultMotion
        #
        #if transpfunc == "FadeOut":
        #    self.TranspFunc = FadeAwayTransp
        #else:            
        #    #self.TranspFunc = DefaultTransp
        #    self.TranspFunc = BlinkTransp(400, 0.4, -50)
        
        self.StartTime = globalvars.Timer.millis
        self.StartX = sprite.x
        self.StartY = sprite.y
        oE.executor.Schedule(self)
        
        
    def _OnExecute(self, que):
        deltaT = oE.millis - self.StartTime
        (self.sprite.x, self.sprite.y) = \
            self.MotionFunc(self.StartX, self.StartY, deltaT)
        self.sprite.transparency = self.TranspFunc(deltaT)
        self.sprite.xScale, self.sprite.yScale = self.ScaleFunc(deltaT)
        
        if FieldMinX <= self.sprite.x <= FieldMaxX \
            and FieldMinY <= self.sprite.y <= FieldMaxY \
            and self.sprite.transparency < 100 and deltaT < self.MaxTime:
            return scraft.CommandStateRepeat
        else:
            self.sprite.Dispose()
            return scraft.CommandStateEnd
        
#------------------------------------
# motion functions
#------------------------------------
def DefaultMotion():
    def f(x0, y0, t):
        return (x0, y0 - 0.1*t)
    return f
    
def BubbleMotion(a0, a1):
    def f(x0, y0, t):    
        return (x0, y0 + a1*(0.001*t) + a0*(0.001*t)**2)
    return f

def InPlaceMotion():
    def f(x0, y0, t):
        return (x0, y0)
    return f
    
#------------------------------------
# transparency functions
#------------------------------------
def FadeAwayTransp(a0, a1):
    def f(t):
        return min(100, max((0.001*t)*a0+a1, 0))    
    return f

def DefaultTransp():
    def f(t):
        return 0
    return f

def BlinkTransp(a, t0, b):
    def f(t):
        return max(a*(0.001*t-t0)**2+b, 0)
    return f

#------------------------------------
# scale functions
#------------------------------------
def DefaultScale():
    def f(t):
        return (100, 100)
    return f

def BlinkScale(a, t0, b, c=100):
    def f(t):
        tmp = a*(0.001*t-t0)**2+b
        return (max(min(tmp,c),0), max(min(tmp,c),0))
    return f

def BounceScale(points):
    def f(t):
        eps = 0.001
        t *= 0.001
        if t <= points[0][0] + eps:
            tmp = points[0][1]
        elif t >= points[-1][0] + eps:
            tmp = points[-1][1]
        else:
            i = len(filter(lambda x: x[0]<t, points))-1
            if t <= points[i][0] + eps:
                tmp = points[i][1]
            else:
                tmp = points[i][1] + 1.0*(t - points[i][0])*(points[i+1][1] - points[i][1])/(points[i+1][0] - points[i][0])
        return (tmp, tmp)
    return f


def PopupText(text, font, x, y,
            motionfunc = DefaultMotion(), transpfunc = DefaultTransp(), scalefunc = DefaultScale(),
            maxTime = 10000):
    spr = MakeTextSprite(font, Layer_Popups, x, y, scraft.HotspotCenter, text)
    tmp = Popup(spr, motionfunc, transpfunc, scalefunc, maxTime)
        

#--------------------------------
# Управляет проигрыванием музыки
#--------------------------------

class Musician(scraft.Dispatcher):
    def __init__(self):
        self.State = MusicState_Menu
        self._PlayNewMelody()
        self.NextStates = []
        self.QueNo = oE.executor.Schedule(self)
        
    def SetState(self, state):
        self.NextStates.append(state)
            
    def _PlayNewMelody(self):
        tmpNewMelody = choice(MusicTracks[self.State])
        oE.PlaySound(tmpNewMelody, Channel_Music, self)
        
    def _OnStopSound(self, sound, channel, cookie, x):
        if not x:
            self._PlayNewMelody()
        
    def _OnExecute(self, que):
        if self.NextStates != []:
            if self.NextStates[-1] != self.State:
                self.State = self.NextStates[-1]
                oE.StopSound(Channel_Music)
                self._PlayNewMelody()
            self.NextStates = []
        return scraft.CommandStateRepeat
        
    def PlaySound(self, sound, channel = Channel_Default):
        oE.PlaySound(sound, channel)

#-----------------------------------
# Возвращается произвольный ключ
# на основе списка (словаря) частот
#-----------------------------------

def RandomKeyByRates(dict):
    tmpKeys = dict.keys()
    tmpNoKeys = len(tmpKeys)
    tmpValues = map(lambda x: dict[x], tmpKeys)
    tmpValueSums = map(lambda x: reduce(lambda a,b: a+b, tmpValues[0:x+1],0), range(tmpNoKeys))
    tmpResultValue = randint(1, tmpValueSums[-1])
    tmpTargetKeyNo = (filter(lambda x: tmpValueSums[x] >= tmpResultValue, range(tmpNoKeys)))[0]
    return tmpKeys[tmpTargetKeyNo]    

