#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

import guiaux
from guicomposite import GuiComposite

def Init(node, presenter):
    global TheCursor
    TheCursor = Cursor(node, presenter)

def SetState(state):
    global TheCursor
    TheCursor.SetState(state)

class Cursor(GuiComposite, scraft.Dispatcher):
    def __init__(self, node, presenter):
        GuiComposite.__init__(self, self, None, node, node, "Cursor", presenter)
        self.presenter = presenter
        self.States = map(lambda x: x.GetContent(), node.GetSubtag("Pointer").Tags("Case"))
        self.Show(False)
        self.QueNo = oE.executor.Schedule(self)
        
    def _OnExecute(self, que):    
        self.Show(oE.mouseIn)
        self.Dummy.x = oE.mouseX
        self.Dummy.y = oE.mouseY
        self.UpdateView(self.presenter.data)
        return scraft.CommandStateRepeat
        
    def SetState(self, state):
        if state in self.States:
            self.presenter.data[self.ego+".Pointer#value"] = state
    
