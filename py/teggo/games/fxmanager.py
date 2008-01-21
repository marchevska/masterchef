#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Набор классов для управления спецэффектами
"""

import sys, traceback
import scraft
from scraft import engine as oE
import math, string
from random import randint, choice

import spriteworks

def CreateEffect(host, name, crd):
    tmpNode = oE.ParseDEF("def/effects.def").GetTag("Effects").GetSubtag(name)
    if string.lower(tmpNode.GetName()) == "particles":
        return ParticleEffect(host, tmpNode, crd)

class Effect:
    def __init__(self, node, crd):
        pass
        
    def Activate(self, flag):
        pass
        
    def Show(self, flag):
        pass
        
    def Dispose(self):
        pass

class ParticleEffect(Effect, scraft.Dispatcher):
    def __init__(self, host, node, crd):
        try:
            self.host = host
            self.p = oE.NewParticles_(node.GetStrAttr("klass"), node.GetIntAttr("layer"))
            self.p.sublayer = node.GetIntAttr("sublayer")
            self.p.cycled = node.GetBoolAttr("cycled")
            self.p.lifeTime = node.GetIntAttr("lifetime")
            self.p.SetEmissionQuantity(node.GetIntAttr("quant"))
            self.p.SetEmissionPeriod(node.GetIntAttr("period"))
            self.p.count = node.GetIntAttr("count")
            #coordinates
            try:
                nodeCrd = eval(node.GetStrAttr("source"))
            except:
                nodeCrd = (0,0)
            self.p.x, self.p.y = crd[0]+nodeCrd[0], crd[1]+nodeCrd[1]
            #other parameters
            paramCodes = { "angle": 1, "transparency": 2, "frno": 3, "speed": 4, "direction": 5,
                          "area": 6, "scale": 7, "angleinc": 8, "transparencyinc": 9, "scaleinc": 10 }
            for prm in paramCodes.keys():
                if node.HasAttr(prm):
                    vals = eval(node.GetStrAttr(prm))
                    try:
                        self.p.SetEmitterCf(paramCodes[prm], vals[0], vals[1])
                    except:
                        try:
                            self.p.SetEmitterCf(paramCodes[prm], vals)
                        except:
                            print string.join(apply(traceback.format_exception, sys.exc_info()))
            if node.GetStrAttr("program") == "default":
                pass
            self.p.dispatcher = self
            self.p.StartEmission()
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def _OnLifetimeOut(self, particles):
        #particles.Dispose()
        self.host.DetachEffect(self)
    
    def Show(self, flag):
        self.p.visible = flag
        
    def Dispose(self):
        self.p.Dispose()



#------------------------------------
# Спрайт двигается по заданному пути
# После завершения движения объект самоликвидируется
#------------------------------------

class Popup(scraft.Dispatcher):
    def __init__(self, sprite,
                 motionfunc, transpfunc, scalefunc, maxTime = 10000, state = None):
        self.sprite = sprite
        self.MotionFunc = motionfunc
        self.TranspFunc = transpfunc
        self.ScaleFunc = scalefunc
        self.MaxTime = maxTime
        self.State = state
        
        self.StartTime = oE.millis
        self.Timer = 0
        self.StartX = sprite.x
        self.StartY = sprite.y
        self.Queno = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):
        self.Timer += que.delta
        (self.sprite.x, self.sprite.y) = self.MotionFunc(self.StartX, self.StartY, self.Timer)
        self.sprite.transparency = self.TranspFunc(self.Timer)
        self.sprite.xScale, self.sprite.yScale = self.ScaleFunc(self.Timer)
        if self.Timer < self.MaxTime:
            return scraft.CommandStateRepeat
        else:
            self.Dispose()
            return scraft.CommandStateEnd
        
    def Activate(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Resume()
        else:
            oE.executor.GetQueue(self.QueNo).Suspend()
        
    def Dispose(self):
        self.sprite.Dispose()
        
#------------------------------------
# motion functions
#------------------------------------

#всплытие пузырьком
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

def BounceTransp(points):
    def f(t):
        return Interpolation(points, t, 0.001)
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


#------------ 
# Всплывающая (двигающаяся) надпись
#------------ 
def PopupText(text, font, x, y,
            motionfunc = DefaultMotion(), transpfunc = DefaultTransp(), scalefunc = DefaultScale(),
            maxTime = 10000, state = None):
    spr = MakeTextSprite(font, Layer_Popups, x, y, scraft.HotspotCenter, text)
    tmp = Popup(spr, motionfunc, transpfunc, scalefunc, maxTime, state)

#------------ 
# Спрайты движутся по заданному контуру
#------------ 
def DrawTrailedContour(params, contour, state = None):
    DefaultParams = { "klass": "star", "layer": 0, "no": 10, "incTrans": 5, "incScale": 3, "delay": 20 }
    prm = {}
    for tmp in DefaultParams.keys():
        if params.has_key(tmp):
            prm[tmp] = params[tmp]
        else:
            prm[tmp] = DefaultParams[tmp]
    tmpSprites = map(lambda x: spriteworks.MakeSprite(prm["klass"], prm["layer"],
                    { "x": contour[0][1], "y": contour[0][2], "hotspot": scraft.HotspotCenter,
                    "transparency": prm["incTrans"]*x,
                    "scale": 100 - prm["incScale"]*x }), xrange(prm["no"]))
    if contour[0][0] == 0:
        tmpTransFunc = DefaultTransp()
    else:
        tmpTransFunc = BounceTransp([(0, 100), (contour[0][0]-0.05, 100), (contour[0][0], 0), (100000, 0)])
    tmp = Popup(TrailProxy(tmpSprites, prm["delay"]), BounceMotion(contour), tmpTransFunc, DefaultScale(),
                (2*contour[-1][0] - contour[-2][0])*1000, state)

#------------ 
# Прокси: композитный спрайт
# Спрайты движутся за первым в виде шлейфа
# Задается задержка каждого спрайта относительно предыдущего
# (следующие спрайты повторяют движение первого, но с задержкой)
# При создании получает список спрайтов
#------------ 
class TrailProxy(scraft.Dispatcher, object):
    def __init__(self, sprites, delay):
        self.Sprites = sprites
        self.Delay = delay
        self.Timer = 0
        self.BasicTrans = map(lambda x: x.transparency, self.Sprites)
        #история координат (x,y) головного спрайта
        self.HistoryX = []
        self.HistoryY = []
        #количество видимых спрайтов шлейфа
        self.count = 0
        for i in range(len(self.Sprites)):
            self.Sprites[i].visible = False
        self.Queno = oE.executor.Schedule(self)
            
    def SetX(self, value):
        self.count = min(int(self.Timer/self.Delay), len(self.Sprites))
        for i in range(self.count):
            self.Sprites[i].visible = True
        
        self.HistoryX.append((self.Timer, value))
        for i in range(self.count-1, 0, -1):
            self.Sprites[i].x = Interpolation(self.HistoryX, self.Timer - i*self.Delay)
        self.Sprites[0].x = value
        
    def GetX(self):
        return self.Sprites[0].x
        
    x = property(GetX, SetX)
        
    def SetY(self, value):
        self.HistoryY.append((self.Timer, value))
        for i in range(len(self.Sprites)-1, 0, -1):
            self.Sprites[i].y = Interpolation(self.HistoryY, self.Timer - i*self.Delay)
        self.Sprites[0].y = value
        
    def GetY(self):
        return self.Sprites[0].y
        
    y = property(GetY, SetY)
        
    def SetTrans(self, value):
        for i in range(len(self.Sprites)):
            self.Sprites[i].transparency = self.BasicTrans[i] + value
            
    def GetTrans(self):
        return self.Sprites[0].transparency
        
    transparency = property(GetTrans, SetTrans)
        
    def _OnExecute(self, que):
        self.Timer += que.delta
        return scraft.CommandStateRepeat
        
    def Activate(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Resume()
        else:
            oE.executor.GetQueue(self.QueNo).Suspend()
        
    def Dispose(self):
        for spr in self.Sprites:
            spr.Dispose()
        del self.Sprites
        oE.executor.DismissQueue(self.QueNo)
        

#------------ 
# Линейная интерполяция значения 
# функции на основе таблицы значений
#------------ 
def Interpolation(points, t, eps = 1):
    t *= eps
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
