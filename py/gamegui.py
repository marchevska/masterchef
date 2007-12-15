#!/usr/bin/env python
# -*- coding: cp1251 -*-

import globalvars
from constants import *
from teggo.games import localizer

Const_TotalHelpPages = 4

#отображение главного меню        
def ShowMenu(*a):
    globalvars.GuiPresenter.data["MainMenu.Play#action"] = PlayGame
    globalvars.GuiPresenter.data["MainMenu.Players#action"] = ShowPlayers
    globalvars.GuiPresenter.data["MainMenu.Options#action"] = ShowOptions
    globalvars.GuiPresenter.data["MainMenu.Rules#action"] = ShowRules
    globalvars.GuiPresenter.data["MainMenu.Hiscores#action"] = ShowHiscoresDialog
    globalvars.GuiPresenter.data["MainMenu.Quit#action"] = QuitGame

    #если у игрока не разлочен ни один эпизод, то кулинарная книга недоступна
    tmpUnlockedSettings = filter(lambda x: \
                            globalvars.CurrentPlayer.GetLevelParams(x).GetBoolAttr("unlocked"),
                            eval(globalvars.GameSettings.GetStrAttr("settings")))
    if tmpUnlockedSettings == []:
        globalvars.GuiPresenter.data["MainMenu.Cookbook#disabled"] = True
    else:
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
        globalvars.GuiPresenter.BringToFront("MainMenu", True)

    
def ShowOptions(*a):
    pass

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
        if globalvars.GuiPresenter.data["Rules#page"] == Const_TotalHelpPages - 1:
            globalvars.GuiPresenter.data["Rules.Next#disabled"] = True
        else:
            globalvars.GuiPresenter.data["Rules.Next#disabled"] = False
            globalvars.GuiPresenter.data["Rules.Next#action"] = RulesNextPage
        globalvars.GuiPresenter.ShowDialog("Rules", True)
        globalvars.GuiPresenter.BringToFront("Rules", True)
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
        if globalvars.GuiPresenter.data["Rules#page"] < Const_TotalHelpPages - 1:
            globalvars.GuiPresenter.data["Rules#page"] += 1
    except:
        pass
    ShowRules()

def ShowCookbook(*a):
    try:
        if not globalvars.GuiPresenter.data.get("Cookbook#page"):
            globalvars.GuiPresenter.data["Cookbook#page"] = 0
        #коррекция в случае переключения на другой профиль игрока:
        #не показывать не разлоченные страницы книги
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
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
        #tmpNewRecipes = globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting)
        #if len(tmpNewRecipes) > 0:
        #    PopupText(defs.GetGameString("Str_NewRecipesLearned"),
        #            "domcasual-30-yellow", 400, 300,
        #            InPlaceMotion(),
        #            BounceTransp([(0, 30), (0.3, 0), (1.5, 0), (2.0, 100)]),
        #            BounceScale([(0, 50), (0.3, 100), (1.5, 120), (2.0, 150)]),
        #            2000, PState_Cookbook)
        #    globalvars.Musician.PlaySound("cookbook.newrecipe")
            
        for i in range(self.TotalRecipesOnPage):
            self.CookbookDialog["Static"]["Recipe"+str(i+1)].x = globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeX")
            self.CookbookDialog["Static"]["Recipe"+str(i+1)].y = globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeY")
            if globalvars.CurrentPlayer.GetLevelParams(tmpRecipes[i]).GetBoolAttr("unlocked"):
                self.CookbookDialog["Static"]["Recipe"+str(i+1)].ChangeKlassTo(globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("badge"))
                #if tmpRecipes[i] in tmpNewRecipes:
                #    globalvars.CurrentPlayer.SetLevelParams(tmpRecipes[i], { "seen": True })
                #    
                #    #эффект обводки контура
                #    tmpCopy = map(lambda x: (-x[0], x[1]), list(Crd_CookbookStickerContourHalf))
                #    tmpCopy.reverse()
                #    tmpContour = (list(Crd_CookbookStickerContourHalf) + tmpCopy)
                #    #движение с постоянной скоростью:
                #    tmpTimes = [Time_TrailInitialDelay] + map(lambda ii: \
                #            math.sqrt((tmpContour[ii][0]-tmpContour[ii+1][0])**2 + (tmpContour[ii][1]-tmpContour[ii+1][1])**2)/Crd_CookbookStickerTrailSpeed,
                #            range(len(tmpContour)-1))
                #    tmpTimesSums = map(lambda x: reduce(lambda a,b: a+b, tmpTimes[0:x+1],0), range(len(tmpContour)))
                #    tmp = map(lambda ii: (tmpTimesSums[ii],
                #                        tmpContour[ii][0] + self.CookbookDialog["Static"]["Recipe"+str(i+1)].x,
                #                        tmpContour[ii][1] + self.CookbookDialog["Static"]["Recipe"+str(i+1)].y),
                #                        range(len(tmpContour)))
                #    DrawTrailedContour({"klass": "star", "no": 20, "layer": Layer_CookbookBtnTxt-1,
                #            "incTrans": 4, "incScale": 4, "delay": 15},
                #            tmp, PState_Cookbook)
                #    
                #else:
                #    self.CookbookDialog["Static"]["Recipe"+str(i+1)].transparency = 0
            else:
                self.CookbookDialog["Static"]["Recipe"+str(i+1)].ChangeKlassTo(globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("emptyBadge"))
        
        #кнопки пролистывания ниги
        #если книга открыта из главного меню
        if self.NextState == PState_None:
            self.CookbookDialog["Buttons"]["CookbookClose"].SetState(ButtonState_Up)
            self.CookbookDialog["Buttons"]["CookbookPrev"].Show((no>0))
            if no>0:
                if globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no-1]).GetBoolAttr("unlocked"):
                    self.CookbookDialog["Buttons"]["CookbookPrev"].SetState(ButtonState_Up)
                else:
                    self.CookbookDialog["Buttons"]["CookbookPrev"].SetState(ButtonState_Inert)
            self.CookbookDialog["Buttons"]["CookbookNext"].Show((no<len(tmpAllSettings)-1))
            if no<len(tmpAllSettings)-1:
                if globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no+1]).GetBoolAttr("unlocked"):
                    self.CookbookDialog["Buttons"]["CookbookNext"].SetState(ButtonState_Up)
                else:
                    self.CookbookDialog["Buttons"]["CookbookNext"].SetState(ButtonState_Inert)
            self.CookbookDialog["Buttons"]["CookbookContinue"].Show(False)
        #иначе - книга открыта после прохождения уровня
        else:
            self.CookbookDialog["Buttons"]["CookbookClose"].SetState(ButtonState_Inert)
            self.CookbookDialog["Buttons"]["CookbookContinue"].Show(True)
            self.CookbookDialog["Buttons"]["CookbookPrev"].Show(False)
            self.CookbookDialog["Buttons"]["CookbookNext"].Show(False)
    except:
        pass


def ShowHelp(*a):
    pass

#отображение рекордов
#данные считываются из файла
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
    globalvars.ExitFlag = True

def PlayGame(*a):
    pass

def SetPause(flag):
    if flag:
        globalvars.GuiPresenter.ShowDialog("Pause", True)
        globalvars.GuiPresenter.BringToFront("Pause", flag)
    else:
        globalvars.GuiPresenter.ShowDialog("Pause", False)
        
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

