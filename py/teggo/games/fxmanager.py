#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Набор классов для управления спецэффектами
"""

import sys, traceback, operator
import scraft
from scraft import engine as oE
import math, string
from random import randint, choice

import spriteworks

def CreateEffect(host, name, param):
    tmpNode = oE.ParseDEF("def/effects.def").GetTag("Effects").GetSubtag(name)
    if string.lower(tmpNode.GetName()) == "particles":
        return ParticleEffect(host, tmpNode, param)
    elif string.lower(tmpNode.GetName()) == "popup":
        return PopupEffect(host, tmpNode, param)
    elif string.lower(tmpNode.GetName()) == "trail":
        return CreateTrailEffect(host, tmpNode, param)

class Effect:
    def __init__(self, host, node, crd):
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
# Спрайт двигается по заданному пути,
# с заданным изменением прозрачности и масштаба,
# заданное время
#------------------------------------

class PopupEffect(Effect, scraft.Dispatcher):
    #------------------------------------
    # param содержит список параметров для создаваемого спрайта
    # sprite - можно передать эффекту уже существующий спрайт
    # layer - слой, на котором будет размещен спрайт
    # text - текст, если спрайт текстовый
    # sublayer - подслой (актуально для корректного размещения в диалогах)
    # crd - начальные координаты спрайта
    # AutoDispose - удалить спрайт после завершения эффекта
    # (актуально при передаче готового спрайта)
    #------------------------------------
    def __init__(self, host, node, param):
        try:
            self.host = host
            if param.has_key("sprite"):
                self.sprite = param["sprite"]
                if param.has_key("layer"):
                    self.sprite.layer = param["layer"]
            else:
                #слой, заданный из скрипта, важнее, чем предопределенный в спеке
                if param.has_key("layer"):
                    tmpLayer = param["layer"]
                elif node.HasAttr("layer"):
                    tmpLayer = node.GetIntAttr("layer")
                else:
                #заменить!
                    tmpLayer = 0
                self.sprite = spriteworks.MakeSprite(node.GetStrAttr("sprite"), tmpLayer)
                self.sprite.hotspot = scraft.HotspotCenter
            if param.has_key("text"):
                self.sprite.text = param["text"]
            if param.has_key("sublayer"):
                self.sprite.sublayer = param["sublayer"]
            elif node.HasAttr("sublayer"):
                self.sprite.sublayer = node.GetIntAttr("sublayer")
            if param.has_key("crd"):
                self.sprite.x, self.sprite.y = param["crd"]
            elif node.HasAttr("crd"):
                self.sprite.x, self.sprite.y = eval(node.GetStrAttr("crd"))
            #удаление спрайта после завершения эффекта
            if param.has_key("AutoDispose"):
                self.AutoDispose = param["AutoDispose"]
            else:
                self.AutoDispose = True
            
            self.MotionFunc = _GetMotionFunc(node)
            self.TranspFunc = _GetTranspFunc(node)
            self.ScaleFunc = _GetScaleFunc(node)
                    
            if node.HasAttr("time"):
                self.MaxTime = node.GetIntAttr("time")
            #elif node.GetBoolAttr("adjustTime") == True:
            #    pass
            else:
                self.MaxTime = None
                
            self.Timer = 0
            self.StartX = self.sprite.x
            self.StartY = self.sprite.y
            self.QueNo = oE.executor.Schedule(self)
            self.Activate(True)
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
            
    def _OnExecute(self, que):
        self.Timer += que.delta
        (self.sprite.x, self.sprite.y) = self.MotionFunc(self.StartX, self.StartY, self.Timer)
        self.sprite.transparency = self.TranspFunc(self.Timer)
        self.sprite.xScale, self.sprite.yScale = self.ScaleFunc(self.Timer)
        if self.MaxTime != None and self.Timer >= self.MaxTime:
            self.host.DetachEffect(self)
            #return scraft.CommandStateEnd
        else:
            return scraft.CommandStateRepeat
        
    def GetTime(self):
        return self.Timer
        
    def Activate(self, flag):
        try:
            if oE.executor.GetQueue(self.QueNo) != None:
                if flag:
                    oE.executor.GetQueue(self.QueNo).Resume()
                else:
                    oE.executor.GetQueue(self.QueNo).Suspend()
        except:
            oE.Log("Error in que activation: "+str(self.QueNo)+", "+str(flag))
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            
        
    def Dispose(self):
        if self.AutoDispose:
            self.sprite.Dispose()
        oE.executor.DismissQueue(self.QueNo)
        
    
def CreateTrailEffect(host, node, param):
    FrnoFunc = _GetTrailFrnoFunc(node)
    TranspFunc = _GetTrailTranspFunc(node)
    ScaleFunc = _GetTrailScaleFunc(node)
    
    if node.GetTag("Motion").GetStrAttr("type") == "contour":
        x0, y0 = eval(node.GetTag("Motion").GetStrAttr("contour"))[0]
    else:
        x0, y0 = (eval(node.GetTag("Motion").GetStrAttr("points"))[0][1],
                  eval(node.GetTag("Motion").GetStrAttr("points"))[0][2]) 
    
    tmpLayer = 0
    
    tmpSprites = map(lambda i: spriteworks.MakeSprite(node.GetStrAttr("sprite"), tmpLayer,
                    { "x": x0, "y": y0, "hotspot": scraft.HotspotCenter,
                    "frno": FrnoFunc(i),"xyScale": ScaleFunc(i), "transparency": TranspFunc(i),}),
                    xrange(node.GetIntAttr("count")))
    tmpSrpProxy = TrailProxy(tmpSprites, node.GetIntAttr("delay"))
    newParam = {}
    newParam["sprite"] = tmpSrpProxy
    if param.has_key("crd"):
        newParam["crd"] = param["crd"]
    # crd - начальные координаты спрайта
    eff = PopupEffect(host, node, newParam)
    tmpSrpProxy.SetHost(eff)
    return eff
    
#----------------------------------------------------------- 
# Функции для PopupEffect
# У спрайта в PopupEffect могут меняться:
# координаты, прозрачность и масштаб
#----------------------------------------------------------- 

#------------------------------------
# преобразование контура в ломаную
#------------------------------------
def _ConvertContour(contour, speed, t0):
    def _Diff(a, b):
        if operator.isNumberType(a) and operator.isNumberType(b):
            return abs(a-b)
        elif operator.isSequenceType(a) and operator.isSequenceType(b):
            return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        else:
            return 0
    def _Alloy(t, a):
        if operator.isNumberType(a):
            return (t, a)
        elif operator.isSequenceType(a):
            return (t, a[0], a[1])
    
    tmpTimes = [t0] + map(lambda ii: int(1000*_Diff(contour[ii],contour[ii+1])/speed), range(len(contour)-1))
    tmpTimesSums = map(lambda x: reduce(lambda a,b: a+b, tmpTimes[0:x+1],0), range(len(contour)))
    tmpPoints = map(lambda x: _Alloy(tmpTimesSums[x], contour[x]), range(len(contour)))
    return tmpPoints

#------------------------------------
# motion functions
#------------------------------------

def _GetMotionFunc(node):
    if node.GetTag("Motion") != None:
        type = node.GetTag("Motion").GetStrAttr("type")
        if type == "bubble":
            a0 = node.GetTag("Motion").GetIntAttr("a0")
            a1 = node.GetTag("Motion").GetIntAttr("a1")
            return _BubbleMotion(a0, a1)
        elif type == "bounce":
            points = eval(node.GetTag("Motion").GetStrAttr("points"))
            return _BounceMotion(points)
        elif type == "contour":
            points = _ConvertContour(eval(node.GetTag("Motion").GetStrAttr("contour")),
                    node.GetTag("Motion").GetIntAttr("speed"), node.GetTag("Motion").GetIntAttr("t0"))
            return _BounceMotion(points)
        else:
            return _DefaultMotion()
    else:
        return _DefaultMotion()
    
#на месте
def _DefaultMotion():
    def f(x0, y0, t):
        return (x0, y0)
    return f
    
#всплытие пузырьком
def _BubbleMotion(a0, a1):
    def f(x0, y0, t):    
        return (x0, y0 + a1*(0.001*t) + a0*(0.001*t)**2)
    return f

#движение по ломаной
def _BounceMotion(points):
    def f(x0, y0, t):
        #eps = 0.001
        #t *= 0.001
        eps = 1
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
        return (x0+tmpX, y0+tmpY)
    return f

#------------------------------------
# transparency functions
#------------------------------------
def _GetTranspFunc(node):
    if node.GetTag("Transparency") != None:
        type = node.GetTag("Transparency").GetStrAttr("type")
        if type == "fadeaway":
            a0 = node.GetTag("Transparency").GetIntAttr("a0")
            a1 = node.GetTag("Transparency").GetIntAttr("a1")
            return _FadeAwayTransp(a0, a1)
        elif type == "blink":
            a = node.GetTag("Transparency").GetIntAttr("a")
            t0 = node.GetTag("Transparency").GetIntAttr("t0")
            b = node.GetTag("Transparency").GetIntAttr("b")
            return _BlinkTransp(a, t0, b)
        elif type == "bounce":
            points = eval(node.GetTag("Transparency").GetStrAttr("points"))
            return _BounceTransp(points)
        else:
            return _DefaultTransp()
    else:
        return _DefaultTransp()

#прозрачность не меняется
def _DefaultTransp():
    def f(t):
        return 0
    return f

#угасание
def _FadeAwayTransp(a0, a1):
    def f(t):
        return min(100, max((0.001*t)*a0+a1, 0))    
    return f

#вспышка
def _BlinkTransp(a, t0, b):
    def f(t):
        return max(a*(0.001*(t-t0))**2+b, 0)
    return f

#изменение по контрольным точкам (ломаная)
def _BounceTransp(points):
    def f(t):
        #return Interpolation(points, t, 0.001)
        return Interpolation(points, t, 1)
    return f
    
#------------------------------------
# scale functions
#------------------------------------
def _GetScaleFunc(node):
    if node.GetTag("Scale") != None:
        type = node.GetTag("Scale").GetStrAttr("type")
        if type == "blink":
            a = node.GetTag("Scale").GetIntAttr("a")
            t0 = node.GetTag("Scale").GetIntAttr("t0")
            b = node.GetTag("Scale").GetIntAttr("b")
            c = node.GetTag("Scale").GetIntAttr("c")
            return _BlinkScale(a, t0, b, c)
        elif type == "bounce":
            points = eval(node.GetTag("Scale").GetStrAttr("points"))
            return _BounceScale(points)
        else:
            return _DefaultScale()
    else:
        return _DefaultScale()

#нет изменения масштаба
def _DefaultScale():
    def f(t):
        return (100, 100)
    return f

#вспышка
def _BlinkScale(a, t0, b, c=100):
    #c - minimal scale
    def f(t):
        tmp = a*(0.001*(t-t0))**2+b
        return (max(min(tmp,c),0), max(min(tmp,c),0))
    return f

#изменение по контрольным точкам (ломаная)
def _BounceScale(points):
    def f(t):
        #eps = 0.001
        #t *= 0.001
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
        return (tmp, tmp)
    return f


#----------------------------------------------------------- 
# Функции для шлейфа
# У частиц шлейфа могут меняться:
# номер кадра, прозрачность и размер - 
# все это в зависимости от номера частицы
#----------------------------------------------------------- 

#------------ 
# вычисление frno частицы по ее номеру
#------------ 
def _GetTrailFrnoFunc(node):
    if node.GetTag("TrailFrno") != None:
        type = node.GetTag("TrailFrno").GetStrAttr("type")
        if type == "func":
            func = node.GetTag("TrailFrno").GetStrAttr("func")
            var = node.GetTag("TrailFrno").GetStrAttr("var")
            return _FuncTrailFrno(func, var)
        elif type == "random":
            frcount = node.GetTag("TrailFrno").GetIntAttr("frcount")
            return _RandomTrailFrno(frcount)
        elif type == "list":
            valuelist = eval(node.GetTag("TrailFrno").GetStrAttr("valuelist"))
            return _ListTrailFrno(valuelist)
        else:
            return _DefaultTrailFrno()
    else:
        return _DefaultTrailFrno()
    
def _DefaultTrailFrno():
    def f(no):
        return 0
    return f

def _FuncTrailFrno(func, var):
    def f(no):
        newStr = func.replace(var, str(no))
        try:
            return eval(newStr)
        except:
            return 0
    return f

def _RandomTrailFrno(frcount):
    def f(no):
        return randint(0, frcount)
    return f

def _ListTrailFrno(valuelist):
    def f(no):
        return valuelist[no % len(valuelist)]
    return f

#------------ 
# вычисление transparency частицы по ее номеру
#------------ 
def _GetTrailTranspFunc(node):
    if node.GetTag("TrailTransp") != None:
        type = node.GetTag("TrailTransp").GetStrAttr("type")
        if type == "func":
            func = node.GetTag("TrailTransp").GetStrAttr("func")
            var = node.GetTag("TrailTransp").GetStrAttr("var")
            return _FuncTrailTransp(func, var)
        elif type == "list":
            valuelist = eval(node.GetTag("TrailTransp").GetStrAttr("valuelist"))
            return _ListTrailTransp(valuelist)
        else:
            return _DefaultTrailTransp()
    else:
        return _DefaultTrailTransp()

def _DefaultTrailTransp():
    def f(no):
        return 0
    return f

def _FuncTrailTransp(func, var):
    def f(no):
        newStr = func.replace(var, str(no))
        try:
            return min(100, eval(newStr))
        except:
            return 0
    return f

def _ListTrailTransp(valuelist):
    def f(no):
        return valuelist[no % len(valuelist)]
    return f

#------------ 
# вычисление scale частицы по ее номеру
#------------ 
def _GetTrailScaleFunc(node):
    if node.GetTag("TrailScale") != None:
        type = node.GetTag("TrailScale").GetStrAttr("type")
        if type == "func":
            str = node.GetTag("TrailScale").GetStrAttr("str")
            var = node.GetTag("TrailScale").GetStrAttr("var")
            return _FuncTrailScale(str, var)
        elif type == "list":
            valuelist = eval(node.GetTag("TrailScale").GetStrAttr("valuelist"))
            return _ListTrailScale(valuelist)
        else:
            return _DefaultTrailScale()
    else:
        return _DefaultTrailScale()

def _DefaultTrailScale():
    def f(no):
        return (100, 100)
    return f

def _FuncTrailScale(func, var):
    def f(no):
        newStr = func.replace(var, str(no))
        try:
            return (eval(newStr), eval(newStr))
        except:
            return (100, 100)
    return f

def _ListTrailScale(valuelist):
    def f(no):
        return (valuelist[no % len(valuelist)], valuelist[no % len(valuelist)])
    return f


#------------ 
# Прокси: композитный спрайт
# Спрайты движутся за первым в виде шлейфа
# Задается задержка каждого спрайта относительно предыдущего
# (следующие спрайты повторяют движение первого, но с задержкой)
# При создании получает список спрайтов
# Предполагается, что прокси используется в PopupEffect
# вместо спрайта
#------------ 
class TrailProxy(object):
    def __init__(self, sprites, delay):
        self.Sprites = sprites
        self.Delay = delay
        self.Timer = 0
        self.Host = None
        self.BasicTrans = map(lambda x: x.transparency, self.Sprites)
        self.BasicXScale = map(lambda x: x.xScale, self.Sprites)
        self.BasicYScale = map(lambda x: x.yScale, self.Sprites)
        #история координат (x,y) головного спрайта
        self.HistoryX = []
        self.HistoryY = []
        #количество видимых спрайтов шлейфа; в начале движения спрайты невидимы
        self.count = 0
        for i in range(len(self.Sprites)):
            self.Sprites[i].visible = False
            
    #------------ 
    # host - агрегирующий эффект, который будет считать время!
    #------------ 
    def SetHost(self, host):
        self.Host = host
        
    def _UpdateTimer(self):
        if self.Host != None:
            self.Timer = self.Host.GetTime()
        self.count = min(int(self.Timer/self.Delay), len(self.Sprites))
        for i in range(self.count):
            self.Sprites[i].visible = True
        
    #------------ 
    # define property: x
    #------------ 
    def SetX(self, value):
        self._UpdateTimer()
        self.HistoryX.append((self.Timer, value))
        for i in range(self.count-1, 0, -1):
            self.Sprites[i].x = Interpolation(self.HistoryX, self.Timer - i*self.Delay)
        self.Sprites[0].x = value
        
    def GetX(self):
        return self.Sprites[0].x
        
    x = property(GetX, SetX)
        
    #------------ 
    # define property: y
    #------------ 
    def SetY(self, value):
        #self._UpdateTimer()
        self.HistoryY.append((self.Timer, value))
        for i in range(len(self.Sprites)-1, 0, -1):
            self.Sprites[i].y = Interpolation(self.HistoryY, self.Timer - i*self.Delay)
        self.Sprites[0].y = value
        
    def GetY(self):
        return self.Sprites[0].y
        
    y = property(GetY, SetY)
        
    #------------ 
    # define property: transparency
    #------------ 
    def SetTrans(self, value):
        #self._UpdateTimer()
        for i in range(len(self.Sprites)):
            self.Sprites[i].transparency = self.BasicTrans[i] + value
            
    def GetTrans(self):
        return self.Sprites[0].transparency
        
    transparency = property(GetTrans, SetTrans)
        
    #------------ 
    # define property: xScale
    #------------ 
    def SetXScale(self, value):
        #self._UpdateTimer()
        for i in range(len(self.Sprites)):
            self.Sprites[i].xScale = int(self.BasicXScale[i]*value/100)
            
    def GetXScale(self):
        return self.Sprites[0].xScale
        
    xScale = property(GetXScale, SetXScale)
        
    #------------ 
    # define property: yScale
    #------------ 
    def SetYScale(self, value):
        #self._UpdateTimer()
        for i in range(len(self.Sprites)):
            self.Sprites[i].yScale = int(self.BasicYScale[i]*value/100)
            
    def GetYScale(self):
        return self.Sprites[0].yScale
        
    yScale = property(GetYScale, SetYScale)
        
    #------------ 
    # that's all for propeties
    #------------ 
        
    def Dispose(self):
        for spr in self.Sprites:
            spr.Dispose()
        del self.Sprites
        

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
