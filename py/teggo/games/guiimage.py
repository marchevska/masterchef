#!/usr/bin/env python
# -*- coding: cp1251 -*-


import string, sys, traceback
from random import randint

import scraft
from scraft import engine as oE
import guiaux

class Image(guiaux.GuiObject):
    def __init__(self, host, parent, node, ego):
        self.ego = ego
        self.host = host
        self.hotspotDefault = node.GetStrAttr("hotspot")
        
        if node.GetStrAttr("sprite") != "":
            self.klassName = node.GetStrAttr("sprite")
        else:
            self.klassName = "$spritecraft$dummy$"
        self.sprite = oE.NewSprite_(self.klassName, parent.layer)
        
        if node.GetStrAttr("animation") != "":
            self.animation = eval(node.GetStrAttr("animation"))
        else:
            self.animation = None
        self.Animator = None
            
        self.sprite.parent = parent
        self.sprite.x, self.sprite.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.sprite.sublayer = parent.sublayer + node.GetIntAttr("sublayer")
        
    def Dispose(self):
        self.sprite.Dispose()
        if self.Animator != None:
            self.Animator.Kill()
            self.Animator = None
        
    def Show(self, flag):
        self.sprite.visible = flag
        
    def UpdateView(self, data):
        try:
            klassName = data.get(self.ego+"#klass")
            if klassName != None:
                self.sprite.ChangeKlassTo(klassName)
            hotspot = data.get(self.ego+"#hotspot")
            if hotspot != None:
                self.sprite.hotspot = guiaux.GetHotspotValue(hotspot)
            elif self.hotspotDefault != "":
                self.sprite.hotspot = guiaux.GetHotspotValue(self.hotspotDefault)
            frno = data.get(self.ego+"#frno")
            if frno != None:
                self.sprite.frno = int(frno)
            x = data.get(self.ego+"#x")
            if x != None:
                self.sprite.x = x
            y = data.get(self.ego+"#y")
            if y != None:
                self.sprite.y = y
            visible = data.get(self.ego+"#visible")
            if visible != None:
                self.sprite.visible = visible
            if data.has_key(self.ego+"#animation"):
                self.animation = data[self.ego+"#animation"]
            if self.Animator == None and self.animation != None:
                self.Animator = ImageLoopAnimator(self.sprite, self.animation)
            elif self.Animator != None and self.animation == None:
                self.Animator.Kill()
                self.Animator = None
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def Activate(self, flag):
        if self.Animator != None:
            self.Animator.Activate(flag)
        
#циклическая анимация спрайта
#объект-аниматор постоянно привязан к спрайту
class ImageLoopAnimator(scraft.Dispatcher):
    def __init__(self, sprite, animation):
        self.Sprite = sprite
        self.Animation = animation
        self.NextFrameTime = 0
        self.NextFrame = 0
        self.QueNo = oE.executor.Schedule(self)
        self.Activate(False)
        
    def Activate(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Resume()
        else:
            oE.executor.GetQueue(self.QueNo).Suspend()
        
    def _OnExecute(self, que):
        try:
            if self.NextFrameTime <= 0:
                if self.NextFrame < len(self.Animation):
                    self.Sprite.frno = self.Animation[self.NextFrame][0]
                    tmpNextFrameData = self.Animation[self.NextFrame]
                    if len(tmpNextFrameData) == 2:
                        self.NextFrameTime += tmpNextFrameData[1]
                    else:
                        self.NextFrameTime += randint(tmpNextFrameData[1], tmpNextFrameData[2])
                    self.NextFrame = (self.NextFrame + 1) % len(self.Animation)
            self.NextFrameTime -= que.delta
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        return scraft.CommandStateRepeat
        
    def Kill(self):
        oE.executor.DismissQueue(self.QueNo)
        
