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
        self.FirstValue = data[self.ego+"#first"]
        self.Values = data[self.ego+"#Values"]
        self.SelectedValues = data[self.ego+"#Selected"]
        tmpActiveButtons = min(self.height, len(self.Values) - self.FirstValue)
        
        #текст на кнопках в списке
        for i in range(tmpActiveButtons):
            data[self.ego+".Player"+str(i)+"#text"] = self.Values[i + self.FirstValue]
            data[self.ego+".Player"+str(i)+"#disabled"] = False
        if tmpActiveButtons < self.height:
            for i in range(tmpActiveButtons, self.height):
                data[self.ego+".Player"+str(i)+"#text"] = ""
                data[self.ego+".Player"+str(i)+"#disabled"] = True
        
        for i in range(self.height):
            data[self.ego+".Player"+str(i)+"#selected"] = ((i + self.FirstValue) in data[self.ego+"#Selected"])
                
        data[self.ego+".ScrollUp#disabled"] = (self.FirstValue == 0)
        data[self.ego+".ScrollDn#disabled"] = (self.FirstValue + self.height >= len(self.Values))
        
        for el in self.Elements:
            el.UpdateView(data)
        
    def _ScrollUp(self):
        if self.FirstValue > 0:
            self.presenter.data[self.ego+"#first"] -= 1
        self.UpdateView(self.presenter.data)
        
    def _ScrollDn(self):
        if self.FirstValue + self.height < len(self.Values):
            self.presenter.data[self.ego+"#first"] += 1
        self.UpdateView(self.presenter.data)
        
    def ButtonAction(self, cmd):
        if cmd in self.Actions.keys():
            self.Actions[cmd]()
        else:
            tmpNo = self.FirstValue + eval(cmd)
            if self.MultiSelect:
                if tmpNo in self.SelectedValues:
                    self.SelectedValues.remove(tmpNo)
                else:
                    self.SelectedValues.append(tmpNo)
            else:
                self.SelectedValues = [tmpNo]
            self.presenter.data[self.ego+"#Selected"] = self.SelectedValues
            self.UpdateView(self.presenter.data)
