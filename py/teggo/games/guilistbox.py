#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

from guicomposite import GuiComposite

import guiaux, guipresenter
import localizer

class GuiListbox(GuiComposite):
    def __init__(self, host, parent, node, structure, ego):
        self.MultiSelect = structure.GetBoolAttr("multiple")
        self.height = structure.GetIntAttr("height")
        self.disableControl = structure.GetBoolAttr("disableControl")
        GuiComposite.__init__(self, host, parent, node, structure, ego)
        for el in self.Elements.values():
            el.host = self
        
        self.Actions = {}
        self.Actions["ScrollUp"] = self._ScrollUp
        self.Actions["ScrollDn"] = self._ScrollDn
        guipresenter.SetData(self.ego+"#height", self.height)
        
        self.command = None
        
        #список значений, из которых мы будем выбирать
        self.Values = []
        #индекс первого видимого элемента в списке
        self.FirstValue = 0
        #список индексов выбранных элементов
        self.SelectedValues = []
        #список имен кнопок. индекс кнопки в этом списке равен ее команде
        self.Buttons = []
        for tmp in structure.Tags("RadioButton"):
            self.Buttons.append(tmp.GetContent())
        
    def UpdateView(self):
        try:
            self.FirstValue = guipresenter.GetData(self.ego+"#first")
            self.Values = guipresenter.GetData(self.ego+"#Values")
            self.SelectedValues = guipresenter.GetData(self.ego+"#Selected")
            tmpActiveButtons = min(self.height, len(self.Values) - self.FirstValue)
            
            #текст на кнопках в списке
            for i in range(tmpActiveButtons):
                guipresenter.SetData(self.ego+"."+self.Buttons[i]+"#text", self.Values[i + self.FirstValue])
                if self.disableControl:
                    guipresenter.SetData(self.ego+"."+self.Buttons[i]+"#disabled", False)
            if tmpActiveButtons < self.height:
                for i in range(tmpActiveButtons, self.height):
                    guipresenter.SetData(self.ego+"."+self.Buttons[i]+"#text", "")
                    if self.disableControl:
                        guipresenter.SetData(self.ego+"."+self.Buttons[i]+"#disabled", True)
            
            for i in range(self.height):
                guipresenter.SetData(self.ego+"."+self.Buttons[i]+"#selected",
                        ((i + self.FirstValue) in guipresenter.GetData(self.ego+"#Selected")))
                    
            guipresenter.SetData(self.ego+".ScrollUp#disabled", (self.FirstValue == 0))
            guipresenter.SetData(self.ego+".ScrollDn#disabled", (self.FirstValue + self.height >= len(self.Values)))
            
            for el in self.Elements.values():
                el.UpdateView()
            if self.command == None:
                self.command = guipresenter.GetData(self.ego+"#action")
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
            
        
    def _ScrollUp(self):
        if self.FirstValue > 0:
            guipresenter.SetData(self.ego+"#first",  guipresenter.GetData(self.ego+"#first") - 1)
        self.UpdateView()
        
    def _ScrollDn(self):
        if self.FirstValue + self.height < len(self.Values):
            guipresenter.SetData(self.ego+"#first",  guipresenter.GetData(self.ego+"#first") + 1)
        self.UpdateView()
        
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
            guipresenter.SetData(self.ego+"#Selected", self.SelectedValues)
            self.UpdateView()
            #вызов команды обновления родительского диалога, если она присвоена
            if callable(self.command):
                self.command()
            
            
