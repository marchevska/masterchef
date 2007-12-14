#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE
import guiaux

class GuiComposite(guiaux.GuiObject):
    # создание композитного объекта
    # host - владеющий диалог
    # parent - dummy-спрайт, к которому цепляется композит
    # node - нода из родительского обхекта, описывающая кооринаты
    # structure - описание структуры, состав объекта
    # ego - имя
    # presenter - фабрика объектов
    def __init__(self, host, parent, node, structure, ego, presenter):
        self.ego = ego
        self.host = host
        self.parent = parent
        if parent != None:
            tmpLayer = parent.layer
        else:
            tmpLayer = node.GetIntAttr("layer")
        self.Dummy = oE.NewSprite_("$spritecraft$dummy$", tmpLayer)
        if parent != None:
            self.Dummy.sublayer = parent.sublayer + structure.GetIntAttr("sublayerBase")
            self.Dummy.parent = parent
        else:
            self.Dummy.sublayer = structure.GetIntAttr("sublayerBase")
        self.Dummy.x, self.Dummy.y = node.GetIntAttr("x"), node.GetIntAttr("y")
        self.Elements = []
        for tmp in structure.Tags():
            self.Elements.append(presenter.CreateObject(host, self.Dummy, tmp, self.ego + "." + tmp.GetContent()))
        
    def Dispose(self):
        for tmp in self.Elements:
            tmp.Dispose()
        self.Dummy.Dispose()
        
    def Activate(self, flag):
        for el in self.Elements:
            el.Activate(flag)
        
    def Show(self, flag):
        self.Dummy.visible = flag
        
    def UpdateView(self, data):
        for el in self.Elements:
            el.UpdateView(data)
            
    
class GuiDialog(GuiComposite):
    def __init__(self, node, ego, presenter):
        # Dialog - частный случай Composite, у которого host - сам и parent всегда None
        GuiComposite.__init__(self, self, None, node, node, ego, presenter)
        #self.host = None
        self.presenter = presenter
        self.LastButtonPressed = None
        self.Actions = {}
        self.Actions["Close_Ok"] = self._Close_Ok
        self.Actions["Close_Cancel"] = self._Close_Cancel
        
    def Activate(self, flag):
        self.LastButtonPressed = None
        GuiComposite.Activate(self, flag)
        
    def _Close_Ok(self):
        #+actions
        self.presenter.ShowDialog(self.ego, False)
        
    def _Close_Cancel(self):
        #+actions
        self.presenter.ShowDialog(self.ego, False)
        
    def ButtonAction(self, cmd):
        if cmd in self.Actions.keys():
            self.Actions[cmd]()
        
        
    
