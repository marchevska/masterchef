#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Спецэффекты
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


#------------------------------------
# Спрайт двигается по заданному пути
#------------------------------------

class Popup(scraft.Dispatcher):
    def __init__(self, sprite,
                 motionfunc, transpfunc, scalefunc, maxTime = 10000):
        self.sprite = sprite
        self.MotionFunc = motionfunc
        self.TranspFunc = transpfunc
        self.ScaleFunc = scalefunc
        self.MaxTime = maxTime
        
        self.StartTime = globalvars.Timer.millis
        self.StartX = sprite.x
        self.StartY = sprite.y
        oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        deltaT = globalvars.Timer.millis - self.StartTime
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
    
#движение по ломаной
def BounceMotion(points):
    def f(x0, y0, t):
        eps = 0.001
        t *= 0.001
        if t <= points[0][0] + eps:
            tmpX = points[0][1]
            tmpY = points[0][2]
        elif t >= points[-1][0] + eps:
            tmpX = points[-1][1]
            tmpY = points[-1][2]
        else:
            i = len(filter(lambda x: x[0]<t, points))-1
            if t <= points[i][0] + eps:
                tmpX = points[i][1]
                tmpY = points[i][2]
            else:
                tmpX = points[i][1] + 1.0*(t - points[i][0])*(points[i+1][1] - points[i][1])/(points[i+1][0] - points[i][0])
                tmpY = points[i][2] + 1.0*(t - points[i][0])*(points[i+1][2] - points[i][2])/(points[i+1][0] - points[i][0])
        return (tmpX, tmpY)
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
        

#------------ 
# Спрайты движутся по заданному контуру
#------------ 
def DrawTrailedContour(params, contour):
    DefaultParams = { "klass": "star", "layer": 0, "no": 10, "incTrans": 5, "incScale": 3, "delay": 20 }
    prm = {}
    for tmp in DefaultParams.keys():
        if params.has_key(tmp):
            prm[tmp] = params[tmp]
        else:
            prm[tmp] = DefaultParams[tmp]
    tmpSprites = map(lambda x: MakeSprite(prm["klass"], prm["layer"],
                    { "x": contour[0][1], "y": contour[0][2], "hotspot": scraft.HotspotCenter,
                    "transparency": prm["incTrans"]*x,
                    "scale": 100 - prm["incScale"]*x }), xrange(prm["no"]))
    tmp = Popup(TrailProxy(tmpSprites, prm["delay"]), BounceMotion(contour), DefaultTransp(), DefaultScale(),
                (2*contour[-1][0] - contour[-2][0])*1000)

#------------ 
# Прокси: композитный спрайт
# Спрайты движутся за первым в виде шлейфа
# Задается задержка каждого спрайта относительно головы
# При создании получает список спрайтов
#------------ 
class TrailProxy(object):
    def __init__(self, sprites, delay):
        self.Sprites = sprites
        self.Delay = delay
        self.StartTime = globalvars.Timer.millis
        self.HistoryX = []
        self.HistoryY = []
        #количество видимых спрайтов шлейфа
        self.count = 0
        for i in range(len(self.Sprites)):
            self.Sprites[i].visible = False
            
    def SetX(self, value):
        self.count = min(int((globalvars.Timer.millis - self.StartTime)/self.Delay), len(self.Sprites))
        for i in range(self.count):
            self.Sprites[i].visible = True
        
        self.HistoryX.append((globalvars.Timer.millis, value))
        for i in range(self.count-1, 0, -1):
            self.Sprites[i].x = Interpolation(self.HistoryX, globalvars.Timer.millis - i*self.Delay)
            #self.Sprites[i].x = self.Sprites[i-1].x
        self.Sprites[0].x = value
        
    def GetX(self):
        return self.Sprites[0].x
        
    x = property(GetX, SetX)
        
    def SetY(self, value):
        self.HistoryY.append((globalvars.Timer.millis, value))
        for i in range(len(self.Sprites)-1, 0, -1):
            self.Sprites[i].y = Interpolation(self.HistoryY, globalvars.Timer.millis - i*self.Delay)
            #self.Sprites[i].y = self.Sprites[i-1].y
        self.Sprites[0].y = value
        
    def GetY(self):
        return self.Sprites[0].y
        
    y = property(GetY, SetY)
        
    def Dispose(self):
        for spr in self.Sprites:
            spr.Dispose()
        del self.Sprites
        

def Interpolation(points, t):
    eps = 1
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
    return tmp
