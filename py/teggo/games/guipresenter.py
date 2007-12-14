import string, sys, traceback

import scraft
from scraft import engine as oE

from guibutton import PushButton
from guiimage import Image
from guitext import TextLabel
from guicomposite import GuiComposite, GuiDialog

import guiaux
import localizer

class GuiPresenter:
    def __init__(self, filename):
        self.DefData = oE.ParseDEF(filename)
        self.data = {}
        
        #parse object styles if necessary
        
        self.Dialogs = {}
        for tmp in self.DefData.GetTag("Objects").Tags("Dialog"):
            self.CreateDialog(tmp.GetContent())
        for tmp in self.Dialogs.values():
            tmp.Show(False)
        self.DialogsStack = []
        
    def CreateDialog(self, name):
        self.Dialogs[name] = GuiDialog(self.DefData.GetTag("Objects").GetSubtag(name, "Dialog"), name, self)
        
        
    def CreateObject(self, host, parent, node, name):
        tmpTagName = node.GetName()
        if _StrCompNoCase(tmpTagName, "Image"):
            el = Image(host, parent, node, name)
        elif _StrCompNoCase(tmpTagName, "PushButton"):
            el = PushButton(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif _StrCompNoCase(tmpTagName, "TextLabel"):
            el = TextLabel(host, parent, node, self.DefData.GetTag("Styles"), name)
        elif self.DefData.GetTag("Objects").GetSubtagNocase(tmpTagName) != None:
            el = GuiComposite(host, parent, node, self.DefData.GetTag("Objects").GetSubtagNocase(tmpTagName), name, self)
        else:
            el = None
        return el
        
    def ShowDialog(self, name, flag):
        if flag:
            if not(self.DialogsStack != [] and self.DialogsStack[-1] == name):
                self.DialogsStack.append(name)
            self.Dialogs[name].Show(True)
            self.Dialogs[name].UpdateView(self.data)
        else:
            self.Dialogs[name].Show(False)
            if self.DialogsStack != [] and self.DialogsStack[-1] == name:
                self.DialogsStack.pop()
                if self.DialogsStack != []:
                    self.ShowDialog(self.DialogsStack[-1], True)
                    self.BringToFront(self.DialogsStack[-1], True)
        
    def BringToFront(self, name, flag):
        tmpOtherDialogs = self.Dialogs.keys()
        tmpOtherDialogs.remove(name)
        for tmp in tmpOtherDialogs:
            self.Dialogs[tmp].Activate(False)
        self.Dialogs[name].Activate(flag)
    
    
def _StrCompNoCase(str1, str2):
    return (string.lower(str1) == string.lower(str2))

    