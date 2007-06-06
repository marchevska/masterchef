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
from random import randint
from guiconst import *
from configconst import *
from guielements import MakeSimpleSprite, MakeTextSprite
import globalvars

#----------------------------------
# Курсор с несколькими состояниями
#----------------------------------

class Cursor(scraft.Dispatcher):
    def __init__(self):
        self.sprite = MakeSimpleSprite(u"cursor", Layer_Cursor)
        self.CursorState = CursorState_Default
        self.QueNo = oE.executor.Schedule(self)
        
    def SetState(self, state):
        if state == CursorState_Default:
            self.sprite.ChangeKlassTo(u"cursor")
        elif state == CursorState_Go:
            self.sprite.ChangeKlassTo(u"cursor-go")
        elif state == CursorState_NoWay:
            self.sprite.ChangeKlassTo(u"cursor-noway")
        elif state == CursorState_None:
            self.sprite.ChangeKlassTo(u"cursor-none")
        if state == CursorState_Go:
            self.sprite.AnimateLoop(2)
        else:
            self.sprite.StopAnimation()
        self.CursorState = state
        
    def _OnExecute(self, que):    
        self.sprite.x = oE.mouseX
        self.sprite.y = oE.mouseY
        
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
                oE.PlaySound(tmp["sound"], tmp["channel"])
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
                oE.PlaySound(tmp["sound"], tmp["channel"])
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
            self.sprite.text = unicode(str(self.ValueShown))
        return scraft.CommandStateRepeat
            
    def Show(self, flag):
        self.sprite.visible = flag
            
    def SetValueStrict(self, newvalue):
        self.Value = self.ValueShown = newvalue
        self.sprite.text = unicode(str(self.ValueShown))
        
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
    def __init__(self, sprite, motionfunc, transpfunc):
        self.sprite = sprite
            
        if motionfunc == "Bubble":
            self.MotionFunc = BubbleMotion
        else:            
            self.MotionFunc = DefaultMotion
        
        if transpfunc == "FadeOut":
            self.TranspFunc = FadeAwayTransp
        else:            
            self.TranspFunc = DefaultTransp
        
        self.StartTime = globalvars.Timer.millis
        self.StartX = sprite.x
        self.StartY = sprite.y
        oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        deltaT = oE.millis - self.StartTime
        (self.sprite.x, self.sprite.y) = \
            self.MotionFunc(self.StartX, self.StartY, deltaT)
        self.sprite.transparency = self.TranspFunc(deltaT)

        if FieldMinX <= self.sprite.x <= FieldMaxX \
            and FieldMinY <= self.sprite.y <= FieldMaxY \
            and self.sprite.transparency < 100:
            return scraft.CommandStateRepeat
        else:
            self.sprite.Dispose()
            return scraft.CommandStateEnd
        
def DefaultMotion(x0, y0, t):
    x = x0
    y = y0 - 0.1*t
    return (x,y)
    
def BubbleMotion(x0, y0, t):
    x = x0
    y = y0 - 0.1*t + 0.000016*t*t
    
    return (x,y)

def FadeAwayTransp(t):
    transp = min(100, max(t*0.05-25, 0))    
    return transp

def DefaultTransp(t):
    return 0

#--------------------------------
# Управляет проигрыванием музыки
#--------------------------------

class Musician(scraft.Dispatcher):
    def __init__(self):
        self.State = MusicState_Menu
        self._PlayNewMelody()
        
    def SetState(self, state):
        if state != self.State:
            self.State = state
            oE.StopSound(Channel_Music)
            self._PlayNewMelody()
            
    def _PlayNewMelody(self):
        if self.State == MusicState_Menu:
            tmpMelodies = list(Tracks_Menu)
        else:
            tmpMelodies = list(Tracks_Game)
        tmpNewMelody = tmpMelodies[randint(0, len(tmpMelodies)-1)]
        oE.PlaySound(tmpNewMelody, Channel_Music, self)
        
    def _OnStopSound(self, sound, channel, cookie, x):
        if not x:
            self._PlayNewMelody()
        

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

