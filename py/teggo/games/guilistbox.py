#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

from guicomposite import GuiComposite

import guiaux
import localizer

class GuiListbox(GuiComposite):
    def __init__(self, host, parent, node, structure, ego, presenter):
        self.MultiSelect = structure.GetBoolAttr("multiple")
        self.height = structure.GetIntAttr("height")
        GuiComposite.__init__(self, host, parent, node, structure, ego, presenter)
        self.presenter = presenter
        for el in self.Elements:
            el.host = self
        
        self.Actions = {}
        self.Actions["ScrollUp"] = self._ScrollUp
        self.Actions["ScrollDn"] = self._ScrollDn
        
        presenter.data[self.ego+"#height"] = self.height
        self.Values = []
        self.FirstValue = 0
        self.SelectedValues = []
        
    def UpdateView(self, data):
        self.FirstValue = data["Players.List#first"]
        self.Values = data["Players.List#Values"]
        tmpActiveButtons = min(self.height, len(self.Values) - self.FirstValue)
        
        #текст на кнопках в списке
        for i in range(tmpActiveButtons):
            data["Players.List.Player"+str(i)+"#text"] = self.Values[i + self.FirstValue]
            data["Players.List.Player"+str(i)+"#disabled"] = False
        if tmpActiveButtons < self.height:
            for i in range(tmpActiveButtons, self.height):
                data["Players.List.Player"+str(i)+"#text"] = ""
                data["Players.List.Player"+str(i)+"#disabled"] = True
        
        for i in range(self.height):
            data["Players.List.Player"+str(i)+"#selected"] = ((i + self.FirstValue) in data["Players.List#Selected"])
                
        data["Players.List.ScrollUp#disabled"] = (self.FirstValue == 0)
        data["Players.List.ScrollDn#disabled"] = (self.FirstValue + self.height >= len(self.Values))
        
        for el in self.Elements:
            el.UpdateView(data)
        
    def _ScrollUp(self):
        if self.FirstValue > 0:
            self.presenter.data["Players.List#first"] -= 1
        self.UpdateView(self.presenter.data)
        
    def _ScrollDn(self):
        if self.FirstValue + self.height < len(self.Values):
            self.presenter.data["Players.List#first"] += 1
        self.UpdateView(self.presenter.data)
        
    def ButtonAction(self, cmd):
        if cmd in self.Actions.keys():
            self.Actions[cmd]()
