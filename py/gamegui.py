#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

import globalvars
import config
from constants import *
from teggo.games import localizer
from teggo.games import guipresenter
from teggo.games import fxmanager

#------------------------------
# используется для однократного вызова диспетчером одной функции
#------------------------------
class RunCMD(scraft.Dispatcher):
    def __init__(self, func):
        self.func = func
    def _OnExecute(self, que):
        self.func()
        return scraft.CommandStateEnd

def InitGUI(*a):
    globalvars.GuiPresenter = guipresenter.GuiPresenter("def/gui.def")
    globalvars.GuiQueue = oE.executor.CreateQueue()

def RaiseEvent():
    globalvars.GuiPresenter.RaiseEvent()

#------------------------------
# показ логотипов
#------------------------------

def ShowLogoSequence(*a):
    if globalvars.BrandingInfo.GetBoolAttr("pubLogo"):
        ShowPubLogo()
    else:
        ShowDevLogo()

def ShowPubLogo(*a):
    globalvars.GuiQueue.ScheduleSleep(3000)
    globalvars.GuiQueue.Schedule(RunCMD(ClosePubLogo))
    oE.SstDefKlass("publisher-logo", globalvars.BrandingInfo.GetSubtag("publisher-logo"))
    globalvars.GuiPresenter.data["PubLogo.Background#klass"] = "publisher-logo"
    if globalvars.BrandingInfo.HasAttr("background"):
        oE.background.color = eval(globalvars.BrandingInfo.GetStrAttr("background"))
    globalvars.GuiPresenter.data["PubLogo.Close#action"] = ClosePubLogo
    globalvars.GuiPresenter.data["PubLogo#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": ClosePubLogo },
        ]
    globalvars.GuiPresenter.ShowDialog("PubLogo", True)

def ClosePubLogo(*a):
    globalvars.GuiQueue.Clear()
    globalvars.GuiPresenter.ShowDialog("PubLogo", False)
    ShowDevLogo()

def ShowDevLogo(*a):
    globalvars.GuiQueue.ScheduleSleep(3000)
    globalvars.GuiQueue.Schedule(RunCMD(CloseDevLogo))
    globalvars.GuiPresenter.data["DevLogo.Close#action"] = CloseDevLogo
    globalvars.GuiPresenter.data["DevLogo#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseDevLogo },
        ]
    globalvars.GuiPresenter.ShowDialog("DevLogo", True)

def CloseDevLogo(*a):
    globalvars.GuiQueue.Clear()
    globalvars.GuiPresenter.ShowDialog("DevLogo", False)
    ShowMenu()

#------------------------------
# отображение главного меню        
#------------------------------

def ShowMenu(*a):
    globalvars.GuiPresenter.data["MainMenu.PlayCareer#action"] = NextCareerStage
    globalvars.GuiPresenter.data["MainMenu.Players#action"] = ShowPlayers
    globalvars.GuiPresenter.data["MainMenu.Options#action"] = ShowOptionsFromMenu
    globalvars.GuiPresenter.data["MainMenu.Rules#action"] = ShowRules
    globalvars.GuiPresenter.data["MainMenu.Hiscores#action"] = ShowHiscoresDialog
    globalvars.GuiPresenter.data["MainMenu.Quit#action"] = AskForQuitGame
    globalvars.GuiPresenter.data["MainMenu#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": AskForQuitGame }
        ]

    #если у игрока не разлочен ни один эпизод, то кулинарная книга недоступна
    tmpUnlockedSettings = filter(lambda x: \
                            globalvars.CurrentPlayer.GetLevelParams(x).GetBoolAttr("unlocked"),
                            eval(globalvars.GameSettings.GetStrAttr("settings")))
    if tmpUnlockedSettings == []:
        globalvars.GuiPresenter.data["MainMenu.Cookbook#disabled"] = True
    else:
        globalvars.GuiPresenter.data["MainMenu.Cookbook#disabled"] = False
        globalvars.GuiPresenter.data["MainMenu.Cookbook#action"] = ShowCookbook

    #брендинг
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

def AskForQuitGame(*a):
    Ask(localizer.GetGameString("Str_Question_ExitGame"), QuitGame)
    
def QuitGame(*a):
    globalvars.ExitFlag = True

#------------------------------
# опции - показ и редактирование
#------------------------------

def ShowOptionsFromMenu(*a):
    globalvars.GuiPresenter.data["Options.Buttons#value"] = "Menu"
    globalvars.GuiPresenter.data["Options.Buttons.Menu.Ok#action"] = CloseOptions
    globalvars.GuiPresenter.data["Options#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseOptions },
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": CloseOptions },
        ]
    ShowOptions()
    
def ShowOptions(*a):
    globalvars.GuiPresenter.data["Options.Sound#value"] = globalvars.GameConfig.GetIntAttr("Sound")
    globalvars.GuiPresenter.data["Options.Sound#onModify"] = UpdateSoundVolume
    globalvars.GuiPresenter.data["Options.Music#value"] = globalvars.GameConfig.GetIntAttr("Music")
    globalvars.GuiPresenter.data["Options.Music#onModify"] = UpdateMusicVolume

    globalvars.GuiPresenter.data["Options.Mute#checked"] = globalvars.GameConfig.GetBoolAttr("Mute")
    globalvars.GuiPresenter.data["Options.Hints#checked"] = globalvars.CurrentPlayer.XML.GetBoolAttr("Hints")
    globalvars.GuiPresenter.data["Options.Fullscreen#checked"] = globalvars.GameConfig.GetBoolAttr("Fullscreen")
    globalvars.GuiPresenter.ShowDialog("Options", True)

#close and apply options
def CloseOptions(*a):
    globalvars.GameConfig.SetBoolAttr("Fullscreen", globalvars.GuiPresenter.data["Options.Fullscreen#checked"])
    globalvars.GameConfig.SetBoolAttr("Mute", globalvars.GuiPresenter.data["Options.Mute#checked"])
    globalvars.CurrentPlayer.XML.SetBoolAttr("Hints", globalvars.GuiPresenter.data["Options.Hints#checked"])
    globalvars.CurrentPlayer.Save()
    config.ApplyOptions()
    globalvars.GuiPresenter.ShowDialog("Options", False)
    
def ShowOptionsFromGame(*a):    
    globalvars.Board.Freeze(True)
    globalvars.GuiPresenter.data["Options.Buttons#value"] = "Game"
    globalvars.GuiPresenter.data["Options.Buttons.Game.Resume#action"] = CloseOptionsAndResumeGame
    globalvars.GuiPresenter.data["Options.Buttons.Game.Restart#action"] = RestartGameFromOptions
    globalvars.GuiPresenter.data["Options.Buttons.Game.EndGame#action"] = ExitFromGameToMenu
    globalvars.GuiPresenter.data["Options#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseOptionsAndResumeGame },
        ]
    ShowOptions()
    
def CloseOptionsAndResumeGame(*a):
    CloseOptions()
    globalvars.Board.Freeze(False)

def RestartGameFromOptions(*a):
    Ask(localizer.GetGameString("Str_Question_RestartLevel"), RestartGame)

def RestartGame(*a):
    CloseOptions()
    PlayLevel()
    
def ExitFromGameToMenu(*a):
    CloseOptions()
    globalvars.Board.Freeze(True)
    globalvars.Board.Clear()
    globalvars.Board.Show(False)
    globalvars.GuiPresenter.ShowDialog("GameHUD", False)
    ShowMenu()
    
def UpdateSoundVolume(*a):
    globalvars.GameConfig.SetIntAttr("Sound", a[0])
    config.ApplyOptions()
    
def UpdateMusicVolume(*a):
    globalvars.GameConfig.SetIntAttr("Music", a[0])
    config.ApplyOptions()
    
#------------------------------
# отображение справки по игре
#------------------------------

def ShowRules(*a):
    try:
        if not globalvars.GuiPresenter.data.get("Rules#page"):
            globalvars.GuiPresenter.data["Rules#page"] = 0
        globalvars.GuiPresenter.data["Rules.Background#klass"] = "help-page"+str(globalvars.GuiPresenter.data["Rules#page"]+1)
        if globalvars.GuiPresenter.data["Rules#page"] == 0:
            globalvars.GuiPresenter.data["Rules.Prev#disabled"] = True
        else:
            globalvars.GuiPresenter.data["Rules.Prev#disabled"] = False
            globalvars.GuiPresenter.data["Rules.Prev#action"] = RulesPrevPage
        if globalvars.GuiPresenter.data["Rules#page"] == globalvars.GuiPresenter.data.get("Rules#TotalHelpPages") - 1:
            globalvars.GuiPresenter.data["Rules.Next#disabled"] = True
        else:
            globalvars.GuiPresenter.data["Rules.Next#disabled"] = False
            globalvars.GuiPresenter.data["Rules.Next#action"] = RulesNextPage
        globalvars.GuiPresenter.data["Rules.Close#action"] = CloseRules
        globalvars.GuiPresenter.data["Rules#kbdCommands"] = [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseRules },
        ]
        globalvars.GuiPresenter.ShowDialog("Rules", True)
    except:
        pass

def RulesPrevPage(*a):
    try:
        if globalvars.GuiPresenter.data["Rules#page"] > 0:
            globalvars.GuiPresenter.data["Rules#page"] -= 1
    except:
        pass
    ShowRules()

def RulesNextPage(*a):
    try:
        if globalvars.GuiPresenter.data["Rules#page"] < globalvars.GuiPresenter.data.get("Rules#TotalHelpPages") - 1:
            globalvars.GuiPresenter.data["Rules#page"] += 1
    except:
        pass
    ShowRules()

def CloseRules(*a):
    globalvars.GuiPresenter.ShowDialog("Rules", False)
    

#------------------------------
# кулинарная книга
#------------------------------

def ShowCookbook(*a):
    try:
        globalvars.GuiPresenter.data["Cookbook#from"] = a[0]
        if not globalvars.GuiPresenter.data.get("Cookbook#page"):
            globalvars.GuiPresenter.data["Cookbook#page"] = 0
        #коррекция в случае переключения на другой профиль игрока:
        #не показывать не разлоченные страницы книги
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
        #no - номер страницы книги
        no = globalvars.GuiPresenter.data["Cookbook#page"]
        while not globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no]).GetBoolAttr("unlocked") and no>0:
            no -= 1
        tmpSetting = tmpAllSettings[no]
        globalvars.GuiPresenter.data["Cookbook#page"] = no
        
        #нарисовать страницу сеттинга
        globalvars.GuiPresenter.data["Cookbook.Background#klass"] = globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("background")
        globalvars.GuiPresenter.data["Cookbook.Logo#klass"] = globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("logo")
        
        #проверить рецепты: известные или нет, новые или старые
        tmpRecipes = filter(lambda x: globalvars.RecipeInfo.GetSubtag(x).GetStrAttr("setting") == tmpSetting,
                                map(lambda x: x.GetContent(), globalvars.RecipeInfo.Tags()))
        tmpNewRecipes = globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting)
        if len(tmpNewRecipes) > 0:
            if globalvars.GuiPresenter.data.get("Cookbook#EffectsLayer") != None:
                layer = globalvars.GuiPresenter.data["Cookbook#EffectsLayer"]
            else:
                layer = globalvars.GuiPresenter.DefData.GetTag("Objects").GetSubtag("Cookbook").GetIntAttr("layer")
            if globalvars.GuiPresenter.data.get("Cookbook#EffectsSublayer") != None:
                sublayer = globalvars.GuiPresenter.data["Cookbook#EffectsSublayer"]
            else:
                sublayer = 0
            globalvars.GuiPresenter.Dialogs["Cookbook"].AttachEffect(\
                fxmanager.CreateEffect(globalvars.GuiPresenter.Dialogs["Cookbook"],
                "Popup.Game.GoalReached", { "text": (localizer.GetGameString("Str_NewRecipesLearned")),
                "crd": (400, 300), "layer": layer, "sublayer": sublayer }))
            
        for i in range(globalvars.GuiPresenter.data["Cookbook#MaxRecipesOnPage"]):
            recipeCrd = (globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeX"), globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeY"))
            globalvars.GuiPresenter.data["Cookbook.Recipe" + str(i+1) + "#x"] = recipeCrd[0]
            globalvars.GuiPresenter.data["Cookbook.Recipe" + str(i+1) + "#y"] = recipeCrd[1]
            if globalvars.CurrentPlayer.GetLevelParams(tmpRecipes[i]).GetBoolAttr("unlocked"):
                globalvars.GuiPresenter.data["Cookbook.Recipe" + str(i+1) + "#klass"] = globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("badge")
                if tmpRecipes[i] in tmpNewRecipes:
                    globalvars.CurrentPlayer.SetLevelParams(tmpRecipes[i], { "seen": True })
                    globalvars.GuiPresenter.Dialogs["Cookbook"].AttachEffect(\
                            fxmanager.CreateEffect(globalvars.GuiPresenter.Dialogs["Cookbook"],
                            "Trail.CookbookNewRecipe", { "crd": recipeCrd }))
            else:
                globalvars.GuiPresenter.data["Cookbook.Recipe" + str(i+1) + "#klass"] = globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("emptyBadge")
        
        #кнопки пролистывания ниги
        #если книга открыта из главного меню
        if string.find(str(a[0]), "MainMenu") >= 0:
            globalvars.GuiPresenter.data["Cookbook.Continue#hidden"] = True
            globalvars.GuiPresenter.data["Cookbook.Close#disabled"] = False
            
            globalvars.GuiPresenter.data["Cookbook.Prev#hidden"] = not(no>0)
            if no>0:
                globalvars.GuiPresenter.data["Cookbook.Prev#disabled"] = \
                        not(globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no-1]).GetBoolAttr("unlocked"))
            
            globalvars.GuiPresenter.data["Cookbook.Next#hidden"] = not(no<len(tmpAllSettings)-1)
            if no<len(tmpAllSettings)-1:
                globalvars.GuiPresenter.data["Cookbook.Next#disabled"] = \
                        not(globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no+1]).GetBoolAttr("unlocked"))
                
        #иначе - книга открыта после прохождения уровня
        else:
            globalvars.GuiPresenter.data["Cookbook.Close#disabled"] = True
            globalvars.GuiPresenter.data["Cookbook.Continue#hidden"] = False
            globalvars.GuiPresenter.data["Cookbook.Prev#hidden"] = True
            globalvars.GuiPresenter.data["Cookbook.Next#hidden"] = True
        
        globalvars.GuiPresenter.data["Cookbook.Prev#action"] = CookbookPrevPage
        globalvars.GuiPresenter.data["Cookbook.Next#action"] = CookbookNextPage
        globalvars.GuiPresenter.data["Cookbook.Close#action"] = CloseCookbook
        globalvars.GuiPresenter.data["Cookbook.Continue#action"] = CloseCookbook
        globalvars.GuiPresenter.data["Cookbook#kbdCommands"] = [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseCookbook },
        ]
        globalvars.GuiPresenter.ShowDialog("Cookbook", True)
    except:
        print string.join(apply(traceback.format_exception, sys.exc_info()))

def CookbookPrevPage(*a):
    try:
        globalvars.GuiPresenter.data["Cookbook#page"] -= 1
    except:
        pass
    ShowCookbook(globalvars.GuiPresenter.data["Cookbook#from"])

def CookbookNextPage(*a):
    try:
        globalvars.GuiPresenter.data["Cookbook#page"] += 1
    except:
        pass
    ShowCookbook(globalvars.GuiPresenter.data["Cookbook#from"])

def CloseCookbook(*a):
    globalvars.GuiPresenter.ShowDialog("Cookbook", False)
    if string.find(str(globalvars.GuiPresenter.data["Cookbook#from"]), "LevelResults") >= 0:
        globalvars.GuiPresenter.ShowDialog("GameHUD", False)
        globalvars.Board.Clear()
        globalvars.Board.Show(False)
        NextCareerStage()

#------------------------------
# отображение рекордов
# данные считываются из файла
#------------------------------

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
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#style"] = \
                        globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("TextLabel.Hiscore.Player.CurrentPlayer")
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#style"] = \
                        globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("TextLabel.Hiscore.Score.CurrentPlayer")
            else:
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#style"] = \
                        globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("TextLabel.Hiscore.Player")
                globalvars.GuiPresenter.data["Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#style"] = \
                        globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("TextLabel.Hiscore.Score")

    globalvars.GuiPresenter.data["Hiscores#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseHiscores },
        ]
    globalvars.GuiPresenter.data["Hiscores.HiscoresClose#action"] = CloseHiscores
    globalvars.GuiPresenter.data["Hiscores.HiscoresReset#action"] = AskForClear
    globalvars.GuiPresenter.ShowDialog("Hiscores", True)

def CloseHiscores(*a):
    globalvars.GuiPresenter.ShowDialog("Hiscores", False)
    
def AskForClear(*a):
    Ask(localizer.GetGameString("Str_Question_ClearHiscores"), ClearHiscores)
    
def ClearHiscores(*a):
    config.ClearHiscores()
    ShowHiscoresDialog()
    
#------------------------------
# список игроков
#------------------------------

def ShowPlayers(*a):
    globalvars.GuiPresenter.data["Players.List#Values"] = globalvars.PlayerList.GetPlayerList()
    if not globalvars.GuiPresenter.data.get("Players.List#first"):
        globalvars.GuiPresenter.data["Players.List#first"] = 0
    if not globalvars.GuiPresenter.data.get("Players.List#Selected"):
        globalvars.GuiPresenter.data["Players.List#Selected"] = []
    
    #прокрутка списка при открытии диалога
    tmpList = globalvars.PlayerList.GetPlayerList()
    tmpFirstPlayer = 0
    if globalvars.GuiPresenter.data["Players.List#Selected"] != []:
        tmpSelectedPlayer = tmpList[globalvars.GuiPresenter.data["Players.List#Selected"][0]]
    else:
        tmpSelectedPlayer = ""
    if globalvars.GameConfig.GetStrAttr("Player") != "":
        tmpName = globalvars.GameConfig.GetStrAttr("Player")
        if tmpSelectedPlayer == "":
            tmpSelectedPlayer = tmpName
    if tmpList.count(tmpSelectedPlayer) > 0:
        tmpInd = tmpList.index(tmpSelectedPlayer)
        globalvars.GuiPresenter.data["Players.List#Selected"] = [tmpInd]
        if tmpInd < globalvars.GuiPresenter.data["Players.List#height"]:
            tmpFirstPlayer = 0
        else:
            tmpFirstPlayer = tmpInd - globalvars.GuiPresenter.data["Players.List#height"]+1
    else:
        if tmpFirstPlayer + globalvars.GuiPresenter.data["Players.List#height"] > len(tmpList):
            tmpFirstPlayer = max(tmpFirstPlayer-1, 0)
        else:
            tmpFirstPlayer = 0

    globalvars.GuiPresenter.data["Players.List#first"] = tmpFirstPlayer
    globalvars.GuiPresenter.data["Players.List#action"] = UpdatePlayersButtons
    
    globalvars.GuiPresenter.data["Players.New#action"] = ShowEnterNameDialog
    globalvars.GuiPresenter.data["Players.Remove#action"] = AskForRemovingPlayer
    globalvars.GuiPresenter.data["Players.Ok#action"] = SelectPlayer
    globalvars.GuiPresenter.data["Players.Close#action"] = ClosePlayers
    UpdatePlayersButtons()
    globalvars.GuiPresenter.ShowDialog("MainMenu", True)
    globalvars.GuiPresenter.ShowDialog("Players", True)

def UpdatePlayersButtons(*a):
    globalvars.GuiPresenter.data["Players.Ok#disabled"] = (globalvars.GuiPresenter.data["Players.List#Selected"] == [])
    globalvars.GuiPresenter.data["Players.Remove#disabled"] = (globalvars.GuiPresenter.data["Players.List#Selected"] == [])
    globalvars.GuiPresenter.data["Players.Close#disabled"] = (globalvars.GameConfig.GetStrAttr("Player") == "")
    globalvars.GuiPresenter.data["Players#kbdCommands"] = \
        [{ "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ClosePlayers }]*(not globalvars.GuiPresenter.data["Players.Close#disabled"]) + \
        [{ "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": SelectPlayer }]*(not globalvars.GuiPresenter.data["Players.Ok#disabled"])
    globalvars.GuiPresenter.ShowDialog("Players", True)

def ClosePlayers(*a):
    globalvars.GuiPresenter.ShowDialog("Players", False)
    
def SelectPlayer(*a):
    if len(globalvars.GuiPresenter.data["Players.List#Selected"]) == 1:
        globalvars.PlayerList.SelectPlayer(globalvars.PlayerList.GetPlayerList()[globalvars.GuiPresenter.data["Players.List#Selected"][0]])
        globalvars.GuiPresenter.ShowDialog("Players", False)
        ShowMenu()

def AskForRemovingPlayer(*a):
    Ask(localizer.GetGameString("Str_Question_RemovePlayer"), RemovePlayer)
    
def RemovePlayer(*a):
    try:
        tmpPlayer = globalvars.PlayerList.GetPlayerList()[globalvars.GuiPresenter.data["Players.List#Selected"][0]]
        globalvars.PlayerList.DelPlayer(tmpPlayer)
    except:
        pass
    globalvars.GuiPresenter.data["Players.List#Selected"] = []
    ShowPlayers()

#------------------------------
# новый игрок - ввод имени
#------------------------------

def ShowEnterNameDialog(*a):
    if not globalvars.GuiPresenter.data.get("EnterName.NewPlayerName#text"):
        globalvars.GuiPresenter.data["EnterName.NewPlayerName#text"] = ""
    if not globalvars.GuiPresenter.data.get("EnterName.ErrorMessage#text"):
        globalvars.GuiPresenter.data["EnterName.ErrorMessage#text"] = ""
    globalvars.GuiPresenter.data["EnterName.NewPlayerName#onUpdate"] = UpdateNameEntry
    globalvars.GuiPresenter.data["EnterName.Ok#action"] = CreateNewPlayerOk
    globalvars.GuiPresenter.data["EnterName.Cancel#action"] = CloseEnterNameDialog
    globalvars.GuiPresenter.data["EnterName#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseEnterNameDialog },
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": CreateNewPlayerOk },
        ]
    globalvars.GuiPresenter.ShowDialog("EnterName", True)

def CheckNameErrors(*a):
    tmpErrorMessage = ""
    tmpName = globalvars.GuiPresenter.data["EnterName.NewPlayerName#text"]
    if len(tmpName) == 0:
        tmpErrorMessage = localizer.GetGameString("Str_EnterName_Error_Empty")
    elif tmpName == 'None':
        tmpErrorMessage = localizer.GetGameString("Str_EnterName_Error_Bad")
    elif globalvars.PlayerList.GetPlayerList().count(tmpName) > 0:
        tmpErrorMessage = localizer.GetGameString("Str_EnterName_Error_Exist")
    globalvars.GuiPresenter.data["EnterName.ErrorMessage#text"] = tmpErrorMessage
    #if tmpErrorMessage != "":
    #    globalvars.GuiPresenter.ShowDialog("EnterName", True)
    globalvars.GuiPresenter.ShowDialog("EnterName", True)

def UpdateNameEntry(*a):
    if globalvars.GuiPresenter.data["EnterName.ErrorMessage#text"] != "":
        #CheckNameErrors()
        globalvars.GuiPresenter.data["EnterName.ErrorMessage#text"] = ""
        globalvars.GuiPresenter.ShowDialog("EnterName", True)

def CreateNewPlayerOk(*a):
    CheckNameErrors()
    if globalvars.GuiPresenter.data["EnterName.ErrorMessage#text"] == "":
        globalvars.PlayerList.CreatePlayer(globalvars.GuiPresenter.data["EnterName.NewPlayerName#text"])
        globalvars.GuiPresenter.data["Players.List#Selected"] = [len(globalvars.PlayerList.GetPlayerList())-1]
        CloseEnterNameDialog()

def CloseEnterNameDialog(*a):
    globalvars.GuiPresenter.data["EnterName.NewPlayerName#text"] = ""
    globalvars.GuiPresenter.data["EnterName.ErrorMessage#text"] = ""
    globalvars.GuiPresenter.ShowDialog("EnterName", False)
    ShowPlayers()

#------------------------------
# управление ходом игры в карьерном режиме
#------------------------------

def NextCareerStage(*a):
    newLevel = globalvars.CurrentPlayer.GetNextLevelInsight()
    if newLevel != None:
        globalvars.CurrentPlayer.GotoYourNextLevel()
        if newLevel.GetName() == "comic":
            ShowComics()
        elif newLevel.GetName() == "outro":
            ShowEpisodeOutro()
        elif newLevel.GetName() == "intro":
            ShowEpisodeIntro()
        else:
            PlayLevel()
    else:
        ShowMap()   
    
    pass
    #try:
    #    #проходим по списку уровней и находим последний разлоченный
    #    tmpAllUnlocked = filter(lambda x: globalvars.CurrentPlayer.GetLevelParams(x.GetContent()).GetBoolAttr("unlocked"),
    #                                globalvars.LevelProgress.GetTag("Levels").Tags())
    #    tmpLastUnlocked = tmpAllUnlocked[-1]
    #    tmpNoUnlockedLevels = len(filter(lambda x: x.GetName() == "level", tmpAllUnlocked))
    #    tmpNewUnlocked = globalvars.CurrentPlayer.NewUnlockedLevel() #str
    #        
    #    #результаты эпизода
    #    if tmpNewUnlocked != "" and \
    #            globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewUnlocked).GetName() == "outro":
    #        globalvars.CurrentPlayer.PopNewUnlockedLevel()
    #        globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewUnlocked))
    #        ShowEpisodeOutro()
    #    #если последний разлоченный - комикс, то показать комикс
    #    elif tmpLastUnlocked.GetName() == "comic":
    #        #если это последний комикс, и его уже видели - показать опять карту
    #        if not tmpLastUnlocked.Next() and \
    #                globalvars.CurrentPlayer.GetLevelParams(tmpLastUnlocked.GetContent()).GetBoolAttr("seen"):
    #            ShowMap()
    #        else:
    #            globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
    #            ShowComics()
    #    #вводная страница эпизода
    #    elif tmpLastUnlocked.GetName() == "intro":
    #        globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
    #        ShowEpisodeIntro()
    #    #иначе: смотрим количество разлоченных уровней
    #    #если больше 1, то показываем карту
    #    elif tmpNoUnlockedLevels > 1:
    #        ShowMap()
    #    #иначе запускаем первый уровень
    #    else:
    #        globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
    #        PlayLevel()
    #except:
    #    oE.Log("Next stage fatal error")
    #    oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
    #    sys.exit()
    
#------------------------------
# карта
#------------------------------

#сброс выделения на карте в случае смены игрока
def ResetMapSelection(*a):
    globalvars.GuiPresenter.data["MapCareer.Levels#Selected"] = []
    tmpOutros = list(globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
    for i in range(len(tmpOutros)):
        globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#selected"] = False
    tmpLevels = list(globalvars.LevelProgress.GetTag("Levels").Tags("level"))
    for i in range(len(tmpLevels)):
        globalvars.GuiPresenter.data["MapCareer.Levels.Level"+str(i+1)+"#selected"] = False
    
def ShowMap(*a):
    #нарисовать картинки эпизодов
    tmpEpisodes = list(globalvars.LevelProgress.GetTag("Episodes").Tags("episode"))
    for i in range(len(tmpEpisodes)):
        globalvars.GuiPresenter.data["MapCareer.Episode"+str(i)+"#klass"] = tmpEpisodes[i].GetStrAttr("image")
        globalvars.GuiPresenter.data["MapCareer.Episode"+str(i)+"#x"] = tmpEpisodes[i].GetIntAttr("x")
        globalvars.GuiPresenter.data["MapCareer.Episode"+str(i)+"#y"] = tmpEpisodes[i].GetIntAttr("y")
        if globalvars.CurrentPlayer.GetLevelParams(tmpEpisodes[i].GetContent()).GetBoolAttr("unlocked"):
            globalvars.GuiPresenter.data["MapCareer.Episode"+str(i)+"#frno"] = 0
        else:
            globalvars.GuiPresenter.data["MapCareer.Episode"+str(i)+"#frno"] = 1
                
    #разместить и нарисовать значки outro эпизодов
    tmpOutros = list(globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
    for i in range(len(tmpOutros)):
        globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#x"] = tmpOutros[i].GetIntAttr("x")
        globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#y"] = tmpOutros[i].GetIntAttr("y")
        
        #читаем запись из профиля игрока
        tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(tmpOutros[i].GetContent())
        if tmpPlayerResult.GetBoolAttr("beat1st"):
            globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#style"] = \
                    globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("RadioButton.Episodes.1st")
        elif tmpPlayerResult.GetBoolAttr("beat2nd"):
            globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#style"] = \
                    globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("RadioButton.Episodes.2nd")
        elif tmpPlayerResult.GetBoolAttr("passed"):
            globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#style"] = \
                    globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("RadioButton.Episodes.Pass")
        else:
            globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#style"] = \
                    globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("RadioButton.Episodes")
        globalvars.GuiPresenter.data["MapCareer.Levels.Episode"+str(i+1)+"#disabled"] = \
                not(tmpPlayerResult.GetBoolAttr("unlocked"))
                
    #разместить и нарисовать значки уровней
    tmpLevels = list(globalvars.LevelProgress.GetTag("Levels").Tags("level"))
    for i in range(len(tmpLevels)):
        globalvars.GuiPresenter.data["MapCareer.Levels.Level"+str(i+1)+"#x"] = tmpLevels[i].GetIntAttr("x")
        globalvars.GuiPresenter.data["MapCareer.Levels.Level"+str(i+1)+"#y"] = tmpLevels[i].GetIntAttr("y")
        
        tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(tmpLevels[i].GetContent())
        if tmpPlayerResult.GetBoolAttr("expert"):
            globalvars.GuiPresenter.data["MapCareer.Levels.Level"+str(i+1)+"#style"] = \
                    globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("RadioButton.LevelsExpert")
        else:
            globalvars.GuiPresenter.data["MapCareer.Levels.Level"+str(i+1)+"#style"] = \
                    globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("RadioButton.Levels")
        globalvars.GuiPresenter.data["MapCareer.Levels.Level"+str(i+1)+"#disabled"] = \
                not(tmpPlayerResult.GetBoolAttr("unlocked"))

    globalvars.GuiPresenter.data["MapCareer.Levels#Values"] = map(lambda x: x.GetContent(), tmpLevels+tmpOutros)
    globalvars.GuiPresenter.data["MapCareer.Levels#first"] = 0
    if not globalvars.GuiPresenter.data.get("MapCareer.Levels#Selected"):
        globalvars.GuiPresenter.data["MapCareer.Levels#Selected"] = []

    #если выбран другой игрок, сбросить выделение
    if not globalvars.GuiPresenter.data.get("MapCareer.Levels#Player"):
        globalvars.GuiPresenter.data["MapCareer.Levels#Player"] = ""
    if globalvars.GuiPresenter.data["MapCareer.Levels#Player"] != globalvars.GameConfig.GetStrAttr("Player"):
        globalvars.GuiPresenter.data["MapCareer.Levels#Selected"] = []
    
    #автоматическое выделение последнего разлоченного уровня
    if globalvars.GuiPresenter.data["MapCareer.Levels#Selected"] == []:
        tmpSelectedLevel = ""
    else:
        tmpSelectedLevel = globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]]
    tmpHilightedLevel = ""
    if globalvars.CurrentPlayer.NewUnlockedLevel() != "":
        #globalvars.Musician.PlaySound("map.newlevel")
        tmpHilightedLevel = tmpSelectedLevel = globalvars.CurrentPlayer.NewUnlockedLevel()
        globalvars.CurrentPlayer.PopNewUnlockedLevel()
    if tmpSelectedLevel == "":
        tmpSelectedLevel = globalvars.CurrentPlayer.LastUnlockedLevel()
    if tmpSelectedLevel in globalvars.GuiPresenter.data["MapCareer.Levels#Values"]:
        globalvars.GuiPresenter.data["MapCareer.Levels#Selected"] = [globalvars.GuiPresenter.data["MapCareer.Levels#Values"].index(tmpSelectedLevel)]

    globalvars.GuiPresenter.data["MapCareer.Levels#action"] = UpdateMapTablet
    #globalvars.GuiPresenter.data["MapCareer.Start#action"] = PlayLevelFromMap
    #globalvars.GuiPresenter.data["MapCareer.ViewResults#action"] = ViewResults
    globalvars.GuiPresenter.data["MapCareer.Start#action"] = DoMapSelection
    globalvars.GuiPresenter.data["MapCareer.ViewResults#action"] = DoMapSelection
    globalvars.GuiPresenter.data["MapCareer.Close#action"] = CloseMap
    globalvars.GuiPresenter.data["MapCareer#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseMap },
        ]

    UpdateMapTablet()
    #globalvars.GuiPresenter.ShowDialog("MapCareer", True)

#обновить надписи на табличке
#при смене состояния карты
def UpdateMapTablet(*a):
    tmpSelectedLevels = map(lambda x: globalvars.GuiPresenter.data["MapCareer.Levels#Values"][x],
                            globalvars.GuiPresenter.data["MapCareer.Levels#Selected"])
    if len(tmpSelectedLevels) == 1:
        tmpNewLevel = tmpSelectedLevels[0]
        globalvars.GuiPresenter.data["MapCareer.Levels#SelectedLevel"] = tmpNewLevel
        tmpLevelKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("level"))
        tmpOutroKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
        
        #если выбран уровень 
        if tmpNewLevel in tmpLevelKeys and \
                    globalvars.CurrentPlayer.GetLevelParams(tmpNewLevel).GetBoolAttr("unlocked"):
            globalvars.GuiPresenter.data["MapCareer.ViewResults#hidden"] = True
            globalvars.GuiPresenter.data["MapCareer.Start#hidden"] = False
            globalvars.GuiPresenter.data["MapCareer.Start#disabled"] = False
            
            tmpBest = globalvars.BestResults.GetSubtag(tmpNewLevel)
            if tmpBest.GetIntAttr("hiscore") != 0 and tmpBest.GetStrAttr("player") != "":
                globalvars.GuiPresenter.data["MapCareer.BestResult#text"] = \
                        localizer.GetGameString("Str_MapHiscore") + str(tmpBest.GetIntAttr("hiscore"))
                globalvars.GuiPresenter.data["MapCareer.AchievedBy#text"] = \
                        localizer.GetGameString("Str_MapAchievedBy") + tmpBest.GetStrAttr("player")
            else:
                globalvars.GuiPresenter.data["MapCareer.BestResult#text"] = localizer.GetGameString("Str_MapNoHiscore")
                globalvars.GuiPresenter.data["MapCareer.AchievedBy#text"] = ""
            
            globalvars.GuiPresenter.data["MapCareer.RestaurantTitle#text"] = \
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("restaurant"))
            globalvars.GuiPresenter.data["MapCareer.RestaurantDay#text"] = \
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("day"))
            
        #просмотр результатов уровня
        elif tmpNewLevel in tmpOutroKeys and \
                    globalvars.CurrentPlayer.GetLevelParams(tmpNewLevel).GetBoolAttr("unlocked"):
            globalvars.GuiPresenter.data["MapCareer.ViewResults#hidden"] = False
            globalvars.GuiPresenter.data["MapCareer.Start#hidden"] = True
            globalvars.GuiPresenter.data["MapCareer.BestResult#text"] = ""
            globalvars.GuiPresenter.data["MapCareer.AchievedBy#text"] = ""
            globalvars.GuiPresenter.data["MapCareer.RestaurantTitle#text"] = \
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("restaurant"))
            globalvars.GuiPresenter.data["MapCareer.RestaurantDay#text"] = \
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("day"))
                
    else:
        globalvars.GuiPresenter.data["MapCareer.Levels#SelectedLevel"] = ""
        globalvars.GuiPresenter.data["MapCareer.ViewResults#hidden"] = True
        globalvars.GuiPresenter.data["MapCareer.Start#hidden"] = False
        globalvars.GuiPresenter.data["MapCareer.Start#disabled"] = True
        globalvars.GuiPresenter.data["MapCareer.BestResult#text"] = ""
        globalvars.GuiPresenter.data["MapCareer.AchievedBy#text"] = ""
        globalvars.GuiPresenter.data["MapCareer.RestaurantTitle#text"] = localizer.GetGameString("Str_MapSelect")
        globalvars.GuiPresenter.data["MapCareer.RestaurantDay#text"] = ""
        
    globalvars.GuiPresenter.ShowDialog("MapCareer", True)

def CloseMap(*a):
    globalvars.GuiPresenter.ShowDialog("MapCareer", False)
    ShowMenu()

def DoMapSelection(*a):
    globalvars.GuiPresenter.ShowDialog("MapCareer", False)
    globalvars.CurrentPlayer.SuggestLevel(globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]])
    if globalvars.CurrentPlayer.GetNextLevelInsight() != None:
        NextCareerStage()
    else:
        oE.Log("Level selection fatal error, level %s", globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]])
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()
        

#------------------------------
# комикс 
#------------------------------

def ShowComics(*a):
    globalvars.GuiPresenter.data["Comics.Background#klass"] = globalvars.CurrentPlayer.GetLevel().GetStrAttr("image")
    globalvars.GuiPresenter.data["Comics.Continue#action"] = CloseComics
    globalvars.GuiPresenter.data["Comics.Close#action"] = CloseComics
    globalvars.GuiPresenter.data["Comics#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseComics },
        ]
    globalvars.GuiPresenter.ShowDialog("MainMenu", False)
    globalvars.GuiPresenter.ShowDialog("Comics", True)

def CloseComics(*a):
    globalvars.GuiPresenter.ShowDialog("Comics", False)
    NextCareerStage()

#------------------------------
# начало эпизода
#------------------------------

def ShowEpisodeIntro(*a):
    #globalvars.Musician.PlaySound("episode.intro")
    tmpLevel = globalvars.CurrentPlayer.GetLevel()
    tmpEpisode = tmpLevel.GetStrAttr("episode")
    tmpCharacters = eval(globalvars.LevelProgress.GetTag("People").GetSubtag(tmpEpisode).GetStrAttr("people")).items()
    
    globalvars.GuiPresenter.data["EpisodeIntro.Theme#value"] = tmpEpisode
    
    #draw characters and write down their names
    for i in range(globalvars.GuiPresenter.data["EpisodeIntro#MaxPeopleOnLevel"]):
        if i < len(tmpCharacters):
            globalvars.GuiPresenter.data["EpisodeIntro.Character"+str(i)+"#klass"] = globalvars.CompetitorsInfo.GetSubtag(tmpCharacters[i][0]).GetStrAttr("src")
            globalvars.GuiPresenter.data["EpisodeIntro.Character"+str(i)+"#hotspot"] = "CenterBottom"
            globalvars.GuiPresenter.data["EpisodeIntro.Character"+str(i)+"#x"], globalvars.GuiPresenter.data["EpisodeIntro.Character"+str(i)+"#y"] = tmpCharacters[i][1]["xy"]
            globalvars.GuiPresenter.data["EpisodeIntro.CharacterName"+str(i)+"#text"] = str(i+1)+". " + localizer.GetGameString(tmpCharacters[i][0])
        else:
            globalvars.GuiPresenter.data["EpisodeIntro.Character"+str(i)+"#klass"] = "$spritecraft$dummy$"
            globalvars.GuiPresenter.data["EpisodeIntro.CharacterName"+str(i)+"#text"] = ""
    
    globalvars.GuiPresenter.data["EpisodeIntro.Continue#action"] = CloseEpisodeIntro
    globalvars.GuiPresenter.data["EpisodeIntro.Close#action"] = CloseEpisodeIntro
    globalvars.GuiPresenter.data["EpisodeIntro#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseEpisodeIntro },
        ]
    globalvars.GuiPresenter.ShowDialog("MainMenu", False)
    globalvars.GuiPresenter.ShowDialog("EpisodeIntro", True)
    
def CloseEpisodeIntro(*a):    
    globalvars.GuiPresenter.ShowDialog("EpisodeIntro", False)
    NextCareerStage()
    
#------------------------------
# конец эпизода
#------------------------------

def ShowEpisodeOutro(*a):
    tmpLevel = globalvars.CurrentPlayer.GetLevel()
    tmpEpisode = tmpLevel.GetStrAttr("episode")
    tmp = globalvars.ThemesInfo.GetSubtag(tmpEpisode)
    tmpResults = globalvars.CurrentPlayer.GetScoresPlaceAndCondition()
    
    #if tmpResults["pass"]:
    #    globalvars.Musician.PlaySound("episode.win")
    #else:
    #    globalvars.Musician.PlaySound("episode.lose")
        
    globalvars.GuiPresenter.data["EpisodeOutro.Theme#value"] = tmpEpisode
        
    #display presenter's speech
    tmpSpeechVariant = tmpEpisode + "_" + (tmpResults["pass"])*"Passed" + (1 - tmpResults["pass"])*"Failed"
    globalvars.GuiPresenter.data["EpisodeOutro.OutroSpeech#value"] = tmpSpeechVariant
    globalvars.GuiPresenter.data["EpisodeOutro.OutroSpeech." + tmpSpeechVariant + ".SpeechWinners#text"] = \
                                reduce(lambda x, y: x+y, map(lambda i: \
                                    localizer.GetGameString(tmpResults["scores"][i][0])+\
                                    ", "*(i<tmpLevel.GetIntAttr("PassFurther")-1),
                                    range(tmpLevel.GetIntAttr("PassFurther"))))
    
    #episode winners
    for i in range(globalvars.GuiPresenter.data["EpisodeOutro#MaxPeopleOnLevel"]):
        if i < tmpLevel.GetIntAttr("PassFurther"):
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+"#visible"] = True
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+"#x"], \
                    globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+"#y"] = \
                    Crd_CharOutroPositions[tmpLevel.GetIntAttr("PassFurther")][i]
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+".Character#klass"] = \
                    globalvars.CompetitorsInfo.GetSubtag(tmpResults["scores"][i][0]).GetStrAttr("src")
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+".Medallion#klass"] = tmp.GetStrAttr("winnerSign")
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+".Number#text"] = str(i+1)
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+".Name#text"] = localizer.GetGameString(tmpResults["scores"][i][0])
            
            tmpEffect = fxmanager.CreateEffect(globalvars.GuiPresenter.Dialogs["EpisodeOutro"],
                        "Particles.OutroCharacterStars", Crd_CharOutroPositions[tmpLevel.GetIntAttr("PassFurther")][i])
            globalvars.GuiPresenter.Dialogs["EpisodeOutro"].AttachEffect(tmpEffect)
            
        else:
            globalvars.GuiPresenter.data["EpisodeOutro.Character"+str(i)+"#visible"] = False
    
    for i in range(globalvars.GuiPresenter.data["EpisodeOutro#MaxPeopleOnLevel"]):
        if i < len(tmpResults["scores"]):
            tmpTextStyleName = globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag(\
                        "TextLabel.EpisodeOutro." + (i == tmpResults["place"]-1)*"Jenny" + \
                        (1 - (i == tmpResults["place"]-1))*"Names" + "." + \
                        (i >= tmpLevel.GetIntAttr("PassFurther"))*"Not" + "Passed")
            globalvars.GuiPresenter.data["EpisodeOutro.CharacterName" + str(i) + "#style"] = tmpTextStyleName
            globalvars.GuiPresenter.data["EpisodeOutro.CharacterScore" + str(i) + "#style"] = tmpTextStyleName
            globalvars.GuiPresenter.data["EpisodeOutro.CharacterName" + str(i) + "#text"] = localizer.GetGameString(tmpResults["scores"][i][0])
            globalvars.GuiPresenter.data["EpisodeOutro.CharacterScore" + str(i) + "#text"] = str(tmpResults["scores"][i][1])
        else:
            globalvars.GuiPresenter.data["EpisodeOutro.CharacterName" + str(i) + "#text"] = ""
            globalvars.GuiPresenter.data["EpisodeOutro.CharacterScore" + str(i) + "#text"] = ""

    globalvars.GuiPresenter.data["EpisodeOutro.Continue#action"] = CloseEpisodeOutro
    globalvars.GuiPresenter.data["EpisodeOutro.Close#action"] = CloseEpisodeOutro
    globalvars.GuiPresenter.data["EpisodeOutro#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseEpisodeOutro },
        ]
    globalvars.GuiPresenter.ShowDialog("EpisodeOutro", True)
            
    
def CloseEpisodeOutro(*a):    
    globalvars.GuiPresenter.ShowDialog("EpisodeOutro", False)
    NextCareerStage()
    
#def ViewResults(*a):
#    globalvars.CurrentPlayer.SuggestLevel(globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]])
#    globalvars.GuiPresenter.ShowDialog("MapCareer", False)
#    globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").\
#                    GetSubtag(globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]]))
#    ShowEpisodeOutro()

#------------------------------
# играть уровень...
#------------------------------

#def PlayLevelFromMap(*a):
#    globalvars.CurrentPlayer.SuggestLevel(globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]])
#    globalvars.GuiPresenter.ShowDialog("MapCareer", False)
#    globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").\
#                    GetSubtag(globalvars.GuiPresenter.data["MapCareer.Levels#Values"][globalvars.GuiPresenter.data["MapCareer.Levels#Selected"][0]]))
#    PlayLevel()
#    
def PlayLevel(*a):
    globalvars.Board.Show(True)
    globalvars.Board.LaunchLevel()
    globalvars.Board.Freeze(True)
    ShowGameHUD()
    ShowLevelGoals()
    
def StartPlaying(*a):
    globalvars.GuiPresenter.ShowDialog("LevelGoals", False)
    globalvars.Board.ReallyStart()
    globalvars.Board.Freeze(False)

#------------------------------
# цели уровня
#------------------------------

def ShowLevelGoals(*a):
    tmpLevelName = globalvars.CurrentPlayer.GetLevel().GetContent()
    tmpLevelParams = globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpLevelName)
    globalvars.GuiPresenter.data["LevelGoals.Title#text"] = \
            localizer.GetGameString(globalvars.CurrentPlayer.GetLevel().GetStrAttr("restaurant")) + " - " + \
            localizer.GetGameString(globalvars.CurrentPlayer.GetLevel().GetStrAttr("day"))
    globalvars.GuiPresenter.data["LevelGoals.TextLevel#text"] = tmpLevelParams.GetStrAttr("name")
    globalvars.GuiPresenter.data["LevelGoals.TextGoal#text"] = str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneyGoal"))
    globalvars.GuiPresenter.data["LevelGoals.TextExpert#text"] = str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertGoal"))
    
    tmpIntro = eval(tmpLevelParams.GetStrAttr("intro"))
    tmpLayout = { "custpic": "CustomerPicture", "bonuspic": "BonusPicture", "nopic": "NoPicture" }[tmpIntro["layout"]]
    globalvars.GuiPresenter.data["LevelGoals.LevelIntro#value"] = tmpLayout
    globalvars.GuiPresenter.data["LevelGoals.LevelIntro."+tmpLayout+".IntroTitle#text"] = localizer.GetGameString(tmpIntro["title"])
    globalvars.GuiPresenter.data["LevelGoals.LevelIntro."+tmpLayout+".IntroText#text"] = localizer.GetGameString(tmpIntro["text"])
    
    if tmpIntro.get("picture") != None:
        globalvars.GuiPresenter.data["LevelGoals.LevelIntro."+tmpLayout+".IntroPicture#klass"] = tmpIntro["picture"]
        if tmpIntro.get("frno") != None:
            globalvars.GuiPresenter.data["LevelGoals.LevelIntro."+tmpLayout+".IntroPicture#frno"] = tmpIntro["frno"]
    globalvars.GuiPresenter.data["LevelGoals.Continue#action"] = StartPlaying
    globalvars.GuiPresenter.data["LevelGoals#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": StartPlaying },
        ]
    globalvars.GuiPresenter.ShowDialog("LevelGoals", True)
    
#------------------------------
# игровая инфо-панель
#------------------------------

def ShowGameHUD(*a):
    globalvars.GuiPresenter.data["GameHUD.Menu#action"] = ShowOptionsFromGame
    if globalvars.GameSettings.GetBoolAttr("debugMode"):
        globalvars.GuiPresenter.data["GameHUD#kbdCommands"] = [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ShowOptionsFromGame },
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_F6}], "call": DebugFinishLevel },
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_F7}], "call": DebugLastCustomer },
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_F8}], "call": DebugLoseLevel },
            ]
    else:
        globalvars.GuiPresenter.data["GameHUD#kbdCommands"] = [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ShowOptionsFromGame },
            ]
    globalvars.GuiPresenter.ShowDialog("GameHUD", True)

def DebugFinishLevel(*a):
    globalvars.Board.SendCommand(Cmd_DebugFinishLevel)
def DebugLastCustomer(*a):
    globalvars.Board.SendCommand(Cmd_DebugLastCustomer)
def DebugLoseLevel(*a):
    globalvars.Board.SendCommand(Cmd_DebugLoseLevel)

#обновить панель информации при старте уровня
def ResetGameHUD(*a):
    tmpSetting = globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme")
    globalvars.GuiPresenter.data["GameHUD.InfoPane#klass"] = globalvars.ThemesInfo.GetSubtag(tmpSetting).GetStrAttr("infopane")
    globalvars.GuiPresenter.data["GameHUD.Menu#style"] = \
            globalvars.GuiPresenter.DefData.GetTag("Styles").GetSubtag("PushButton.HUD-Menu."+tmpSetting)
    globalvars.GuiPresenter.data["GameHUD.LevelName#text"] = globalvars.CurrentPlayer.GetLevel().GetStrAttr("name")

def UpdateGameHUD(*a):
    try:
        if a[0].has_key("RemainingCustomers"):
            globalvars.GuiPresenter.data["GameHUD.NoPeople#text"] = str(a[0]["RemainingCustomers"])
        if a[0].has_key("LevelScore"):
            globalvars.GuiPresenter.data["GameHUD.Score#text"] = str(a[0]["LevelScore"])
        if a[0].has_key("Expert"):
            if a[0]["Expert"]:
                globalvars.GuiPresenter.data["GameHUD.GoalText#text"] = localizer.GetGameString("Str_HUD_ExpertText")
                globalvars.GuiPresenter.data["GameHUD.Goal#text"] = str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertgoal"))
            else:
                globalvars.GuiPresenter.data["GameHUD.GoalText#text"] = localizer.GetGameString("Str_HUD_GoalText")
                globalvars.GuiPresenter.data["GameHUD.Goal#text"] = str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneygoal"))
    except:
        pass
    globalvars.GuiPresenter.Dialogs["GameHUD"].UpdateView(globalvars.GuiPresenter.data)

#------------------------------
# результаты уровня
#------------------------------

def ShowLevelResults(*a):
    #a[0] = passing flag
    #a[1] = parameters (score, expert, etc)
    
    globalvars.Board.Freeze(True)
    tmpLevelName = globalvars.CurrentPlayer.GetLevel().GetContent()
    tmpLevelParams = globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpLevelName)
    
    tmpResult = (a[0] and a[1].get("expert"))*"Expert" + (a[0] and not(a[1].get("expert")))*"Passed" + (not a[0])*"Failed"
    globalvars.GuiPresenter.data["LevelResults.Background#value"] = tmpResult
    globalvars.GuiPresenter.data["LevelResults.Buttons#value"] = (a[0])*"Passed" + (not a[0])*"Failed"
    globalvars.GuiPresenter.data["LevelResults.Comment#text"] = \
            localizer.GetGameString(eval(tmpLevelParams.GetStrAttr(string.lower(tmpResult)))["text"])

    globalvars.GuiPresenter.data["LevelResults.TextServed#text"] = str(a[1]["served"])
    globalvars.GuiPresenter.data["LevelResults.TextLost#text"] = str(a[1]["lost"])
    globalvars.GuiPresenter.data["LevelResults.TextEarned#text"] = str(a[1]["score"])
    globalvars.GuiPresenter.data["LevelResults.TextLevelPoints#text"] = \
                str((a[0])*(globalvars.GameSettings.GetIntAttr("expertPoints")*a[1]["expert"] + \
                globalvars.GameSettings.GetIntAttr("levelPoints")*(1-a[1]["expert"]))) + \
                localizer.GetGameString("Str_LvComplete_From") + \
                str(globalvars.GameSettings.GetIntAttr("expertPoints"))
    globalvars.GuiPresenter.data["LevelResults.TextRoundPoints#text"] = \
                str(globalvars.CurrentPlayer.GetLevelParams(globalvars.LevelSettings.GetTag("Layout").GetStrAttr("theme")).GetIntAttr("points")) + \
                localizer.GetGameString("Str_LvComplete_From") + \
                str(globalvars.GameSettings.GetIntAttr("expertAll"))
    
    globalvars.GuiPresenter.data["LevelResults.ExpertSign#visible"] = a[1]["expert"]
    tmpBest = globalvars.BestResults.GetSubtag(globalvars.CurrentPlayer.GetLevel().GetContent())
    globalvars.GuiPresenter.data["LevelResults.BestSign#visible"] = \
                (a[0] and a[1]["score"]==tmpBest.GetIntAttr("hiscore") and a[1]["score"]>0)

    globalvars.GuiPresenter.data["LevelResults.Buttons.Passed.Continue#action"] = CloseLevelResults
    globalvars.GuiPresenter.data["LevelResults.Buttons.Failed.Restart#action"] = RestartLevelAfterLevelResults
    globalvars.GuiPresenter.data["LevelResults.Buttons.Failed.MainMenu#action"] = ExitToMenuFromLevelResults
    if a[0]:    
        globalvars.GuiPresenter.data["LevelResults#kbdCommands"] = [
            { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseLevelResults },
            ]
    else:
        globalvars.GuiPresenter.data["LevelResults#kbdCommands"] = [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ExitToMenuFromLevelResults },
            { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": RestartLevelAfterLevelResults },
            ]
    globalvars.GuiQueue.ScheduleSleep(1600)
    globalvars.GuiQueue.Schedule(RunCMD(ShowLevelResultsDialog))
    
def ShowLevelResultsDialog(*a):
    globalvars.GuiPresenter.ShowDialog("LevelResults", True)

def CloseLevelResults(*a):
    globalvars.GuiPresenter.ShowDialog("LevelResults", False)
    tmpSetting = globalvars.LevelSettings.GetTag("Layout").GetStrAttr("theme")
    if globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting) != []:
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
        globalvars.GuiPresenter.data["Cookbook#page"] = tmpAllSettings.index(tmpSetting)
        #globalvars.GuiPresenter.data["Cookbook#from"] = "Game"
        ShowCookbook(a)
    else:
        globalvars.GuiPresenter.ShowDialog("GameHUD", False)
        globalvars.Board.Clear()
        globalvars.Board.Show(False)
        NextCareerStage()

def RestartLevelAfterLevelResults(*a):
    globalvars.GuiPresenter.ShowDialog("LevelResults", False)
    #globalvars.Board.Clear()
    PlayLevel()

def ExitToMenuFromLevelResults(*a):
    globalvars.GuiPresenter.ShowDialog("LevelResults", False)
    globalvars.GuiPresenter.ShowDialog("GameHUD", False)
    globalvars.Board.Clear()
    globalvars.Board.Show(False)
    ShowMenu()

#------------------------------
# подсказка
#------------------------------

def ShowHint(*a):
    tmpHintNode = globalvars.HintsInfo.GetSubtag(a[0])
    tmpXY = eval(tmpHintNode.GetStrAttr("xy"))
    globalvars.GuiPresenter.data["Hints#x"], globalvars.GuiPresenter.data["Hints#y"] = a[1][0]+tmpXY[0], a[1][1]+tmpXY[1]
    globalvars.GuiPresenter.data["Hints.Background#value"] = tmpHintNode.GetStrAttr("layout")
    globalvars.GuiPresenter.data["Hints.HintsText#text"] = localizer.GetGameString(tmpHintNode.GetStrAttr("text"))
    globalvars.GuiPresenter.data["Hints.ShowHints#checked"] = globalvars.CurrentPlayer.XML.GetBoolAttr("Hints")
    globalvars.GuiPresenter.data["Hints.Continue#action"] = CloseHint
    globalvars.GuiPresenter.data["Hints.Close#action"] = CloseHint
    globalvars.GuiPresenter.data["Hints#kbdCommands"] = [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseHint },
        ]
    globalvars.GuiPresenter.ShowDialog("Hints", True)
    globalvars.Board.Freeze(True, False)
        
def CloseHint(*a):
    globalvars.CurrentPlayer.XML.SetBoolAttr("Hints", globalvars.GuiPresenter.data["Hints.ShowHints#checked"])
    globalvars.GuiPresenter.ShowDialog("Hints", False)
    globalvars.Board.Freeze(False)


#------------------------------
# задать вопрос
#------------------------------

def Ask(*a):
    globalvars.GuiPresenter.data["YesNo.Question#text"] = a[0]
    globalvars.GuiPresenter.data["YesNo.Ok#action"] = CloseQuestionYes
    globalvars.GuiPresenter.data["YesNo.Cancel#action"] = CloseQuestionNo
    globalvars.GuiPresenter.data["YesNo#YesAction"] = a[1]
    globalvars.GuiPresenter.data["YesNo#kbdCommands"] = [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": CloseQuestionYes },
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseQuestionNo },
        ]
    globalvars.GuiPresenter.ShowDialog("YesNo", True)

def CloseQuestionYes(*a):
    globalvars.GuiPresenter.ShowDialog("YesNo", False)
    globalvars.GuiPresenter.data["YesNo#YesAction"]()

def CloseQuestionNo(*a):
    globalvars.GuiPresenter.ShowDialog("YesNo", False)

#------------------------------
# окно паузы
#------------------------------

def SetPause(flag):
    #globalvars.Board.Freeze(flag)
    if flag:
        globalvars.GuiPresenter.data["Pause.Unpause#action"] = UnPause
        globalvars.GuiPresenter.data["Pause#kbdCommands"] = [
            { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": UnPause },
        ]
        globalvars.GuiPresenter.ShowDialog("Pause", True)
    else:
        globalvars.GuiPresenter.ShowDialog("Pause", False)
        
    #if flag:
        #if globalvars.StateStack[-1] in (PState_YesNo, PState_YesNoCancel, PState_EnterName):
            #globalvars.GuiPresenter.ShowDialog("Pause", flag)
            #self._ReleaseState(globalvars.StateStack[-1])
            #self.LastQuestion = ""
        #if globalvars.StateStack[-1] in (PState_Hints,):
        #    self._ReleaseState(globalvars.StateStack[-1])
        #self._SetState(PState_Pause)
    #globalvars.Musician.SetPause(flag)

def UnPause(*a):
    globalvars.PausedState = not globalvars.PausedState
    SetPause(False)

#------------------------------
# текстовые сообщения во время игры
# a[0] - код события
# a[1] - текст или число для вывода
# a[2] - координаты (необходимость этого параметра определяется по коду события)
#------------------------------

def ShowGameText(*a):
    if globalvars.GuiPresenter.data.get("GameHUD#EffectsLayer") != None:
        layer = globalvars.GuiPresenter.data["GameHUD#EffectsLayer"]
    else:
        layer = globalvars.GuiPresenter.DefData.GetTag("Objects").GetSubtag("GameHUD").GetIntAttr("layer")
    if globalvars.GuiPresenter.data.get("GameHUD#EffectsSublayer") != None:
        sublayer = globalvars.GuiPresenter.data["GameHUD#EffectsSublayer"]
    else:
        sublayer = 0
    
    #изменение счета за использование или потерю фишек
    if a[0] == "score":
        if a[1] > 0:
            style = "Popup.Game.AddScore"
            text = "+"+str(a[1])
        else:
            style = "Popup.Game.SubtractScore"
            text = str(a[1])
        crd = a[2]
    #сбор или потеря денег при ходе покупателя
    elif a[0] == "money":
        if len(a[1]) == 2:
            style = "Popup.Game.TakeMoney"
            text = "+$"+str(a[1][0])+"+$"+str(a[1][1])
        elif len(a[1]) == 1:
            if a[1][0] > 0:
                style = "Popup.Game.AddScore"
                text = "+$"+str(a[1][0])
            else:
                style = "Popup.Game.LoseMoney"
                text = "-$"+str(-a[1][0])
        crd = a[2]
    #похвала за удаление большого количества фишек
    elif a[0] == "commend":
        style = "Popup.Game.Commend"
        text = localizer.GetGameString(str(a[1]))
        crd = a[2]
    #достижэение базовой или экспертной цели уровня
    elif a[0] == "goalreached":
        style = "Popup.Game.GoalReached"
        text = localizer.GetGameString(str(a[1]))
        crd = (400, 300)
        
    globalvars.GuiPresenter.Dialogs["GameHUD"].AttachEffect(\
                fxmanager.CreateEffect(globalvars.GuiPresenter.Dialogs["GameHUD"],
                style, { "text": text, "crd": crd, "layer": layer, "sublayer": sublayer }))
            
#------------------------------
# отображение других эффектов
# a[0] - код события
# a[1] - координаты 
#------------------------------
def ShowGameEffect(*a):
    if globalvars.GuiPresenter.data.get("GameHUD#EffectsLayer") != None:
        layer = globalvars.GuiPresenter.data["GameHUD#EffectsLayer"]
    else:
        layer = globalvars.GuiPresenter.DefData.GetTag("Objects").GetSubtag("GameHUD").GetIntAttr("layer")
    if globalvars.GuiPresenter.data.get("GameHUD#EffectsSublayer") != None:
        sublayer = globalvars.GuiPresenter.data["GameHUD#EffectsSublayer"]
    else:
        sublayer = 0
    globalvars.GuiPresenter.Dialogs["GameHUD"].AttachEffect(\
                fxmanager.CreateEffect(globalvars.GuiPresenter.Dialogs["GameHUD"],
                a[0], { "crd": a[1], "layer": layer, "sublayer": sublayer }))
