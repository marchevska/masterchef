#!/usr/bin/env python
# -*- coding: cp1251 -*-

import string, sys, traceback

import scraft
from scraft import engine as oE

import globalvars
import config
from constants import *
from teggo.games import localizer, guipresenter, fxmanager, musicsound, cursor

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
    guipresenter.UseFile("def/gui.def")

GuiQueue = None

def ScheduleFunction(func, delta):
    global GuiQueue
    if GuiQueue == None:
        GuiQueue = oE.executor.CreateQueue()
    GuiQueue.ScheduleSleep(delta)
    GuiQueue.Schedule(RunCMD(func))

def CancelSchedule():
    global GuiQueue
    if GuiQueue != None:
        GuiQueue.Clear()

#------------------------------
# показ логотипов
#------------------------------

def ShowLogoSequence(*a):
    if globalvars.BrandingInfo.GetBoolAttr("pubLogo"):
        ShowPubLogo()
    else:
        ShowDevLogo()

def ShowPubLogo(*a):
    ScheduleFunction(ClosePubLogo, 3000)
    oE.SstDefKlass("publisher-logo", globalvars.BrandingInfo.GetSubtag("publisher-logo"))
    guipresenter.SetData("PubLogo.Background#klass", "publisher-logo")
    if globalvars.BrandingInfo.HasAttr("background"):
        oE.background.color = eval(globalvars.BrandingInfo.GetStrAttr("background"))
    guipresenter.SetData("PubLogo.Close#action", ClosePubLogo)
    guipresenter.SetData("PubLogo#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": ClosePubLogo },
        ])
    guipresenter.ShowDialog("PubLogo", True)

def ClosePubLogo(*a):
    CancelSchedule()
    guipresenter.ShowDialog("PubLogo", False)
    ShowDevLogo()

def ShowDevLogo(*a):
    ScheduleFunction(CloseDevLogo, 3000)
    guipresenter.SetData("DevLogo.Close#action", CloseDevLogo)
    guipresenter.SetData("DevLogo#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseDevLogo },
        ])
    guipresenter.ShowDialog("DevLogo", True)

def CloseDevLogo(*a):
    CancelSchedule()
    guipresenter.ShowDialog("DevLogo", False)
    ShowMenu()

#------------------------------
# отображение главного меню        
#------------------------------

def ShowMenu(*a):
    guipresenter.SetData("MainMenu.PlayCareer#action", NextCareerStage)
    guipresenter.SetData("MainMenu.Players#action", ShowPlayers)
    guipresenter.SetData("MainMenu.Options#action", ShowOptionsFromMenu)
    guipresenter.SetData("MainMenu.Cookbook#action", ShowCookbook)
    guipresenter.SetData("MainMenu.Rules#action", ShowRules)
    guipresenter.SetData("MainMenu.Hiscores#action", ShowHiscoresDialog)
    guipresenter.SetData("MainMenu.Quit#action", AskForQuitGame)
    guipresenter.SetData("MainMenu#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": AskForQuitGame }
        ])

    #если у игрока не разлочен ни один эпизод, то кулинарная книга недоступна
    tmpUnlockedSettings = filter(lambda x: \
                            globalvars.CurrentPlayer.GetLevelParams(x).GetBoolAttr("unlocked"),
                            eval(globalvars.GameSettings.GetStrAttr("settings")))
    guipresenter.SetData("MainMenu.Cookbook#disabled", (tmpUnlockedSettings == []))

    #брендинг
    tmpDevLogoInfo = globalvars.BrandingInfo.GetTag("smallDevLogo")
    guipresenter.SetData("MainMenu.DevLogoSmall#klass", tmpDevLogoInfo.GetStrAttr("klass"))
    guipresenter.SetData("MainMenu.DevLogoSmall#x", tmpDevLogoInfo.GetIntAttr("x"))
    guipresenter.SetData("MainMenu.DevLogoSmall#y", tmpDevLogoInfo.GetIntAttr("y"))
    tmpPubLogoInfo = globalvars.BrandingInfo.GetTag("smallPubLogo")
    if tmpPubLogoInfo.GetStrAttr("klass") != "$spritecraft$dummy$":
        oE.SstDefKlass("publisher-logo-small", globalvars.BrandingInfo.GetSubtag("publisher-logo-small"))
        guipresenter.SetData("MainMenu.PubLogoSmall#klass", tmpPubLogoInfo.GetStrAttr("klass"))
        guipresenter.SetData("MainMenu.PubLogoSmall#x", tmpPubLogoInfo.GetIntAttr("x"))
        guipresenter.SetData("MainMenu.PubLogoSmall#y", tmpPubLogoInfo.GetIntAttr("y"))

    guipresenter.SetData("MainMenu.VersionNumber#text",
                localizer.GetGameString("Str_Menu_Version")+globalvars.BuildInfo.GetStrAttr("buildNo"))
    if globalvars.GameConfig.GetStrAttr("Player") == "":
        guipresenter.SetData("MainMenu.WelcomeMessage#text", "")
        guipresenter.SetData("MainMenu.WelcomeName#text", "")
        if len(globalvars.PlayerList.GetPlayerList()) <= 1:
            ShowEnterNameDialog()
        else:
            ShowPlayers()
    else:
        guipresenter.SetData("MainMenu.WelcomeMessage#text", localizer.GetGameString("Str_Menu_Welcome"))
        guipresenter.SetData("MainMenu.WelcomeName#text", globalvars.GameConfig.GetStrAttr("Player"))
    guipresenter.ShowDialog("MainMenu", True)

def AskForQuitGame(*a):
    Ask(localizer.GetGameString("Str_Question_ExitGame"), QuitGame)
    
def QuitGame(*a):
    globalvars.ExitFlag = True

#------------------------------
# опции - показ и редактирование
#------------------------------

def ShowOptionsFromMenu(*a):
    guipresenter.SetData("Options.Buttons#value", "Menu")
    guipresenter.SetData("Options.Buttons.Menu.Ok#action", CloseOptions)
    guipresenter.SetData("Options#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseOptions },
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": CloseOptions },
        ])
    ShowOptions()
    
def ShowOptions(*a):
    guipresenter.SetData("Options.Sound#value", globalvars.GameConfig.GetIntAttr("Sound"))
    guipresenter.SetData("Options.Sound#onModify", UpdateSoundVolume)
    guipresenter.SetData("Options.Music#value", globalvars.GameConfig.GetIntAttr("Music"))
    guipresenter.SetData("Options.Music#onModify", UpdateMusicVolume)
    guipresenter.SetData("Options.Mute#checked", globalvars.GameConfig.GetBoolAttr("Mute"))
    guipresenter.SetData("Options.Mute#onUpdate", UpdateMuteSoudnsOption)
    guipresenter.SetData("Options.Hints#checked", globalvars.CurrentPlayer.XML.GetBoolAttr("Hints"))
    guipresenter.SetData("Options.Fullscreen#checked", globalvars.GameConfig.GetBoolAttr("Fullscreen"))
    guipresenter.ShowDialog("Options", True)

#close and apply options
def CloseOptions(*a):
    globalvars.GameConfig.SetBoolAttr("Fullscreen", guipresenter.GetData("Options.Fullscreen#checked"))
    globalvars.GameConfig.SetBoolAttr("Mute", guipresenter.GetData("Options.Mute#checked"))
    globalvars.CurrentPlayer.XML.SetBoolAttr("Hints", guipresenter.GetData("Options.Hints#checked"))
    globalvars.CurrentPlayer.Save()
    config.ApplyOptions()
    guipresenter.ShowDialog("Options", False)
    
def ShowOptionsFromGame(*a):    
    guipresenter.SetData("Options.Buttons#value", "Game")
    guipresenter.SetData("Options.Buttons.Game.Resume#action", CloseOptions)
    guipresenter.SetData("Options.Buttons.Game.Restart#action", RestartGameFromOptions)
    guipresenter.SetData("Options.Buttons.Game.EndGame#action", ExitFromGameToMenu)
    guipresenter.SetData("Options#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseOptions },
        ])
    ShowOptions()
    
def RestartGameFromOptions(*a):
    Ask(localizer.GetGameString("Str_Question_RestartLevel"), RestartGame)

def RestartGame(*a):
    CloseOptions()
    PlayLevel()
    
def ExitFromGameToMenu(*a):
    CloseOptions()
    globalvars.Board.Clear()
    globalvars.Board.Show(False)
    guipresenter.ShowDialog("GameHUD", False)
    ShowMenu()
    
def UpdateMuteSoudnsOption(*a):
    globalvars.GameConfig.SetBoolAttr("Mute", guipresenter.GetData("Options.Mute#checked"))
    config.ApplyOptions()

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
        if not guipresenter.GetData("Rules#page"):
            guipresenter.SetData("Rules#page", 0)
        guipresenter.SetData("Rules.Background#klass", "help-page"+str(guipresenter.GetData("Rules#page")+1))
        if guipresenter.GetData("Rules#page") == 0:
            guipresenter.SetData("Rules.Prev#disabled", True)
        else:
            guipresenter.SetData("Rules.Prev#disabled", False)
            guipresenter.SetData("Rules.Prev#action", RulesPrevPage)
        if guipresenter.GetData("Rules#page") == guipresenter.GetData("Rules#TotalHelpPages") - 1:
            guipresenter.SetData("Rules.Next#disabled", True)
        else:
            guipresenter.SetData("Rules.Next#disabled", False)
            guipresenter.SetData("Rules.Next#action", RulesNextPage)
        guipresenter.SetData("Rules.Close#action", CloseRules)
        guipresenter.SetData("Rules#kbdCommands", [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseRules },
        ])
        guipresenter.ShowDialog("Rules", True)
    except:
        pass

def RulesPrevPage(*a):
    try:
        if guipresenter.GetData("Rules#page") > 0:
            guipresenter.SetData("Rules#page", guipresenter.GetData("Rules#page") - 1)
    except:
        pass
    ShowRules()

def RulesNextPage(*a):
    try:
        if guipresenter.GetData("Rules#page") < guipresenter.GetData("Rules#TotalHelpPages") - 1:
            guipresenter.SetData("Rules#page", guipresenter.GetData("Rules#page") + 1)
    except:
        pass
    ShowRules()

def CloseRules(*a):
    guipresenter.ShowDialog("Rules", False)
    

#------------------------------
# кулинарная книга
#------------------------------

def ShowCookbook(*a):
    try:
        guipresenter.SetData("Cookbook#from", a[0])
        if not guipresenter.GetData("Cookbook#page"):
            guipresenter.SetData("Cookbook#page", 0)
        #коррекция в случае переключения на другой профиль игрока:
        #не показывать не разлоченные страницы книги
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
        #no - номер страницы книги
        no = guipresenter.GetData("Cookbook#page")
        while not globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no]).GetBoolAttr("unlocked") and no>0:
            no -= 1
        tmpSetting = tmpAllSettings[no]
        guipresenter.SetData("Cookbook#page", no)
        
        #нарисовать страницу сеттинга
        guipresenter.SetData("Cookbook.Background#klass", globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("background"))
        guipresenter.SetData("Cookbook.Logo#klass", globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("logo"))
        
        #проверить рецепты: известные или нет, новые или старые
        tmpRecipes = filter(lambda x: globalvars.RecipeInfo.GetSubtag(x).GetStrAttr("setting") == tmpSetting,
                                map(lambda x: x.GetContent(), globalvars.RecipeInfo.Tags()))
        tmpNewRecipes = globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting)
        if len(tmpNewRecipes) > 0:
            guipresenter.CreateEffect("Cookbook", "Popup.Game.GoalReached",
                    { "text": (localizer.GetGameString("Str_NewRecipesLearned")), "crd": (400, 300) })
            
        for i in range(guipresenter.GetData("Cookbook#MaxRecipesOnPage")):
            recipeCrd = (globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeX"), globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeY"))
            guipresenter.SetData("Cookbook.Recipe" + str(i+1) + "#x", recipeCrd[0])
            guipresenter.SetData("Cookbook.Recipe" + str(i+1) + "#y", recipeCrd[1])
            if globalvars.CurrentPlayer.GetLevelParams(tmpRecipes[i]).GetBoolAttr("unlocked"):
                guipresenter.SetData("Cookbook.Recipe" + str(i+1) + "#klass", globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("badge"))
                if tmpRecipes[i] in tmpNewRecipes:
                    globalvars.CurrentPlayer.SetLevelParams(tmpRecipes[i], { "seen": True })
                    guipresenter.CreateEffect("Cookbook", "Trail.CookbookNewRecipe", { "crd": recipeCrd })
            else:
                guipresenter.SetData("Cookbook.Recipe" + str(i+1) + "#klass", globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("emptyBadge"))
        
        #кнопки пролистывания ниги
        #если книга открыта из главного меню
        if string.find(str(a[0]), "MainMenu") >= 0:
            guipresenter.SetData("Cookbook.Continue#hidden", True)
            guipresenter.SetData("Cookbook.Close#disabled", False)
            
            guipresenter.SetData("Cookbook.Prev#hidden", not(no>0))
            if no>0:
                guipresenter.SetData("Cookbook.Prev#disabled",
                        not(globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no-1]).GetBoolAttr("unlocked")))
            
            guipresenter.SetData("Cookbook.Next#hidden", not(no<len(tmpAllSettings)-1))
            if no<len(tmpAllSettings)-1:
                guipresenter.SetData("Cookbook.Next#disabled", 
                        not(globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no+1]).GetBoolAttr("unlocked")))
                
        #иначе - книга открыта после прохождения уровня
        else:
            guipresenter.SetData("Cookbook.Close#disabled", True)
            guipresenter.SetData("Cookbook.Continue#hidden", False)
            guipresenter.SetData("Cookbook.Prev#hidden", True)
            guipresenter.SetData("Cookbook.Next#hidden", True)
        
        guipresenter.SetData("Cookbook.Prev#action", CookbookPrevPage)
        guipresenter.SetData("Cookbook.Next#action", CookbookNextPage)
        guipresenter.SetData("Cookbook.Close#action", CloseCookbook)
        guipresenter.SetData("Cookbook.Continue#action", CloseCookbook)
        guipresenter.SetData("Cookbook#kbdCommands", [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseCookbook },
        ])
        guipresenter.ShowDialog("Cookbook", True)
    except:
        print string.join(apply(traceback.format_exception, sys.exc_info()))

def CookbookPrevPage(*a):
    try:
        guipresenter.SetData("Cookbook#page", guipresenter.GetData("Cookbook#page") - 1)
    except:
        pass
    ShowCookbook(guipresenter.GetData("Cookbook#from"))

def CookbookNextPage(*a):
    try:
        guipresenter.SetData("Cookbook#page", guipresenter.GetData("Cookbook#page") + 1)
    except:
        pass
    ShowCookbook(guipresenter.GetData("Cookbook#from"))

def CloseCookbook(*a):
    guipresenter.ShowDialog("Cookbook", False)
    if string.find(str(guipresenter.GetData("Cookbook#from")), "LevelResults") >= 0:
        guipresenter.ShowDialog("GameHUD", False)
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
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Logo#frno", 2*i)
            else:
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Logo#frno", 2*i+1)
        
        tmpTagScores = map(lambda x: (x.GetContent() ,x.GetStrAttr("score")),
                    globalvars.Hiscores.GetSubtag(tmpHiscoreTags[i]).Tags())
        for j in range(5):
            if j < len(tmpTagScores):
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#text", tmpTagScores[j][0])
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#text", tmpTagScores[j][1])
            else:
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#text", localizer.GetGameString("Str_Hiscores_EmptyPlayer"))
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#text", "")
            if guipresenter.GetData("Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#text") == globalvars.GameConfig.GetStrAttr("Player"):
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#style", guipresenter.GetStyle("TextLabel.Hiscore.Player.CurrentPlayer"))
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#style", guipresenter.GetStyle("TextLabel.Hiscore.Score.CurrentPlayer"))
            else:
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Player" + str(j+1) + "#style", guipresenter.GetStyle("TextLabel.Hiscore.Player"))
                guipresenter.SetData("Hiscores." + tmpHiscoreTags[i] + ".Score" + str(j+1) + "#style", guipresenter.GetStyle("TextLabel.Hiscore.Score"))

    guipresenter.SetData("Hiscores#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseHiscores },
        ])
    guipresenter.SetData("Hiscores.HiscoresClose#action", CloseHiscores)
    guipresenter.SetData("Hiscores.HiscoresReset#action", AskForClear)
    guipresenter.ShowDialog("Hiscores", True)

def CloseHiscores(*a):
    guipresenter.ShowDialog("Hiscores", False)
    
def AskForClear(*a):
    Ask(localizer.GetGameString("Str_Question_ClearHiscores"), ClearHiscores)
    
def ClearHiscores(*a):
    config.ClearHiscores()
    ShowHiscoresDialog()
    
#------------------------------
# список игроков
#------------------------------

def ShowPlayers(*a):
    guipresenter.SetData("Players.List#Values", globalvars.PlayerList.GetPlayerList())
    if not guipresenter.GetData("Players.List#first"):
        guipresenter.SetData("Players.List#first", 0)
    if not guipresenter.GetData("Players.List#Selected"):
        guipresenter.SetData("Players.List#Selected", [])
    
    #прокрутка списка при открытии диалога
    tmpList = globalvars.PlayerList.GetPlayerList()
    tmpFirstPlayer = 0
    if guipresenter.GetData("Players.List#Selected") != []:
        tmpSelectedPlayer = tmpList[guipresenter.GetData("Players.List#Selected")[0]]
    else:
        tmpSelectedPlayer = ""
    if globalvars.GameConfig.GetStrAttr("Player") != "":
        tmpName = globalvars.GameConfig.GetStrAttr("Player")
        if tmpSelectedPlayer == "":
            tmpSelectedPlayer = tmpName
    if tmpList.count(tmpSelectedPlayer) > 0:
        tmpInd = tmpList.index(tmpSelectedPlayer)
        guipresenter.SetData("Players.List#Selected", [tmpInd])
        if tmpInd < guipresenter.GetData("Players.List#height"):
            tmpFirstPlayer = 0
        else:
            tmpFirstPlayer = tmpInd - guipresenter.GetData("Players.List#height")+1
    else:
        if tmpFirstPlayer + guipresenter.GetData("Players.List#height") > len(tmpList):
            tmpFirstPlayer = max(tmpFirstPlayer-1, 0)
        else:
            tmpFirstPlayer = 0

    guipresenter.SetData("Players.List#first", tmpFirstPlayer)
    guipresenter.SetData("Players.List#action", UpdatePlayersButtons)
    
    guipresenter.SetData("Players.New#action", ShowEnterNameDialog)
    guipresenter.SetData("Players.Remove#action", AskForRemovingPlayer)
    guipresenter.SetData("Players.Ok#action", SelectPlayer)
    guipresenter.SetData("Players.Close#action", ClosePlayers)
    UpdatePlayersButtons()
    guipresenter.ShowDialog("MainMenu", True)
    guipresenter.ShowDialog("Players", True)

def UpdatePlayersButtons(*a):
    guipresenter.SetData("Players.Ok#disabled", (guipresenter.GetData("Players.List#Selected") == []))
    guipresenter.SetData("Players.Remove#disabled", (guipresenter.GetData("Players.List#Selected") == []))
    guipresenter.SetData("Players.Close#disabled", (globalvars.GameConfig.GetStrAttr("Player") == ""))
    guipresenter.SetData("Players#kbdCommands",
        [{ "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ClosePlayers }]*(not guipresenter.GetData("Players.Close#disabled")) + \
        [{ "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": SelectPlayer }]*(not guipresenter.GetData("Players.Ok#disabled")))
    guipresenter.ShowDialog("Players", True)

def ClosePlayers(*a):
    guipresenter.ShowDialog("Players", False)
    
def SelectPlayer(*a):
    if len(guipresenter.GetData("Players.List#Selected")) == 1:
        globalvars.PlayerList.SelectPlayer(globalvars.PlayerList.GetPlayerList()[guipresenter.GetData("Players.List#Selected")[0]])
        guipresenter.ShowDialog("Players", False)
        ShowMenu()

def AskForRemovingPlayer(*a):
    Ask(localizer.GetGameString("Str_Question_RemovePlayer"), RemovePlayer)
    
def RemovePlayer(*a):
    try:
        tmpPlayer = globalvars.PlayerList.GetPlayerList()[guipresenter.GetData("Players.List#Selected")[0]]
        globalvars.PlayerList.DelPlayer(tmpPlayer)
    except:
        pass
    guipresenter.SetData("Players.List#Selected", [])
    ShowPlayers()

#------------------------------
# новый игрок - ввод имени
#------------------------------

def ShowEnterNameDialog(*a):
    if not guipresenter.GetData("EnterName.NewPlayerName#text"):
        guipresenter.SetData("EnterName.NewPlayerName#text", "")
    if not guipresenter.GetData("EnterName.ErrorMessage#text"):
        guipresenter.SetData("EnterName.ErrorMessage#text", "")
    guipresenter.SetData("EnterName.NewPlayerName#onUpdate", UpdateNameEntry)
    guipresenter.SetData("EnterName.Ok#action", CreateNewPlayerOk)
    guipresenter.SetData("EnterName.Cancel#action", CloseEnterNameDialog)
    guipresenter.SetData("EnterName#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseEnterNameDialog },
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": CreateNewPlayerOk },
        ])
    guipresenter.ShowDialog("EnterName", True)

def CheckNameErrors(*a):
    tmpErrorMessage = ""
    tmpName = guipresenter.GetData("EnterName.NewPlayerName#text")
    if len(tmpName) == 0:
        tmpErrorMessage = localizer.GetGameString("Str_EnterName_Error_Empty")
    elif tmpName == 'None':
        tmpErrorMessage = localizer.GetGameString("Str_EnterName_Error_Bad")
    elif globalvars.PlayerList.GetPlayerList().count(tmpName) > 0:
        tmpErrorMessage = localizer.GetGameString("Str_EnterName_Error_Exist")
    guipresenter.SetData("EnterName.ErrorMessage#text", tmpErrorMessage)
    #if tmpErrorMessage != "":
    #    guipresenter.ShowDialog("EnterName", True)
    guipresenter.ShowDialog("EnterName", True)

def UpdateNameEntry(*a):
    if guipresenter.GetData("EnterName.ErrorMessage#text") != "":
        #CheckNameErrors()
        guipresenter.SetData("EnterName.ErrorMessage#text", "")
        guipresenter.ShowDialog("EnterName", True)

def CreateNewPlayerOk(*a):
    CheckNameErrors()
    if guipresenter.GetData("EnterName.ErrorMessage#text") == "":
        globalvars.PlayerList.CreatePlayer(guipresenter.GetData("EnterName.NewPlayerName#text"))
        guipresenter.SetData("Players.List#Selected", [len(globalvars.PlayerList.GetPlayerList())-1])
        CloseEnterNameDialog()

def CloseEnterNameDialog(*a):
    guipresenter.SetData("EnterName.NewPlayerName#text", "")
    guipresenter.SetData("EnterName.ErrorMessage#text", "")
    guipresenter.ShowDialog("EnterName", False)
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
    
#------------------------------
# карта
#------------------------------

#сброс выделения на карте в случае смены игрока
def ResetMapSelection(*a):
    guipresenter.SetData("MapCareer.Levels#Selected", [])
    tmpOutros = list(globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
    for i in range(len(tmpOutros)):
        guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#selected", False)
    tmpLevels = list(globalvars.LevelProgress.GetTag("Levels").Tags("level"))
    for i in range(len(tmpLevels)):
        guipresenter.SetData("MapCareer.Levels.Level"+str(i+1)+"#selected", False)
    
def ShowMap(*a):
    #нарисовать картинки эпизодов
    tmpEpisodes = list(globalvars.LevelProgress.GetTag("Episodes").Tags("episode"))
    for i in range(len(tmpEpisodes)):
        guipresenter.SetData("MapCareer.Episode"+str(i)+"#klass", tmpEpisodes[i].GetStrAttr("image"))
        guipresenter.SetData("MapCareer.Episode"+str(i)+"#x", tmpEpisodes[i].GetIntAttr("x"))
        guipresenter.SetData("MapCareer.Episode"+str(i)+"#y", tmpEpisodes[i].GetIntAttr("y"))
        if globalvars.CurrentPlayer.GetLevelParams(tmpEpisodes[i].GetContent()).GetBoolAttr("unlocked"):
            guipresenter.SetData("MapCareer.Episode"+str(i)+"#frno", 0)
        else:
            guipresenter.SetData("MapCareer.Episode"+str(i)+"#frno", 1)
                
    #разместить и нарисовать значки outro эпизодов
    tmpOutros = list(globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
    for i in range(len(tmpOutros)):
        guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#x", tmpOutros[i].GetIntAttr("x"))
        guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#y", tmpOutros[i].GetIntAttr("y"))
        
        #читаем запись из профиля игрока
        tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(tmpOutros[i].GetContent())
        if tmpPlayerResult.GetBoolAttr("beat1st"):
            guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#style", guipresenter.GetStyle("RadioButton.Episodes.1st"))
        elif tmpPlayerResult.GetBoolAttr("beat2nd"):
            guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#style", guipresenter.GetStyle("RadioButton.Episodes.2nd"))
        elif tmpPlayerResult.GetBoolAttr("passed"):
            guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#style", guipresenter.GetStyle("RadioButton.Episodes.Pass"))
        else:
            guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#style", guipresenter.GetStyle("RadioButton.Episodes.Episodes"))
        guipresenter.SetData("MapCareer.Levels.Episode"+str(i+1)+"#disabled", not(tmpPlayerResult.GetBoolAttr("unlocked")))
                
    #разместить и нарисовать значки уровней
    tmpLevels = list(globalvars.LevelProgress.GetTag("Levels").Tags("level"))
    for i in range(len(tmpLevels)):
        guipresenter.SetData("MapCareer.Levels.Level"+str(i+1)+"#x", tmpLevels[i].GetIntAttr("x"))
        guipresenter.SetData("MapCareer.Levels.Level"+str(i+1)+"#y", tmpLevels[i].GetIntAttr("y"))
        
        tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(tmpLevels[i].GetContent())
        if tmpPlayerResult.GetBoolAttr("expert"):
            guipresenter.SetData("MapCareer.Levels.Level"+str(i+1)+"#style", guipresenter.GetStyle("RadioButton.LevelsExpert"))
        else:
            guipresenter.SetData("MapCareer.Levels.Level"+str(i+1)+"#style", guipresenter.GetStyle("RadioButton.Levels"))
        guipresenter.SetData("MapCareer.Levels.Level"+str(i+1)+"#disabled", not(tmpPlayerResult.GetBoolAttr("unlocked")))

    guipresenter.SetData("MapCareer.Levels#Values", map(lambda x: x.GetContent(), tmpLevels+tmpOutros))
    guipresenter.SetData("MapCareer.Levels#first", 0)
    if not guipresenter.GetData("MapCareer.Levels#Selected"):
        guipresenter.SetData("MapCareer.Levels#Selected", [])

    #если выбран другой игрок, сбросить выделение
    if not guipresenter.GetData("MapCareer.Levels#Player"):
        guipresenter.SetData("MapCareer.Levels#Player", "")
    if guipresenter.GetData("MapCareer.Levels#Player") != globalvars.GameConfig.GetStrAttr("Player"):
        guipresenter.SetData("MapCareer.Levels#Selected", [])
    
    #автоматическое выделение последнего разлоченного уровня
    if guipresenter.GetData("MapCareer.Levels#Selected") == []:
        tmpSelectedLevel = ""
    else:
        tmpSelectedLevel = guipresenter.GetData("MapCareer.Levels#Values")[guipresenter.GetData("MapCareer.Levels#Selected")[0]]
    tmpHilightedLevel = ""
    if globalvars.CurrentPlayer.NewUnlockedLevel() != "":
        tmpHilightedLevel = tmpSelectedLevel = globalvars.CurrentPlayer.NewUnlockedLevel()
        globalvars.CurrentPlayer.PopNewUnlockedLevel()
    if tmpSelectedLevel == "":
        tmpSelectedLevel = globalvars.CurrentPlayer.LastUnlockedLevel()
    if tmpSelectedLevel in guipresenter.GetData("MapCareer.Levels#Values"):
        guipresenter.SetData("MapCareer.Levels#Selected", [guipresenter.GetData("MapCareer.Levels#Values").index(tmpSelectedLevel)])

    guipresenter.SetData("MapCareer.Levels#action", UpdateMapTablet)
    #guipresenter.GetData("MapCareer.Start#action"] = PlayLevelFromMap
    #guipresenter.GetData("MapCareer.ViewResults#action"] = ViewResults
    guipresenter.SetData("MapCareer.Start#action", DoMapSelection)
    guipresenter.SetData("MapCareer.ViewResults#action", DoMapSelection)
    guipresenter.SetData("MapCareer.Close#action", CloseMap)
    guipresenter.SetData("MapCareer#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseMap },
        ])

    UpdateMapTablet()

#обновить надписи на табличке
#при смене состояния карты
def UpdateMapTablet(*a):
    tmpSelectedLevels = map(lambda x: guipresenter.GetData("MapCareer.Levels#Values")[x],
                            guipresenter.GetData("MapCareer.Levels#Selected"))
    if len(tmpSelectedLevels) == 1:
        tmpNewLevel = tmpSelectedLevels[0]
        guipresenter.SetData("MapCareer.Levels#SelectedLevel", tmpNewLevel)
        tmpLevelKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("level"))
        tmpOutroKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
        
        #если выбран уровень 
        if tmpNewLevel in tmpLevelKeys and \
                    globalvars.CurrentPlayer.GetLevelParams(tmpNewLevel).GetBoolAttr("unlocked"):
            guipresenter.SetData("MapCareer.ViewResults#hidden", True)
            guipresenter.SetData("MapCareer.Start#hidden", False)
            guipresenter.SetData("MapCareer.Start#disabled", False)
            
            tmpBest = globalvars.BestResults.GetSubtag(tmpNewLevel)
            if tmpBest.GetIntAttr("hiscore") != 0 and tmpBest.GetStrAttr("player") != "":
                guipresenter.SetData("MapCareer.BestResult#text",
                        localizer.GetGameString("Str_MapHiscore") + str(tmpBest.GetIntAttr("hiscore")))
                guipresenter.SetData("MapCareer.AchievedBy#text",
                        localizer.GetGameString("Str_MapAchievedBy") + tmpBest.GetStrAttr("player"))
            else:
                guipresenter.SetData("MapCareer.BestResult#text", localizer.GetGameString("Str_MapNoHiscore"))
                guipresenter.SetData("MapCareer.AchievedBy#text", "")
            
            guipresenter.SetData("MapCareer.RestaurantTitle#text",
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("restaurant")))
            guipresenter.SetData("MapCareer.RestaurantDay#text",
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("day")))
            
        #просмотр результатов уровня
        elif tmpNewLevel in tmpOutroKeys and \
                    globalvars.CurrentPlayer.GetLevelParams(tmpNewLevel).GetBoolAttr("unlocked"):
            guipresenter.SetData("MapCareer.ViewResults#hidden", False)
            guipresenter.SetData("MapCareer.Start#hidden", True)
            guipresenter.SetData("MapCareer.BestResult#text", "")
            guipresenter.SetData("MapCareer.AchievedBy#text", "")
            guipresenter.SetData("MapCareer.RestaurantTitle#text",
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("restaurant")))
            guipresenter.SetData("MapCareer.RestaurantDay#text",
                localizer.GetGameString(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewLevel).GetStrAttr("day")))
                
    else:
        guipresenter.SetData("MapCareer.Levels#SelectedLevel", "")
        guipresenter.SetData("MapCareer.ViewResults#hidden", True)
        guipresenter.SetData("MapCareer.Start#hidden", False)
        guipresenter.SetData("MapCareer.Start#disabled", True)
        guipresenter.SetData("MapCareer.BestResult#text", "")
        guipresenter.SetData("MapCareer.AchievedBy#text", "")
        guipresenter.SetData("MapCareer.RestaurantTitle#text", localizer.GetGameString("Str_MapSelect"))
        guipresenter.SetData("MapCareer.RestaurantDay#text", "")
        
    guipresenter.ShowDialog("MapCareer", True)

def CloseMap(*a):
    guipresenter.ShowDialog("MapCareer", False)
    ShowMenu()

def DoMapSelection(*a):
    guipresenter.ShowDialog("MapCareer", False)
    globalvars.CurrentPlayer.SuggestLevel(guipresenter.GetData("MapCareer.Levels#Values")[guipresenter.GetData("MapCareer.Levels#Selected")[0]])
    if globalvars.CurrentPlayer.GetNextLevelInsight() != None:
        NextCareerStage()
    else:
        oE.Log("Level selection fatal error, level %s", guipresenter.GetData("MapCareer.Levels#Values")[guipresenter.GetData("MapCareer.Levels#Selected")[0]])
        oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        sys.exit()
        

#------------------------------
# комикс 
#------------------------------

def ShowComics(*a):
    guipresenter.SetData("Comics.Background#klass", globalvars.CurrentPlayer.GetLevel().GetStrAttr("image"))
    guipresenter.SetData("Comics.Continue#action", CloseComics)
    guipresenter.SetData("Comics.Close#action", CloseComics)
    guipresenter.SetData("Comics#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseComics },
        ])
    guipresenter.ShowDialog("MainMenu", False)
    guipresenter.ShowDialog("Comics", True)

def CloseComics(*a):
    guipresenter.ShowDialog("Comics", False)
    NextCareerStage()

#------------------------------
# начало эпизода
#------------------------------

def ShowEpisodeIntro(*a):
    musicsound.PlaySound("episode.intro")
    tmpLevel = globalvars.CurrentPlayer.GetLevel()
    tmpEpisode = tmpLevel.GetStrAttr("episode")
    tmpCharacters = eval(globalvars.LevelProgress.GetTag("People").GetSubtag(tmpEpisode).GetStrAttr("people")).items()
    
    guipresenter.SetData("EpisodeIntro.Theme#value", tmpEpisode)
    
    #draw characters and write down their names
    for i in range(guipresenter.GetData("EpisodeIntro#MaxPeopleOnLevel")):
        if i < len(tmpCharacters):
            guipresenter.SetData("EpisodeIntro.Character"+str(i)+"#klass", globalvars.CompetitorsInfo.GetSubtag(tmpCharacters[i][0]).GetStrAttr("src"))
            guipresenter.SetData("EpisodeIntro.Character"+str(i)+"#hotspot", "CenterBottom")
            guipresenter.SetData("EpisodeIntro.Character"+str(i)+"#x", tmpCharacters[i][1]["xy"][0])
            guipresenter.SetData("EpisodeIntro.Character"+str(i)+"#y", tmpCharacters[i][1]["xy"][1])
            guipresenter.SetData("EpisodeIntro.CharacterName"+str(i)+"#text", str(i+1)+". " + localizer.GetGameString(tmpCharacters[i][0]))
        else:
            guipresenter.SetData("EpisodeIntro.Character"+str(i)+"#klass", "$spritecraft$dummy$")
            guipresenter.SetData("EpisodeIntro.CharacterName"+str(i)+"#text", "")
    
    guipresenter.SetData("EpisodeIntro.Continue#action", CloseEpisodeIntro)
    guipresenter.SetData("EpisodeIntro.Close#action", CloseEpisodeIntro)
    guipresenter.SetData("EpisodeIntro#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseEpisodeIntro },
        ])
    guipresenter.ShowDialog("MainMenu", False)
    guipresenter.ShowDialog("EpisodeIntro", True)
    
def CloseEpisodeIntro(*a):    
    guipresenter.ShowDialog("EpisodeIntro", False)
    NextCareerStage()
    
#------------------------------
# конец эпизода
#------------------------------

def ShowEpisodeOutro(*a):
    tmpLevel = globalvars.CurrentPlayer.GetLevel()
    tmpEpisode = tmpLevel.GetStrAttr("episode")
    tmp = globalvars.ThemesInfo.GetSubtag(tmpEpisode)
    tmpResults = globalvars.CurrentPlayer.GetScoresPlaceAndCondition()
    
    if tmpResults["pass"]:
        musicsound.PlaySound("episode.win")
    else:
        musicsound.PlaySound("episode.lose")
        
    guipresenter.SetData("EpisodeOutro.Theme#value", tmpEpisode)
        
    #display presenter's speech
    tmpSpeechVariant = tmpEpisode + "_" + (tmpResults["pass"])*"Passed" + (1 - tmpResults["pass"])*"Failed"
    guipresenter.SetData("EpisodeOutro.OutroSpeech#value", tmpSpeechVariant)
    guipresenter.SetData("EpisodeOutro.OutroSpeech." + tmpSpeechVariant + ".SpeechWinners#text",
                                reduce(lambda x, y: x+y, map(lambda i: \
                                    localizer.GetGameString(tmpResults["scores"][i][0])+\
                                    ", "*(i<tmpLevel.GetIntAttr("PassFurther")-1),
                                    range(tmpLevel.GetIntAttr("PassFurther")))))
    
    #episode winners
    for i in range(guipresenter.GetData("EpisodeOutro#MaxPeopleOnLevel")):
        if i < tmpLevel.GetIntAttr("PassFurther"):
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+"#visible", True)
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+"#x", Crd_CharOutroPositions[tmpLevel.GetIntAttr("PassFurther")][i][0])
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+"#y", Crd_CharOutroPositions[tmpLevel.GetIntAttr("PassFurther")][i][1])
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+".Character#klass",
                    globalvars.CompetitorsInfo.GetSubtag(tmpResults["scores"][i][0]).GetStrAttr("src"))
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+".Medallion#klass", tmp.GetStrAttr("winnerSign"))
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+".Number#text", str(i+1))
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+".Name#text", localizer.GetGameString(tmpResults["scores"][i][0]))
            guipresenter.CreateEffect("EpisodeOutro", "Particles.OutroCharacterStars",
                        { "crd": Crd_CharOutroPositions[tmpLevel.GetIntAttr("PassFurther")][i] })
            
        else:
            guipresenter.SetData("EpisodeOutro.Character"+str(i)+"#visible", False)
    
    for i in range(guipresenter.GetData("EpisodeOutro#MaxPeopleOnLevel")):
        if i < len(tmpResults["scores"]):
            tmpTextStyleName = guipresenter.GetStyle(\
                        "TextLabel.EpisodeOutro." + (i == tmpResults["place"]-1)*"Jenny" + \
                        (1 - (i == tmpResults["place"]-1))*"Names" + "." + \
                        (i >= tmpLevel.GetIntAttr("PassFurther"))*"Not" + "Passed")
            guipresenter.SetData("EpisodeOutro.CharacterName" + str(i) + "#style", tmpTextStyleName)
            guipresenter.SetData("EpisodeOutro.CharacterScore" + str(i) + "#style", tmpTextStyleName)
            guipresenter.SetData("EpisodeOutro.CharacterName" + str(i) + "#text", localizer.GetGameString(tmpResults["scores"][i][0]))
            guipresenter.SetData("EpisodeOutro.CharacterScore" + str(i) + "#text", str(tmpResults["scores"][i][1]))
        else:
            guipresenter.SetData("EpisodeOutro.CharacterName" + str(i) + "#text", "")
            guipresenter.SetData("EpisodeOutro.CharacterScore" + str(i) + "#text", "")

    guipresenter.SetData("EpisodeOutro.Continue#action", CloseEpisodeOutro)
    guipresenter.SetData("EpisodeOutro.Close#action", CloseEpisodeOutro)
    guipresenter.SetData("EpisodeOutro#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseEpisodeOutro },
        ])
    guipresenter.ShowDialog("EpisodeOutro", True)
            
    
def CloseEpisodeOutro(*a):    
    guipresenter.ShowDialog("EpisodeOutro", False)
    NextCareerStage()
    
#def ViewResults(*a):
#    globalvars.CurrentPlayer.SuggestLevel(guipresenter.GetData("MapCareer.Levels#Values"][guipresenter.GetData("MapCareer.Levels#Selected"][0]])
#    guipresenter.ShowDialog("MapCareer", False)
#    globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").\
#                    GetSubtag(guipresenter.GetData("MapCareer.Levels#Values"][guipresenter.GetData("MapCareer.Levels#Selected"][0]]))
#    ShowEpisodeOutro()

#------------------------------
# играть уровень...
#------------------------------

#def PlayLevelFromMap(*a):
#    globalvars.CurrentPlayer.SuggestLevel(guipresenter.GetData("MapCareer.Levels#Values"][guipresenter.GetData("MapCareer.Levels#Selected"][0]])
#    guipresenter.ShowDialog("MapCareer", False)
#    globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").\
#                    GetSubtag(guipresenter.GetData("MapCareer.Levels#Values"][guipresenter.GetData("MapCareer.Levels#Selected"][0]]))
#    PlayLevel()
#    
def PlayLevel(*a):
    globalvars.Board.Show(True)
    globalvars.Board.LaunchLevel()
    ShowGameHUD()
    ShowLevelGoals()
    
def StartPlaying(*a):
    guipresenter.ShowDialog("LevelGoals", False)
    globalvars.Board.ReallyStart()

#------------------------------
# цели уровня
#------------------------------

def ShowLevelGoals(*a):
    tmpLevelName = globalvars.CurrentPlayer.GetLevel().GetContent()
    tmpLevelParams = globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpLevelName)
    guipresenter.SetData("LevelGoals.Title#text",
            localizer.GetGameString(globalvars.CurrentPlayer.GetLevel().GetStrAttr("restaurant")) + " - " + \
            localizer.GetGameString(globalvars.CurrentPlayer.GetLevel().GetStrAttr("day")))
    guipresenter.SetData("LevelGoals.TextLevel#text", tmpLevelParams.GetStrAttr("name"))
    guipresenter.SetData("LevelGoals.TextGoal#text", str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneyGoal")))
    guipresenter.SetData("LevelGoals.TextExpert#text", str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertGoal")))
    
    tmpIntro = eval(tmpLevelParams.GetStrAttr("intro"))
    tmpLayout = { "custpic": "CustomerPicture", "bonuspic": "BonusPicture", "nopic": "NoPicture" }[tmpIntro["layout"]]
    guipresenter.SetData("LevelGoals.LevelIntro#value", tmpLayout)
    guipresenter.SetData("LevelGoals.LevelIntro."+tmpLayout+".IntroTitle#text", localizer.GetGameString(tmpIntro["title"]))
    guipresenter.SetData("LevelGoals.LevelIntro."+tmpLayout+".IntroText#text", localizer.GetGameString(tmpIntro["text"]))
    
    if tmpIntro.get("picture") != None:
        guipresenter.SetData("LevelGoals.LevelIntro."+tmpLayout+".IntroPicture#klass", tmpIntro["picture"])
        if tmpIntro.get("frno") != None:
            guipresenter.SetData("LevelGoals.LevelIntro."+tmpLayout+".IntroPicture#frno", tmpIntro["frno"])
    guipresenter.SetData("LevelGoals.Continue#action", StartPlaying)
    guipresenter.SetData("LevelGoals#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": StartPlaying },
        ])
    guipresenter.ShowDialog("LevelGoals", True)
    
#------------------------------
# игровая инфо-панель
#------------------------------

def ShowGameHUD(*a):
    guipresenter.SetData("GameHUD.Menu#action", ShowOptionsFromGame)
    if globalvars.GameSettings.GetBoolAttr("debugMode"):
        guipresenter.SetData("GameHUD#kbdCommands", [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ShowOptionsFromGame },
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_F6}], "call": DebugFinishLevel },
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_F7}], "call": DebugLastCustomer },
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_F8}], "call": DebugLoseLevel },
            ])
    else:
        guipresenter.SetData("GameHUD#kbdCommands", [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ShowOptionsFromGame },
            ])
    guipresenter.SetData("GameHUD#onActivate", UnFreezeGame)
    guipresenter.SetData("GameHUD#onDeactivate", FreezeGame)
    guipresenter.ShowDialog("GameHUD", True)

def DebugFinishLevel(*a):
    globalvars.Board.SendCommand(Cmd_DebugFinishLevel)
def DebugLastCustomer(*a):
    globalvars.Board.SendCommand(Cmd_DebugLastCustomer)
def DebugLoseLevel(*a):
    globalvars.Board.SendCommand(Cmd_DebugLoseLevel)

#обновить панель информации при старте уровня
def ResetGameHUD(*a):
    tmpSetting = globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme")
    guipresenter.SetData("GameHUD.InfoPane#klass", globalvars.ThemesInfo.GetSubtag(tmpSetting).GetStrAttr("infopane"))
    guipresenter.SetData("GameHUD.Menu#style", guipresenter.GetStyle("PushButton.HUD-Menu."+tmpSetting))
    guipresenter.SetData("GameHUD.LevelName#text", globalvars.CurrentPlayer.GetLevel().GetStrAttr("name"))

def UpdateGameHUD(*a):
    try:
        if a[0].has_key("RemainingCustomers"):
            guipresenter.SetData("GameHUD.NoPeople#text", str(a[0]["RemainingCustomers"]))
        if a[0].has_key("LevelScore"):
            guipresenter.SetData("GameHUD.Score#text", str(a[0]["LevelScore"]))
        if a[0].has_key("Expert"):
            if a[0]["Expert"]:
                guipresenter.SetData("GameHUD.GoalText#text", localizer.GetGameString("Str_HUD_ExpertText"))
                guipresenter.SetData("GameHUD.Goal#text", str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertgoal")))
            else:
                guipresenter.SetData("GameHUD.GoalText#text", localizer.GetGameString("Str_HUD_GoalText"))
                guipresenter.SetData("GameHUD.Goal#text", str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneygoal")))
    except:
        pass
    guipresenter.ShowDialog("GameHUD", True)

def UnFreezeGame(*a):
    globalvars.Board.Freeze(False)

def FreezeGame(*a):
    globalvars.Board.Freeze(True)

#------------------------------
# результаты уровня
#------------------------------

def ShowLevelResults(*a):
    #a[0] = passing flag
    #a[1] = parameters (score, expert, etc)
    
    tmpLevelName = globalvars.CurrentPlayer.GetLevel().GetContent()
    tmpLevelParams = globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpLevelName)
    
    tmpResult = (a[0] and a[1].get("expert"))*"Expert" + (a[0] and not(a[1].get("expert")))*"Passed" + (not a[0])*"Failed"
    guipresenter.SetData("LevelResults.Background#value", tmpResult)
    guipresenter.SetData("LevelResults.Buttons#value", (a[0])*"Passed" + (not a[0])*"Failed")
    guipresenter.SetData("LevelResults.Comment#text",
            localizer.GetGameString(eval(tmpLevelParams.GetStrAttr(string.lower(tmpResult)))["text"]))

    guipresenter.SetData("LevelResults.TextServed#text", str(a[1]["served"]))
    guipresenter.SetData("LevelResults.TextLost#text", str(a[1]["lost"]))
    guipresenter.SetData("LevelResults.TextEarned#text", str(a[1]["score"]))
    guipresenter.SetData("LevelResults.TextLevelPoints#text",
                str((a[0])*(globalvars.GameSettings.GetIntAttr("expertPoints")*a[1]["expert"] + \
                globalvars.GameSettings.GetIntAttr("levelPoints")*(1-a[1]["expert"]))) + \
                localizer.GetGameString("Str_LvComplete_From") + \
                str(globalvars.GameSettings.GetIntAttr("expertPoints")))
    guipresenter.SetData("LevelResults.TextRoundPoints#text",
                str(globalvars.CurrentPlayer.GetLevelParams(globalvars.LevelSettings.GetTag("Layout").GetStrAttr("theme")).GetIntAttr("points")) + \
                localizer.GetGameString("Str_LvComplete_From") + \
                str(globalvars.GameSettings.GetIntAttr("expertAll")))
    
    guipresenter.SetData("LevelResults.ExpertSign#visible", a[1]["expert"])
    tmpBest = globalvars.BestResults.GetSubtag(globalvars.CurrentPlayer.GetLevel().GetContent())
    guipresenter.SetData("LevelResults.BestSign#visible",
                (a[0] and a[1]["score"]==tmpBest.GetIntAttr("hiscore") and a[1]["score"]>0))

    guipresenter.SetData("LevelResults.Buttons.Passed.Continue#action", CloseLevelResults)
    guipresenter.SetData("LevelResults.Buttons.Failed.Restart#action", RestartLevelAfterLevelResults)
    guipresenter.SetData("LevelResults.Buttons.Failed.MainMenu#action", ExitToMenuFromLevelResults)
    if a[0]:    
        guipresenter.SetData("LevelResults#kbdCommands", [
            { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseLevelResults },
            ])
    else:
        guipresenter.SetData("LevelResults#kbdCommands", [
            { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": ExitToMenuFromLevelResults },
            { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": RestartLevelAfterLevelResults },
            ])
    ScheduleFunction(ShowLevelResultsDialog, 1500)
    
def ShowLevelResultsDialog(*a):
    guipresenter.ShowDialog("LevelResults", True)

def CloseLevelResults(*a):
    guipresenter.ShowDialog("LevelResults", False)
    tmpSetting = globalvars.LevelSettings.GetTag("Layout").GetStrAttr("theme")
    if globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting) != []:
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
        guipresenter.SetData("Cookbook#page", tmpAllSettings.index(tmpSetting))
        #guipresenter.GetData("Cookbook#from"] = "Game"
        ShowCookbook(a)
    else:
        guipresenter.ShowDialog("GameHUD", False)
        globalvars.Board.Clear()
        globalvars.Board.Show(False)
        NextCareerStage()

def RestartLevelAfterLevelResults(*a):
    guipresenter.ShowDialog("LevelResults", False)
    #globalvars.Board.Clear()
    PlayLevel()

def ExitToMenuFromLevelResults(*a):
    guipresenter.ShowDialog("LevelResults", False)
    guipresenter.ShowDialog("GameHUD", False)
    globalvars.Board.Clear()
    globalvars.Board.Show(False)
    ShowMenu()

#------------------------------
# подсказка
#------------------------------

def ShowHint(*a):
    tmpHintNode = globalvars.HintsInfo.GetSubtag(a[0])
    tmpXY = eval(tmpHintNode.GetStrAttr("xy"))
    guipresenter.SetData("Hints#x", a[1][0]+tmpXY[0])
    guipresenter.SetData("Hints#y", a[1][1]+tmpXY[1])
    guipresenter.SetData("Hints.Background#value", tmpHintNode.GetStrAttr("layout"))
    guipresenter.SetData("Hints.HintsText#text", localizer.GetGameString(tmpHintNode.GetStrAttr("text")))
    guipresenter.SetData("Hints.ShowHints#checked", globalvars.CurrentPlayer.XML.GetBoolAttr("Hints"))
    guipresenter.SetData("Hints.Continue#action", CloseHint)
    guipresenter.SetData("Hints.Close#action", CloseHint)
    guipresenter.SetData("Hints#kbdCommands", [
        { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": CloseHint },
        ])
    guipresenter.ShowDialog("Hints", True)
    #globalvars.Board.Freeze(True, False)
        
def CloseHint(*a):
    globalvars.CurrentPlayer.XML.SetBoolAttr("Hints", guipresenter.GetData("Hints.ShowHints#checked"))
    guipresenter.ShowDialog("Hints", False)


#------------------------------
# задать вопрос
#------------------------------

def Ask(*a):
    guipresenter.SetData("YesNo.Question#text", a[0])
    guipresenter.SetData("YesNo.Ok#action", CloseQuestionYes)
    guipresenter.SetData("YesNo.Cancel#action", CloseQuestionNo)
    guipresenter.SetData("YesNo#YesAction", a[1])
    guipresenter.SetData("YesNo#kbdCommands", [
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ENTER}], "call": CloseQuestionYes },
        { "condition": [{"func": oE.EvtKey, "value": scraft.Key_ESC}], "call": CloseQuestionNo },
        ])
    guipresenter.ShowDialog("Hints", False)
    guipresenter.ShowDialog("EnterName", False)
    guipresenter.ShowDialog("Pause", False)
    guipresenter.ShowDialog("YesNo", True)

def CloseQuestionYes(*a):
    guipresenter.ShowDialog("YesNo", False)
    guipresenter.GetData("YesNo#YesAction")()

def CloseQuestionNo(*a):
    guipresenter.ShowDialog("YesNo", False)

#------------------------------
# окно паузы
#------------------------------

def SetPause(flag):
    if flag:
        guipresenter.SetData("Pause.Unpause#action", UnPause)
        guipresenter.SetData("Pause#kbdCommands", [
            { "condition": [{"func": oE.EvtIsKeyDown, "value": True}], "call": UnPause },
        ])
        guipresenter.ShowDialog("Hints", False)
        guipresenter.ShowDialog("EnterName", False)
        guipresenter.ShowDialog("YesNo", False)
        guipresenter.ShowDialog("Pause", True)
    else:
        guipresenter.ShowDialog("Pause", False)
    musicsound.Pause(flag)

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
        
    guipresenter.CreateEffect("GameHUD", style, { "text": text, "crd": crd })
            
#------------------------------
# отображение других эффектов
#------------------------------
def ShowGameEffect(effectname, crd):
    guipresenter.CreateEffect("GameHUD", effectname, { "crd": crd })

#------------------------------
# функция для установки специфических для игры параметров курсора
#------------------------------
def SetCursorState(param):
    if guipresenter.GetData("Cursor#params") == None:
        guipresenter.SetData("Cursor#params", {})
    tmpData = guipresenter.GetData("Cursor#params")
    for tmp in param.keys():
        tmpData[tmp] = param[tmp]
    guipresenter.SetData("Cursor#params", tmpData)
    if param.has_key("button"):
        cursor.SetState(param["button"])
        
    if param.has_key("state"):
        guipresenter.SetData("Cursor.Token#value", param["state"])
    if param.get("state") == "Token":
        if param.has_key("tokentype") and param.has_key("tokenno"):
            guipresenter.SetData("Cursor.Token.Token.Token#klass",
                    globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(param["tokentype"]).GetStrAttr("iconSrc"))
            guipresenter.SetData("Cursor.Token.Token.Number#text", str(param["tokenno"]))
    elif param.get("state") == "Tool":
        if param.has_key("tooltype"):
            guipresenter.SetData("Cursor.Token.Tool.Tool#klass",
                    globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(param["tooltype"]).GetStrAttr("src"))
    if param.has_key("red"):
        guipresenter.SetData("Cursor.Blocker#value", str(param["red"]))

def GetCursorState(paramName):
    return guipresenter.GetData("Cursor#params").get(paramName)
