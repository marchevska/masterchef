#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

from guibutton import * 
from guiimage import Image
from guitext import TextLabel, TextEntry, TextArea
from guicomposite import GuiComposite, GuiDialog, GuiVariant, GuiActivator
from guilistbox import GuiListbox
from guislider import Slider

import guiaux
import localizer

class GuiPresenter:
    def __init__(self, filename):
        self.DefData = oE.ParseDEF(filename)
        self.data = {}
        
        #список видимых диалогов, сортированный снизу вверх
        self.DialogsList = []
        self.ActiveDialog = None
        
        
        #parse object styles if necessary
        
        self.Dialogs = {}
        for tmp in self.DefData.GetTag("Objects").Tags("Dialog"):
            self.CreateDialog(tmp.GetContent())
        for tmp in self.Dialogs.values():
            tmp.Show(False)
            tmp.Activate(False)
        self.LastEventProcessed = False
        
    def CreateDialog(self, name):
        self.Dialogs[name] = GuiDialog(self.ProcessStructure(self.DefData.GetTag("Objects").GetSubtag(name, "Dialog")),
                                       name, self)
       
        
    def CreateObject(self, host, parent, node, name):
        tmpTagName = node.GetName()
        if _StrCompNoCase(tmpTagName, "Image"):
            el = Image(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "PushButton"):
            el = PushButton(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "CheckBox"):
            el = CheckBox(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "RadioButton"):
            el = RadioButton(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "TextLabel"):
            el = TextLabel(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "Slider"):
            el = Slider(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "TextEntry"):
            el = TextEntry(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "TextArea"):
            el = TextArea(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "Variant"):
            el = GuiVariant(host, parent, node, self.ProcessStructure(node), name, self)
        elif _StrCompNoCase(tmpTagName, "Activator"):
            el = GuiActivator(host, parent, node, self.ProcessStructure(node), name, self)
        elif _StrCompNoCase(tmpTagName, "Case"):
            el = GuiComposite(host, parent, node, self.ProcessStructure(node), name, self)
        elif self.DefData.GetTag("Objects").GetSubtagNocase(tmpTagName, "Composite") != None:
            el = GuiComposite(host, parent, node,
                              self.ProcessStructure(self.DefData.GetTag("Objects").GetSubtagNocase(tmpTagName)), name, self)
        elif self.DefData.GetTag("Objects").GetSubtagNocase(tmpTagName, "Listbox") != None:
            el = GuiListbox(host, parent, node,
                              self.ProcessStructure(self.DefData.GetTag("Objects").GetSubtagNocase(tmpTagName)), name, self)
        else:
            el = None
        return el
        
    def ShowDialog(self, name, flag):
        if flag:
            if self.DialogsList.count(name) == 0:
                self.DialogsList.append(name)
                self.DialogsList.sort(lambda x,y: cmp(self.Dialogs[y].GetLayer(), self.Dialogs[x].GetLayer()))
            #self.Dialogs[name].Show(True)
            #self.Dialogs[name].UpdateView(self.data)
        else:
            #self.Dialogs[name].Show(False)
            if self.DialogsList.count(name)>0:
                self.DialogsList.remove(name)
        self.Dialogs[name].UpdateView(self.data)
        self.Dialogs[name].Show(flag)
        self._UpdateActiveDialog()
        
    def _UpdateActiveDialog(self):
        if self.ActiveDialog in self.Dialogs.keys():
            self.Dialogs[self.ActiveDialog].Activate(False)
        if self.DialogsList != []:
            self.ActiveDialog = self.DialogsList[-1]
            self.Dialogs[self.ActiveDialog].Activate(True)
        else:
            self.ActiveDialog = None
        
    #рекурсивная обработка структуры с циклами     
    def ProcessStructure(self, structure):
        for tmp in structure.Tags("Repeat"):
            variables = {}
            for var in tmp.Tags("Variable"):
                newVar = "$"+var.GetContent()+"$"
                if var.HasAttr("values"):
                    newVals = eval(var.GetStrAttr("values"))
                else:
                    newVals = range(var.GetIntAttr("start"), var.GetIntAttr("finish") + var.GetIntAttr("step"), var.GetIntAttr("step"))
                variables[newVar] = newVals
                
            totalValues = min(map(lambda x: len(variables[x]), variables.keys()))
            self.ProcessStructure(tmp.GetTag("Node"))
            for tmp2 in tmp.GetTag("Node").Tags():
                for i in range(totalValues):
                    newElement = tmp2.Clone()
                    vars = dict(map(lambda x: (x, variables[x][i]), variables.keys()))
                    ReplaceVariables(newElement, vars)
                    structure.InsertCopyOf(newElement)
        for tmp in structure.Tags("Repeat"):
            tmp.Erase()
        return structure
    
    #функции, связанные с обработкой событий
    def RaiseEvent(self):
        self.LastEventProcessed = False
        
    def MarkEventProcessed(self):
        self.LastEventProcessed = True
        
    def IsEventProcessed(self):
        return self.LastEventProcessed
    
#рекурсивная замена переменных на заданный набор значений
def ReplaceVariables(node, vars):
    tmpContent = node.GetContent()
    for var in vars.keys():
        tmpContent = tmpContent.replace(var, str(vars[var]))
    node.SetContent(tmpContent)
    for attr in list(node.Attributes()):
        newAttr = attr[1]
        for var in vars.keys():
            newAttr = newAttr.replace(var, str(vars[var]))
        try:
            newAttr = str(eval(newAttr))
        except:
            pass
        node.SetStrAttr(attr[0], newAttr)
    for tmp in node.Tags():
        ReplaceVariables(tmp, vars)
    
def _StrCompNoCase(str1, str2):
    return (string.lower(str1) == string.lower(str2))

    