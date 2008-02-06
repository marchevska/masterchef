#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

import guiaux, guipresenter
import localizer
import musicsound

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
    def __init__(self, host, parent, node, structure, ego):
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
                    guipresenter.SetData(self.ego+"#"+tmp.GetContent(), tmp.GetIntAttr("value"))
                else:
                    guipresenter.SetData(self.ego+"#"+tmp.GetContent(), tmp.GetStrAttr("value"))
            else:
                self.Elements[tmp.GetContent()] = guipresenter.CreateObject(host, self.Dummy, tmp, self.ego + "." + tmp.GetContent())
        
    def Dispose(self):
        for tmp in self.Elements.values():
            tmp.Dispose()
        self.Dummy.Dispose()
        
    def Activate(self, flag):
        for el in self.Elements.values():
            el.Activate(flag)
        
    def Show(self, flag):
        self.Dummy.visible = flag
        
    def UpdateView(self):
        try:
            x = guipresenter.GetData(self.ego+"#x")
            if x != None:
                self.Dummy.x = x
            y = guipresenter.GetData(self.ego+"#y")
            if y != None:
                self.Dummy.y = y
            visible = guipresenter.GetData(self.ego+"#visible")
            if visible != None:
                self.Dummy.visible = visible
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        for el in self.Elements.values():
            el.UpdateView()
            
    
#-------------------------------------
# Диалоговое окно
# Частный случай Composite, у которого host - сам и parent всегда None
# Является хостом верхнего уровня (statehost) для своих активных элементов
# Отвечает за обработку событий
#-------------------------------------
class GuiDialog(GuiComposite):
    def __init__(self, node, ego):
        self.MusicTheme = node.GetStrAttr("music")
        self.LastButtonPressed = None
        self.FocusOn = None
        GuiComposite.__init__(self, self, None, node, node, ego)
        self.onActivate = None
        self.onDeactivate = None
        self.KeyboardCommands = []
        for el in self.Elements.values():
            if el != self.FocusOn:
                el.LoseFocus()
        self.Effects = []
        
    def GetLayer(self):
        return self.Dummy.layer
        
    def Activate(self, flag):
        self.LastButtonPressed = None
        for el in self.Elements.values()+self.Effects:
            el.Activate(flag)
        if flag:
            musicsound.SetState(self.MusicTheme)
            if callable(self.onActivate):
                self.onActivate(self.ego)
        else:
            if callable(self.onDeactivate):
                self.onDeactivate(self.ego)
        
    def UpdateView(self):
        try:
            cmds = guipresenter.GetData(self.ego+"#kbdCommands")
            if cmds != None:
                self.KeyboardCommands = cmds
            onActivate = guipresenter.GetData(self.ego+"#onActivate")
            if onActivate != None:
                self.onActivate = onActivate
            onDeactivate = guipresenter.GetData(self.ego+"#onDeactivate")
            if onDeactivate != None:
                self.onDeactivate = onDeactivate
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))
        GuiComposite.UpdateView(self)
            
    def Show(self, flag):
        GuiComposite.Show(self, flag)
        if not flag:
            for el in self.Effects:
                el.Dispose()
                
    def SetFocusTo(self, el):
        if self.FocusOn != None:
            self.FocusOn.LoseFocus()
        if el != None:
            el.GetFocus()
        self.FocusOn = el
    
    def ButtonAction(self, cmd):
        self.SetFocusTo(None)
    
    def ProcessInput(self):
        if self.FocusOn != None and self.FocusOn.ProcessInput():
            self.FocusOn.UpdateView()
            return True
        else:
            for tmp in self.KeyboardCommands:
                val = True
                for cond in tmp["condition"]:
                    if cond["func"]() != cond["value"]:
                        val = False
                if val:
                    tmp["call"]()
                    return True
        return False
    
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
    def __init__(self, host, parent, node, structure, ego):
        GuiComposite.__init__(self, host, parent, node, structure, ego)
        self.valueDefault = node.GetStrAttr("valueDefault")
        self.value = None
        
    def Activate(self, flag):
        for val in self.Elements.keys():
            self.Elements[val].Activate((val == self.value) and flag)
        
    def UpdateView(self):
        try:
            value = guipresenter.GetData(self.ego+"#value")
            if value != None:
                self.value = value
            else:
                self.value = self.valueDefault
            for val in self.Elements.keys():
                if val == self.value:
                    self.Elements[val].Show(True)
                    self.Elements[val].UpdateView()
                else:
                    self.Elements[val].Show(False)
        except:
            print string.join(apply(traceback.format_exception, sys.exc_info()))

#-------------------------------------
# Activator - тип Варианта
#-------------------------------------
class GuiActivator(GuiComposite):
    def __init__(self, host, parent, node, structure, ego):
        GuiComposite.__init__(self, host, parent, node, structure, ego)
        self.valueDefault = node.GetStrAttr("valueDefault")
        self.value = None
        
    def Activate(self, flag):
        for val in self.Elements.keys():
            self.Elements[val].Show(val == str(flag))
            self.Elements[val].Activate(val == str(flag))
        
    
    
