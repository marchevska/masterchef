#!/usr/bin/env python
# -*- coding: cp1251 -*-

import globalvars
from constants import *
from teggo.games import localizer

def ShowMenu(*a):
    globalvars.GuiPresenter.data["MainMenu.Play#action"] = PlayGame
    globalvars.GuiPresenter.data["MainMenu.Players#action"] = ShowPlayers
    globalvars.GuiPresenter.data["MainMenu.Options#action"] = ShowOptions
    globalvars.GuiPresenter.data["MainMenu.Rules#action"] = ShowRules
    globalvars.GuiPresenter.data["MainMenu.Hiscores#action"] = ShowHiscoresDialog
    globalvars.GuiPresenter.data["MainMenu.Quit#action"] = QuitGame

    #���� � ������ �� �������� �� ���� ������, �� ���������� ����� ����������
    tmpUnlockedSettings = filter(lambda x: \
                            globalvars.CurrentPlayer.GetLevelParams(x).GetBoolAttr("unlocked"),
                            eval(globalvars.GameSettings.GetStrAttr("settings")))
    if tmpUnlockedSettings == []:
        globalvars.GuiPresenter.data["MainMenu.Cookbook#disabled"] = True
    else:
        globalvars.GuiPresenter.data["MainMenu.Cookbook#action"] = ShowCookbook

    #��������
    tmpDevLogoInfo = globalvars.BrandingInfo.GetTag("smallDevLogo")
    globalvars.GuiPresenter.data["MainMenu.DevLogoSmall#klass"] = tmpDevLogoInfo.GetStrAttr("klass")
    globalvars.GuiPresenter.data["MainMenu.DevLogoSmall#x"] = tmpDevLogoInfo.GetIntAttr("x")
    globalvars.GuiPresenter.data["MainMenu.DevLogoSmall#y"] = tmpDevLogoInfo.GetIntAttr("y")
    tmpPubLogoInfo = globalvars.BrandingInfo.GetTag("smallPubLogo")
    if tmpPubLogoInfo.GetStrAttr("klass") != "$spritecraft$dummy$":
        oE.SstDefKlass("publisher-logo-small", globalvars.BrandingInfo.GetSubtag("publisher-logo-small"))
        globalvars.GuiPresenter.data["MainMenu.PubLogoSmall#klass"] = tmpPubLogoInfo.GetStrAttr("klass")
        globalvars.GuiPresenter.data["MainMenu.PubLogoSmall#x"] = tmpPubLogoInfo.GetIntAttr("x")
        globalvars.GuiPresenter.data["MainMenu.PubLogoSmall#y"] = tmpPubLogoInfo.GetIntAttr("y")

    globalvars.GuiPresenter.data["MainMenu.VersionNumber#text"] = \
                localizer.GetGameString("Str_Menu_Version")+globalvars.BuildInfo.GetStrAttr("buildNo")
    if globalvars.GameConfig.GetStrAttr("Player") == "":
        globalvars.GuiPresenter.data["MainMenu.WelcomeMessage#text"] = ""
        globalvars.GuiPresenter.data["MainMenu.WelcomeName#text"] = ""
        if len(globalvars.PlayerList.GetPlayerList()) <= 1:
            ShowEnterNameDialog()
        else:
            ShowPlayers()
    else:
        globalvars.GuiPresenter.data["MainMenu.WelcomeMessage#text"] = localizer.GetGameString("Str_Menu_Welcome")
        globalvars.GuiPresenter.data["MainMenu.WelcomeName#text"] = globalvars.GameConfig.GetStrAttr("Player")
        globalvars.GuiPresenter.ShowDialog("MainMenu", True)
        globalvars.GuiPresenter.BringToFront("MainMenu", True)

    
def ShowOptions(*a):
    pass

def ShowRules(*a):
    pass

def ShowCookbook(*a):
    pass

def ShowHelp(*a):
    pass

def ShowHiscoresDialog(*a):
    tmpHiscoreTags = map(lambda x: x.GetContent(), globalvars.Hiscores.Tags())
    tmpAllEpisodes = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Episodes").Tags("episode"))
    for i in range(len(tmpHiscoreTags)):
        if tmpHiscoreTags[i] in tmpAllEpisodes:
            if globalvars.CurrentPlayer.GetLevelParams(tmpHiscoreTags[i]).GetBoolAttr("unlocked"):
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Logo#frno"] = 2*i
            else:
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Logo#frno"] = 2*i+1
        
        tmpTagScores = map(lambda x: (x.GetContent() ,x.GetStrAttr("score")),
                    globalvars.Hiscores.GetSubtag(tmpHiscoreTags[i]).Tags())
        for j in range(5):
            if j < len(tmpTagScores):
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#text"] = tmpTagScores[j][0]
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#text"] = tmpTagScores[j][1]
            else:
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#text"] = localizer.GetGameString("Str_Hiscores_EmptyPlayer")
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#text"] = ""
            if globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#text"] == globalvars.GameConfig.GetStrAttr("Player"):
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#cfilt"] = CFilt_HiscoreCurrentPlayer
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#cfilt"] = CFilt_HiscoreCurrentPlayer
            else:
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#cfilt"] = CFilt_HiscoreOther
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#cfilt"] = CFilt_HiscoreOther

    globalvars.GuiPresenter.ShowDialog("Hiscores", True)
    globalvars.GuiPresenter.BringToFront("Hiscores", True)
    
def ShowPlayers(*a):
    pass

def ShowEnterNameDialog(*a):
    pass

def QuitGame(*a):
    pass

def PlayGame(*a):
    pass

def SetPause(flag):
    #globalvars.GuiPresenter.data["Pause.Unpause#action"] = UnSetPause
    #globalvars.GuiPresenter.data["Pause.Text1#text"] = ""
    globalvars.GuiPresenter.ShowDialog("Pause", flag)
    globalvars.GuiPresenter.BringToFront("Pause", flag)
        
    #if flag:
        #if globalvars.StateStack[-1] in (PState_YesNo, PState_YesNoCancel, PState_EnterName):
            #globalvars.GuiPresenter.ShowDialog("Pause", flag)
            #globalvars.GuiPresenter.BringToFront("Pause", flag)
            #self._ReleaseState(globalvars.StateStack[-1])
            #self.LastQuestion = ""
        #if globalvars.StateStack[-1] in (PState_Hints,):
        #    self._ReleaseState(globalvars.StateStack[-1])
        #self._SetState(PState_Pause)
    #globalvars.Musician.SetPause(flag)

