#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

import guiaux
import localizer

#-------------------------------------
# Композит - общий случай составного объекта
#-------------------------------------
class GuiComposite(guiaux.GuiObject):
    # создание композитного объекта
    # host - владеющий диалог
    # parent - dummy-спрайт, к которому привязывается композит
    # node - нода из родительского объекта, описывающая кооринаты
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
        self.Elements = {}
        for tmp in structure.Tags():
            if string.lower(tmp.GetName()) == "parameter":
                if tmp.GetStrAttr("type") == "integer":
                    presenter.data[self.ego+"#"+tmp.GetContent()] = tmp.GetIntAttr("value")
                else:
                    presenter.data[self.ego+"#"+tmp.GetContent()] = tmp.GetStrAttr("value")
            else:
                self.Elements[tmp.GetContent()] = presenter.CreateObject(host, self.Dummy, tmp, self.ego + "." + tmp.GetContent())
        
    def Dispose(self):
        for tmp in self.Elements.values():
            tmp.Dispose()
        self.Dummy.Dispose()
        
    def Activate(self, flag):
        for el in self.Elements.values():
            el.Activate(flag)
        #for el in self.Elements.values()+self.Effects:
        #    el.Activate(flag)
        
    def Show(self, flag):
        self.Dummy.visible = flag
        #if not flag:
        #    for el in self.Effects:
        #        el.Dispose()
        
    def UpdateView(self, data):
        try:
            x = data.get(self.ego+"#x")
            if x != None:
                self.Dummy.x = x
            y = data.get(self.ego+"#y")
            if y != None:
                self.Dummy.y = y
            visible = data.get(self.ego+"#visible")
            if visible != None:
                self.Dummy.visible = visible
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        for el in self.Elements.values():
            el.UpdateView(data)
            
    
#-------------------------------------
# Диалоговое окно
# Частный случай Composite, у которого host - сам и parent всегда None
# Является хостом верхнего уровня (statehost) для своих активных элементов
# Отвечает за обработку событий
#-------------------------------------
class GuiDialog(GuiComposite, scraft.Dispatcher):
    def __init__(self, node, ego, presenter):
        self.presenter = presenter
        self.LastButtonPressed = None
        self.FocusOn = None
        GuiComposite.__init__(self, self, None, node, node, ego, presenter)
        self.Actions = {}
        self.Actions["Close_Ok"] = self._Close_Ok
        self.Actions["Close_Cancel"] = self._Close_Cancel
        self.KeyboardCommands = []
        for el in self.Elements.values():
            if el != self.FocusOn:
                el.LoseFocus()
        self.Effects = []
        self.QueNo = oE.executor.Schedule(self)
        
    def GetLayer(self):
        return self.Dummy.layer
        
    def Activate(self, flag):
        self.LastButtonPressed = None
        for el in self.Elements.values()+self.Effects:
            el.Activate(flag)
        try:
            if flag:
                oE.executor.GetQueue(self.QueNo).Resume()
            else:
                oE.executor.GetQueue(self.QueNo).Suspend()
        except:
            print self.QueNo, "failed to activate", flag
        
    def UpdateView(self, data):
        try:
            cmds = data.get(self.ego+"#kbdCommands")
            if cmds != None:
                self.KeyboardCommands = cmds
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        GuiComposite.UpdateView(self, data)
            
    def Show(self, flag):
        GuiComposite.Show(self, flag)
        if not flag:
            for el in self.Effects:
                el.Dispose()
                
    def _Close_Ok(self):
        #+actions
        self.presenter.ShowDialog(self.ego, False)
        
    def _Close_Cancel(self):
        #+actions
        self.presenter.ShowDialog(self.ego, False)
        
    def SetFocusTo(self, el):
        if self.FocusOn != None:
            self.FocusOn.LoseFocus()
        if el != None:
            el.GetFocus()
        self.FocusOn = el
    
    def ButtonAction(self, cmd):
        self.SetFocusTo(None)
        if cmd in self.Actions.keys():
            self.Actions[cmd]()
    
    def _OnExecute(self, que):
        try:
            if oE.EvtIsKeyDown() and not self.presenter.IsEventProcessed():
                if self.FocusOn != None and self.FocusOn.ProcessInput(self.presenter.data):
                    self.FocusOn.UpdateView(self.presenter.data)
                else:
                    for tmp in self.KeyboardCommands:
                        val = True
                        for cond in tmp["condition"]:
                            if cond["func"]() != cond["value"]:
                                val = False
                        if val:
                            self.presenter.MarkEventProcessed()
                            tmp["call"]()
                            break
                    #if oE.EvtKey() == scraft.Key_ESC:
                    #    self._Close_Cancel()
                    #elif oE.EvtKey() == scraft.Key_ENTER:
                    #    self._Close_Ok()
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        return scraft.CommandStateRepeat
        
    def AttachEffect(self, effectObject):
        self.Effects.append(effectObject)
        
    def DetachEffect(self, effectObject):
        if effectObject in self.Effects:
            effectObject.Dispose()
            self.Effects.remove(effectObject)
        
#-------------------------------------
# Variant содержит несколько композитов
# из которых в каждый момент виден только один
#-------------------------------------
class GuiVariant(GuiComposite):
    def __init__(self, host, parent, node, structure, ego, presenter):
        GuiComposite.__init__(self, host, parent, node, structure, ego, presenter)
        self.valueDefault = node.GetStrAttr("valueDefault")
        self.value = None
        
    def Activate(self, flag):
        for val in self.Elements.keys():
            self.Elements[val].Activate((val == self.value) and flag)
        
    def UpdateView(self, data):
        try:
            value = data.get(self.ego+"#value")
            if value != None:
                self.value = value
            else:
                self.value = self.valueDefault
            for val in self.Elements.keys():
                if val == self.value:
                    self.Elements[val].Show(True)
                    self.Elements[val].UpdateView(data)
                else:
                    self.Elements[val].Show(False)
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))

#-------------------------------------
# Activator - тип Варианта
#-------------------------------------
class GuiActivator(GuiComposite):
    def __init__(self, host, parent, node, structure, ego, presenter):
        GuiComposite.__init__(self, host, parent, node, structure, ego, presenter)
        self.valueDefault = node.GetStrAttr("valueDefault")
        self.value = None
        
    def Activate(self, flag):
        for val in self.Elements.keys():
            self.Elements[val].Show(val == str(flag))
            self.Elements[val].Activate(val == str(flag))
        
    
    
