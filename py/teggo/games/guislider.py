#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

import guiaux, guipresenter
import localizer

class Slider(guiaux.GuiObject, scraft.Dispatcher):
    def __init__(self, host, parent, node, ego):
        self.ego = ego
        self.host = host
        self.statehost = host
        self.style = guipresenter.GetStyle(node.GetStrAttr("style"))
        self.styleDefault = self.style
        self.hotspotDefault = scraft.HotspotCenter
        self.state = None
        self.Dragging = False
        self.command = None
        self.value = 0
        self.MinValue, self.MaxValue = node.GetIntAttr("minValue"), node.GetIntAttr("maxValue")
            
        self.Dummy = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Dummy.parent = parent
        self.Dummy.x, self.Dummy.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.Dummy.xSize, self.Dummy.ySize = self.style.GetTag("HitArea").GetIntAttr("width"), self.style.GetTag("HitArea").GetIntAttr("height")
        self.Dummy.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("HitArea").GetIntAttr("sublayer")
        if self.style.GetTag("HitArea").HasAttr("hotspot"):
            self.Dummy.hotspot = guiaux.GetHotspotValue(self.style.GetTag("HitArea").GetStrAttr("hotspot"))
        else:
            self.Dummy.hotspot = self.hotspotDefault
        self.Dummy.dispatcher = scraft.Dispatcher(self)
        
        #чувсвительная область, в которой происходит перетаскивание
        #при выходе за пределы этой области перетаскивание прекращается
        self.Dummy2 = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        self.Dummy2.parent = self.Dummy
        self.Dummy2.hierarchy.xScale, self.Dummy2.hierarchy.yScale = False, False
        if self.style.GetTag("HitArea").HasAttr("hotspot"):
            self.Dummy2.hotspot = guiaux.GetHotspotValue(self.style.GetTag("HitArea").GetStrAttr("hotspot"))
        else:
            self.Dummy2.hotspot = self.hotspotDefault
        self.Dummy2.xSize, self.Dummy2.ySize = self.style.GetTag("SensitiveArea").GetIntAttr("width"), self.style.GetTag("SensitiveArea").GetIntAttr("height")
        self.Dummy2.x, self.Dummy2.x = int((self.Dummy2.xHotspot - 0.5)*self.Dummy2.xSize), int((self.Dummy2.yHotspot - 0.5)*self.Dummy2.ySize)
        
        self.Background = oE.NewSprite_("$spritecraft$dummy$", parent.layer)
        if self.style.GetTag("Background").GetStrAttr("sprite") != "":
            self.Background.ChangeKlassTo(self.style.GetTag("Background").GetStrAttr("sprite"))
        if self.style.GetTag("Background").HasAttr("hotspot"):
            self.Background.hotspot = guiaux.GetHotspotValue(self.style.GetTag("Background").GetStrAttr("hotspot"))
        else:
            self.Background.hotspot = self.hotspotDefault
        self.Background.parent = self.Dummy
        self.Background.hierarchy.xScale, self.Background.hierarchy.yScale = False, False
        self.Background.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Background").GetIntAttr("sublayer")
        self.Background.x, self.Background.y = self.style.GetTag("Background").GetIntAttr("x"), self.style.GetTag("Background").GetIntAttr("y")
        
        self.Zipper = oE.NewSprite_(self.style.GetTag("Zipper").GetStrAttr("sprite"), parent.layer)
        #if self.style.GetTag("Zipper").HasAttr("hotspot"):
        #    self.Zipper.hotspot = guiaux.GetHotspotValue(self.style.GetTag("Zipper").GetStrAttr("hotspot"))
        #else:
        #    self.Zipper.hotspot = self.hotspotDefault
        self.Zipper.parent = self.Dummy
        self.Zipper.hierarchy.xScale, self.Zipper.hierarchy.yScale = False, False
        self.Zipper.sublayer = parent.sublayer + node.GetIntAttr("sublayer") + self.style.GetTag("Zipper").GetIntAttr("sublayer")
        self.Zipper.x, self.Zipper.y = self.style.GetTag("Zipper").GetIntAttr("x0"), self.style.GetTag("Zipper").GetIntAttr("y0")
        
        self.ZipperXRange = (self.style.GetTag("Zipper").GetIntAttr("x0"), self.style.GetTag("Zipper").GetIntAttr("x1"))
        self.ZipperYRange = (self.style.GetTag("Zipper").GetIntAttr("y0"), self.style.GetTag("Zipper").GetIntAttr("y1"))
        self.QueNo = oE.executor.Schedule(self)

    def _SetState(self, state = "Up"):
        try:
            self.state = state
            if self.style.GetTag("Zipper").GetSubtag(state) != None and \
                    self.style.GetTag("Zipper").GetSubtag(state).HasAttr("sprite"):
                ZipperKlass = self.style.GetTag("Zipper").GetSubtag(state).GetStrAttr("sprite")
            elif self.style.GetTag("Zipper").GetSubtag("Default") != None and \
                    self.style.GetTag("Zipper").GetSubtag("Default").HasAttr("sprite"):
                ZipperKlass = self.style.GetTag("Zipper").GetSubtag("Default").GetStrAttr("sprite")
            else:
                ZipperKlass = "$spritecraft$dummy$"
            self.Zipper.ChangeKlassTo(ZipperKlass)
            if self.style.GetTag("Zipper").GetSubtag(state) != None:
                self.Zipper.frno = self.style.GetTag("Zipper").GetSubtag(state).GetIntAttr("frno")
            else:
                self.Zipper.frno = self.style.GetTag("Zipper").GetSubtag("Default").GetIntAttr("frno")
            if self.style.GetTag("Zipper").HasAttr("hotspot"):
                self.Zipper.hotspot = guiaux.GetHotspotValue(self.style.GetTag("Zipper").GetStrAttr("hotspot"))
            else:
                self.Zipper.hotspot = self.hotspotDefault
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
            

    def UpdateView(self):
        try:
            value = guipresenter.GetData(self.ego+"#value")
            if value != None:
                value = _Nearest(value, (self.MinValue, self.MaxValue))
                self.value = value
            self._PlaceZipper()
                
            if not self.Dragging:
                self._SetState("Up")
            else:
                self._SetState("Down")
            if self.command == None:
                self.command = guipresenter.GetData(self.ego+"#onModify")
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        
    def _PlaceZipper(self):
        self.Zipper.x = self.ZipperXRange[0] + int(1.0*(self.value - self.MinValue)/(self.MaxValue - self.MinValue)*(self.ZipperXRange[1]-self.ZipperXRange[0]))
        self.Zipper.y = self.ZipperYRange[0] + int(1.0*(self.value - self.MinValue)/(self.MaxValue - self.MinValue)*(self.ZipperYRange[1]-self.ZipperYRange[0]))

    def Dispose(self):
        self.Zipper.Dispose()
        self.Background.Dispose()
        self.Dummy.Dispose()
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.Background.visible = flag
        self.Zipper.visible = flag
        
    #активирует кнопку, когда ее диалог становится активным
    def Activate(self, flag):
        if flag:
            self.Dummy.dispatcher = self
        else:
            self.Dummy.dispatcher = None
        try:
            if flag:
                oE.executor.GetQueue(self.QueNo).Resume()
            else:
                oE.executor.GetQueue(self.QueNo).Suspend()
        except:
            print self.QueNo, "failed to activate", flag
        
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
                #если нажатие было по бегунку, начать перетаскивание
                if self.Zipper.mouseOver:
                    self.Dragging = True
                #если нажатие в свободной точке, переместить туда бегунок
                #и пересчиать значение переменной
                else:
                    self.Zipper.x = _Nearest(x - self.Dummy.x, self.ZipperXRange)
                    self.Zipper.y = _Nearest(y - self.Dummy.y, self.ZipperYRange)
                    self._SetNewValue(x, y)
        
    def _OnMouseUp(self, sprite, x, y, button):
        if self.state != "Inert":
            if button == 1 and self.statehost.LastButtonPressed == self.ego:
                self._SetState("Roll")
                if self.Dragging:
                    self.Dragging = False
            self.statehost.LastButtonPressed = None

    def _OnExecute(self, que):
        if self.Dragging:
            self.Zipper.x = _Nearest(oE.mouseX - self.Dummy.x, self.ZipperXRange)
            self.Zipper.y = _Nearest(oE.mouseY - self.Dummy.y, self.ZipperYRange)
            self._SetNewValue(oE.mouseX, oE.mouseY)
            if not self.Dummy2.mouseOver:
                self.Dragging = False
                self.statehost.LastButtonPressed = None
        return scraft.CommandStateRepeat

    def _SetNewValue(self, x, y):
        if self.style.GetStrAttr("direction") == "Horizontal":
            newValue = self.MinValue + int(1.0*(x - self.Dummy.x - self.ZipperXRange[0])*(self.MaxValue - self.MinValue)/(self.ZipperXRange[1] - self.ZipperXRange[0]))
        else:
            newValue = self.MinValue + int(1.0*(y - self.Dummy.y - self.ZipperYRange[0])*(self.MaxValue - self.MinValue)/(self.ZipperYRange[1] - self.ZipperYRange[0]))
        newValue = _Nearest(newValue, (self.MinValue, self.MaxValue))
        self.value = newValue
        guipresenter.SetData(self.ego+"#value", newValue)
        if callable(self.command):
            self.command(newValue)


#ближайшее к value значение из отрезка range
def _Nearest(value, range):
    if range[0] > value:
        return range [0]
    elif range[1] < value:
        return range[1]
    else:
        return value
    