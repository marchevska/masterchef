#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback, operator

import scraft
from scraft import engine as oE

from guibutton import * 
from guiimage import Image
from guitext import TextLabel, TextEntry, TextArea
from guicomposite import GuiComposite, GuiDialog, GuiVariant, GuiActivator
from guilistbox import GuiListbox
from guislider import Slider
from guibar import Bar

import guiaux
import localizer
import cursor
import fxmanager

ThePresenter = None

#-------------------------------------
# подключает файл с описаниями GUI
# информация добавляется последовательно; более страые файлы имеют приоритет!
#-------------------------------------
def UseFile(filename):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    ThePresenter.UseFile(filename)
        
def CreateObject(*a):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    ThePresenter.CreateObject(*a)

def ShowDialog(name, flag):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    ThePresenter.ShowDialog(name, flag)

def SetData(name, value):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    ThePresenter.SetData(name, value)

def GetData(name):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    return ThePresenter.GetData(name)

def GetStyle(name):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    return ThePresenter.GetStyle(name)

def CreateEffect(hostname, effectname, effectparam):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    ThePresenter.CreateEffect(hostname, effectname, effectparam)

def CreateObject(*a):
    global ThePresenter
    if ThePresenter == None:
        ThePresenter = GuiPresenter()
    return ThePresenter.CreateObject(*a)

class GuiPresenter(scraft.Dispatcher):
    def __init__(self):
        self.ObjectsData = scraft.Xdata()
        self.StylesData = scraft.Xdata()
        self.EffectsData = scraft.Xdata()
        self.data = {}
        self.Dialogs = {}
        self.DialogsList = []
        self.ActiveDialog = None
        self.QueNo = oE.executor.Schedule(self)
        
    def UseFile(self, filename):
        try:
            tmpDefData = oE.ParseDEF(filename)
            for tmpTags in tmpDefData.Tags("Objects"):
                for tmp in tmpTags.Tags():
                    self.ObjectsData.InsertCopyOf(tmp)
            for tmpTags in tmpDefData.Tags("Styles"):
                for tmp in tmpTags.Tags():
                    self.StylesData.InsertCopyOf(tmp)
            for tmpTags in tmpDefData.Tags("Effects"):
                for tmp in tmpTags.Tags():
                    self.EffectsData.InsertCopyOf(tmp)
        except:
            oE.Log("Unable to parse the following file: %s", filename)
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        
    #создать диалог, если он еще не создан
    # если данных по диалогу нет, - аварийный выход
    def _EnsureObjectExistence(self, name):
        tmpTagName = self.ObjectsData.GetSubtag(name).GetName()
        if  _StrCompNoCase(tmpTagName, "Cursor"):
            if not cursor.IsCreated() and self.ObjectsData.GetTag("Cursor") != None:
                cursor.Init(self.ObjectsData.GetTag("Cursor"))
            return
        elif _StrCompNoCase(tmpTagName, "Dialog"):
            if not name in self.Dialogs.keys():
                if self.ObjectsData.GetSubtag(name, "Dialog") != None:
                    self.Dialogs[name] = self.CreateObject(None, None, self.ObjectsData.GetSubtag(name, "Dialog"), name)
                    self.Dialogs[name].Show(False)
                    self.Dialogs[name].Activate(False)
                else:
                    oE.Log("Unable to find data for the following dialog: %s", name)
                    oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
                    sys.exit()
        
    def ShowDialog(self, name, flag):
        self._EnsureObjectExistence("Cursor")
        self._EnsureObjectExistence(name)
        if flag:
            if self.DialogsList.count(name) == 0:
                self.DialogsList.append(name)
                self.DialogsList.sort(lambda x,y: cmp(self.Dialogs[y].GetLayer(), self.Dialogs[x].GetLayer()))
        else:
            if self.DialogsList.count(name)>0:
                self.DialogsList.remove(name)
        self.Dialogs[name].UpdateView()
        self.Dialogs[name].Show(flag)
        self._UpdateActiveDialog()
        
    def CreateObject(self, host, parent, node, name):
        tmpTagName = node.GetName()
        if _StrCompNoCase(tmpTagName, "Dialog"):
            el = GuiDialog(self.ProcessStructure(node), name)
        elif _StrCompNoCase(tmpTagName, "Image"):
            el = Image(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "PushButton"):
            el = PushButton(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "CheckBox"):
            el = CheckBox(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "RadioButton"):
            el = RadioButton(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "TextLabel"):
            el = TextLabel(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "Slider"):
            el = Slider(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "Bar"):
            el = Bar(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "TextEntry"):
            el = TextEntry(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "TextArea"):
            el = TextArea(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "Variant"):
            el = GuiVariant(host, parent, node, self.ProcessStructure(node), name)
        elif _StrCompNoCase(tmpTagName, "Activator"):
            el = GuiActivator(host, parent, node, self.ProcessStructure(node), name)
        elif _StrCompNoCase(tmpTagName, "Case"):
            el = GuiComposite(host, parent, node, self.ProcessStructure(node), name)
        elif self.ObjectsData.GetSubtagNocase(tmpTagName, "Composite") != None:
            el = GuiComposite(host, parent, node,
                              self.ProcessStructure(self.ObjectsData.GetSubtagNocase(tmpTagName)), name)
        elif self.ObjectsData.GetSubtagNocase(tmpTagName, "Listbox") != None:
            el = GuiListbox(host, parent, node,
                              self.ProcessStructure(self.ObjectsData.GetSubtagNocase(tmpTagName)), name)
        else:
            el = None
        return el
            
    def _UpdateActiveDialog(self):
        if self.DialogsList != [] and self.ActiveDialog == self.DialogsList[-1]:
            return
        if self.ActiveDialog in self.Dialogs.keys():
            self.Dialogs[self.ActiveDialog].Activate(False)
        if self.DialogsList != []:
            self.ActiveDialog = self.DialogsList[-1]
            self.Dialogs[self.ActiveDialog].Activate(True)
        else:
            self.ActiveDialog = None
        
    def _OnExecute(self, que):
        try:
            if oE.EvtIsKeyDown():
                if self.ActiveDialog != None and self.Dialogs[self.ActiveDialog].ProcessInput():
                    self.Dialogs[self.ActiveDialog].UpdateView()
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        return scraft.CommandStateRepeat
        
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
    
    def SetData(self, name, value):
        self.data[name] = value
        
    def GetData(self, name):
        hostname = name[0:min((name+".").find("."), (name+"#").find("#"))]
        self._EnsureObjectExistence(hostname)
        return self.data.get(name)
        
    def GetStyle(self, name):
        return self.StylesData.GetSubtag(name)
        
    def CreateEffect(self, hostname, effectname, effectparam):
        self._EnsureObjectExistence(hostname)
        
        if self.GetData(hostname+"#EffectsLayer") != None:
            layer = self.GetData(hostname+"#EffectsLayer")
        else:
            layer = self.Dialogs[hostname].GetLayer()
        if self.GetData(hostname+"#EffectsSublayer") != None:
            sublayer = self.GetData(hostname+"#EffectsSublayer")
        else:
            sublayer = 0
        
        if not operator.isMappingType(effectparam):
            effectparam = {}
        effectparam["layer"] = layer
        effectparam["sublayer"] = sublayer
        #self.Dialogs[hostname].AttachEffect(fxmanager.CreateEffect(self.Dialogs[hostname], effectname, effectparam))
        self.Dialogs[hostname].AttachEffect(fxmanager.CreateEffect(self.Dialogs[hostname],
                                            self.EffectsData.GetSubtag(effectname), effectparam))
        
  
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

    