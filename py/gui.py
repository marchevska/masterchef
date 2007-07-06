#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
ГУИ
"""

import sys
import string
import scraft
from scraft import engine as oE
from configconst import *
from guiconst import *
from guielements import *
from strings import *
from customer import *
import defs
import playerlist
import config
import globalvars
import traceback
from random import shuffle

class Gui(scraft.Dispatcher):
    def __init__(self):
        globalvars.Frozen = False
        globalvars.LastCookie = Cmd_None
        self.LastCookie = Cmd_None
        self.NextStateTime = 0
        self.CurrentHelpPage = 0
        self.TotalHelpPages = 1
        self.FirstPlayer = 0
        self.SelectedPlayer = ""                #имя выбранного игрока
        self.SelectedLevel = ""                 #название выбранного уровня (имя файла)
        self.TotalPlayersOnScreen = 6
        self.TotalCareerLevels = 0
        self.TotalRecipesOnPage = 12
        self.MaxNewRecipes = 12
        self.MaxPeopleOnLevel = 8
        self.MaxPeopleOnOutro = 4
        self.CurrentCookbookPage = 0
        self.NextState = PState_None
        self.SavedOptions = []
           
        self.GraySprite = MakeSprite("gray.screen", Layer_Background+1)
            
        #--------------
        # логотипы разработчика и издателя
        #--------------
        self.DevLogo = { "Static": {}, "Text": {}, "Buttons": {} }
        self.DevLogo["Buttons"]["Back"] = PushButton("",
                self, Cmd_DevLogoClose, PState_DevLogo, u"developer-logo", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.PubLogo = { "Static": {}, "Text": {}, "Buttons": {} }
        self.PubLogo["Buttons"]["Back"] = PushButton("",
                self, Cmd_PubLogoClose, PState_PubLogo, u"publisher-logo", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
           
        #--------------
        # главное меню
        #--------------
        self.MainMenuDialog = { "Static": {}, "Text": {}, "Buttons": {}, "Animations": {} }
        self.MainMenuDialog["Static"]["Back"] = MakeSimpleSprite(u"mainmenu-background", Layer_Background)
        self.MainMenuDialog["Static"]["Tablet"] = MakeSprite("mainmenu.tablet", Layer_Static,
                { "x": 675, "y": 100, "hotspot": scraft.HotspotCenter } )
        self.MainMenuDialog["Static"]["JaneEyes"] = MakeSprite("mainmenu.jane.eyes", Layer_BtnText,
                { "x": 190, "y": 220 } )
        self.MainMenuDialog["Animations"]["JaneEyes"] = CustomersAnimator(self.MainMenuDialog["Static"]["JaneEyes"],
                globalvars.CustomerAnimations.GetSubtag("animation.mainmenu.janeeyes"))
        self.MainMenuDialog["Animations"]["JaneEyes"].SetState("None")
        self.MainMenuDialog["Animations"]["JaneEyes"].Freeze(True)
        self.MainMenuDialog["Static"]["Vapor"] = MakeSprite("mainmenu.vapor", Layer_BtnText,
                { "x": 320, "y": 350 } )
        self.MainMenuDialog["Animations"]["Vapor"] = CustomersAnimator(self.MainMenuDialog["Static"]["Vapor"],
                globalvars.CustomerAnimations.GetSubtag("animation.mainmenu.vapor"))
        self.MainMenuDialog["Animations"]["Vapor"].SetState("None")
        self.MainMenuDialog["Animations"]["Vapor"].Freeze(True)
        self.MainMenuDialog["Buttons"]["PlayCareer"] = PushButton("PlayCareer",
                self, Cmd_Menu_PlayCareer, PState_MainMenu,
                "mainmenu.green-button", [0, 1, 2], 
                Layer_BtnText, 675, 230, 210, 50,
                Str_Menu_PlayCareer, ["mainmenu.domcasual", "mainmenu.domcasual", "mainmenu.domcasual.down"])
        #self.MainMenuDialog["Buttons"]["PlayEndless"] = PushButton("PlayEndless",
        #        self, Cmd_Menu_PlayEndless, PState_MainMenu,
        #        "mainmenu-career-endless-button", [1, 3, 5, 7], 
        #        Layer_BtnText, 495, 215, 130, 170)
        self.MainMenuDialog["Buttons"]["Options"] = PushButton("Options",
                self, Cmd_Menu_Options, PState_MainMenu,
                "mainmenu.yellow-button", [0, 1, 2], 
                Layer_BtnText, 675, 275, 200, 40,
                Str_Menu_Options, ["mainmenu.domcasual", "mainmenu.domcasual", "mainmenu.domcasual.down"])
        self.MainMenuDialog["Buttons"]["Help"] = PushButton("Help",
                self, Cmd_Menu_Rules, PState_MainMenu,
                "mainmenu.yellow-button", [0, 1, 2], 
                Layer_BtnText, 675, 315, 200, 40,
                Str_Menu_Rules, ["mainmenu.domcasual", "mainmenu.domcasual", "mainmenu.domcasual.down"])
        self.MainMenuDialog["Buttons"]["Cookbook"] = PushButton("Cookbook",
                self, Cmd_Menu_Cookbook, PState_MainMenu,
                "mainmenu.yellow-button", [0, 1, 2], 
                Layer_BtnText, 675, 355, 200, 40,
                Str_Menu_Cookbook, ["mainmenu.domcasual", "mainmenu.domcasual", "mainmenu.domcasual.down"])
        self.MainMenuDialog["Buttons"]["Quit"] = PushButton("Quit",
                self, Cmd_Menu_Quit, PState_MainMenu,
                "mainmenu.yellow-button", [0, 1, 2], 
                Layer_BtnText, 675, 395, 200, 40,
                Str_Menu_Quit, ["mainmenu.domcasual", "mainmenu.domcasual", "mainmenu.domcasual.down"])
        self.MainMenuDialog["Buttons"]["Players"] = PushButton("Players",
                self, Cmd_Menu_Players, PState_MainMenu,
                "mainmenu-players-button", [0, 1, 2, 3], 
                Layer_BtnText, 675, 160, 190, 30,
                Str_Menu_Players, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.MainMenuDialog["Text"]["WelcomeMessage"] = MakeSprite("domcasual-11", Layer_BtnText,
                { "x": 600, "y": 125, "cfilt-color": 0xFF8000 } )
        
        #---------
        # справка
        #---------
        self.RulesDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.RulesDialog["Static"]["Back"] = MakeSimpleSprite(u"help-page1", Layer_Background)
        self.RulesDialog["Buttons"]["HelpPrev"] = PushButton("HelpPrev",
                self, Cmd_HelpPrev, PState_Help,
                u"button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 100, 570, 120, 40,
                Str_HelpPrev, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.RulesDialog["Buttons"]["HelpNext"] = PushButton("HelpNext",
                self, Cmd_HelpNext, PState_Help,
                u"button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 260, 570, 120, 40,
                Str_HelpNext, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.RulesDialog["Buttons"]["HelpClose"] = PushButton("HelpClose",
                self, Cmd_HelpClose, PState_Help,
                u"button-4st", [0, 1, 2], 
                Layer_BtnText, 700, 570, 120, 40,
                Str_HelpClose, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        
        #----------------
        # кулинарная книга
        #----------------
        self.CookbookDialog = {"Static": {}, "Text": {}, "Buttons": {}, "Animations": {}}
        self.CookbookDialog["Static"]["Back"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBg)
        self.CookbookDialog["Static"]["Logo"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBtnTxt,
                                                { "x": 50, "y": 50 })
        self.CookbookDialog["Buttons"]["CookbookClose"] = PushButton("CookbookClose",
                self, Cmd_CookbookClose, PState_Cookbook,
                u"cookbook.close-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 390, 527, 100, 130)
        self.CookbookDialog["Buttons"]["CookbookContinue"] = PushButton("CookbookContinue",
                self, Cmd_CookbookClose, PState_Cookbook,
                u"continue-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 600, 550, 140, 50)
        self.CookbookDialog["Buttons"]["CookbookNext"] = PushButton("CookbookNext",
                self, Cmd_CookbookNext, PState_Cookbook,
                u"cookbook.next-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 700, 550, 100, 130)
        self.CookbookDialog["Buttons"]["CookbookPrev"] = PushButton("CookbookPrev",
                self, Cmd_CookbookPrev, PState_Cookbook,
                u"cookbook.prev-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 100, 550, 100, 130)
        for i in range(self.TotalRecipesOnPage):
            self.CookbookDialog["Static"]["Recipe"+str(i+1)] = MakeSprite("$spritecraft$dummy$", Layer_PopupBtnTxt)
        for i in range(self.MaxNewRecipes):
            self.CookbookDialog["Static"]["NewRecipe"+str(i+1)] = MakeSprite("cookbook.new-recipe", Layer_PopupBtnTxt-1)
            self.CookbookDialog["Animations"]["NewRecipe"+str(i+1)] = \
                            CustomersAnimator(self.CookbookDialog["Static"]["NewRecipe"+str(i+1)],
                            globalvars.CustomerAnimations.GetSubtag("animation.cookbook.new-recipe"))
            self.CookbookDialog["Animations"]["NewRecipe"+str(i+1)].SetState("None")
            self.CookbookDialog["Animations"]["NewRecipe"+str(i+1)].Freeze(True)
        
        #----------------
        # список игроков
        #----------------
        self.PlayersDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.PlayersDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.PlayersDialog["Text"]["Title"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Players_Title)
        self.PlayersDialog["Buttons"]["Remove"] = PushButton("PlayersRemove",
                self, Cmd_PlayersRemove, PState_Players,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 260, 470, 120, 40,
                Str_PlayersRemove, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.PlayersDialog["Buttons"]["Ok"] = PushButton("PlayersOk",
                self, Cmd_PlayersOk, PState_Players,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 400, 470, 120, 40,
                Str_PlayersOk, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.PlayersDialog["Buttons"]["Cancel"] = PushButton("PlayersCancel",
                self, Cmd_PlayersCancel, PState_Players,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 540, 470, 120, 40,
                Str_PlayersCancel, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.PlayersDialog["Buttons"]["Up"] = PushButton("PlayersUp",
                self, Cmd_PlayersUp, PState_Players,
                u"players-arrow-up", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 520, 250, 30, 30)
        self.PlayersDialog["Buttons"]["Down"] = PushButton("PlayersDown",
                self, Cmd_PlayersDown, PState_Players,
                u"players-arrow-down", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 520, 410, 30, 30)
        self.PlayersDialog["Buttons"]["New"] = PushButton("NewPlayer",
                self, Cmd_PlayersNew, PState_Players,
                u"mainmenu.green-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 400, 210, 210, 50,
                Str_PlayersNew, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        for i in range(self.TotalPlayersOnScreen):
            self.PlayersDialog["Buttons"]["Player_"+str(i)] = PushButton("PlayerNo"+str(i),
                self, Cmd_PlayersSelect+i, PState_Players,
                u"players-select-button", [0, 1, 2, 4, 3], 
                Layer_PopupBtnTxt, 390, 250 + 32 * i, 220, 30,
                "", [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-up", u"domcasual-10-up"])
        
        #------------
        # ввод имени
        #------------
        self.EnterNameDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.EnterNameDialog["Static"]["Back"] = MakeSimpleSprite(u"2nd-popup-background", Layer_2ndPopupBg)
        self.EnterNameDialog["Text"]["Title"] = MakeTextSprite(u"domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 250,
                                                    scraft.HotspotCenterTop, Str_EnterName_Title)
        self.EnterNameDialog["Static"]["TextCursor"] = MakeSimpleSprite(u"textcursor", Layer_2ndPopupBtnTxt, 400, 290)
        self.EnterNameDialog["Static"]["TextCursor"].AnimateLoop(2)
        self.EnterNameDialog["Buttons"]["Ok"] = PushButton("EnterNameOk",
                self, Cmd_EnterNameOk, PState_EnterName,
                u"button-4st", [0, 1, 2, 3], 
                Layer_2ndPopupBtnTxt, 330, 342, 120, 40,
                Str_EnterNameOk, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.EnterNameDialog["Buttons"]["Cancel"] = PushButton("EnterNameCancel",
                self, Cmd_EnterNameCancel, PState_EnterName,
                u"button-4st", [0, 1, 2, 3], 
                Layer_2ndPopupBtnTxt, 470, 342, 120, 40,
                Str_EnterNameCancel, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.EnterNameDialog["Text"]["Name"] = MakeTextSprite(u"domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 290)
        self.EnterNameDialog["Text"]["NameErrors"] = MakeTextSprite(u"domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 320)
        self.EnterNameDialog["Text"]["NameErrors"].xScale, self.EnterNameDialog["Text"]["NameErrors"].yScale = 50,50
        
        #------------------
        # старт уровня
        #------------------
        self.LevelGoalsDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.LevelGoalsDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.LevelGoalsDialog["Text"]["Title"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                scraft.HotspotCenter, Str_LvGoals_Title)
        self.LevelGoalsDialog["Text"]["Text0"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 220)
        self.LevelGoalsDialog["Text"]["Text1"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 300, 270)
        self.LevelGoalsDialog["Text"]["Text2"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 500, 270)
        self.LevelGoalsDialog["Text"]["Text3"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 300, 350)
        self.LevelGoalsDialog["Text"]["Text4"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 500, 350)
        self.LevelGoalsDialog["Buttons"]["Play"] = PushButton("PlayLevel",
                self, Cmd_LvGoalsPlay, PState_StartLevel,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 470, 120, 40,
                Str_LvGoalsPlay, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        
        #------------------
        # уровень завершен
        #------------------
        self.LevelCompleteDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.LevelCompleteDialog["Static"]["Back"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBg)
        self.LevelCompleteDialog["Text"]["Title"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 470, 130,
                                                                   scraft.HotspotCenter, Str_LvComplete_Title)
        self.LevelCompleteDialog["Text"]["LabelServed"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 565, "y": 207, "hotspot": scraft.HotspotRightCenter, "text": Str_LvComplete_Served })
        self.LevelCompleteDialog["Text"]["LabelLost"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 565, "y": 242, "hotspot": scraft.HotspotRightCenter, "text": Str_LvComplete_Lost })
        self.LevelCompleteDialog["Text"]["LabelEarned"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 565, "y": 277, "hotspot": scraft.HotspotRightCenter, "text": Str_LvComplete_Score })
        
        self.LevelCompleteDialog["Text"]["Text3"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 300, 370)
        self.LevelCompleteDialog["Text"]["Text4"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 500, 370)
        self.LevelCompleteDialog["Text"]["Text5"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 420)
        
        self.LevelCompleteDialog["Text"]["TextServed"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 580, "y": 207, "hotspot": scraft.HotspotLeftCenter })
        self.LevelCompleteDialog["Text"]["TextLost"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 580, "y": 242, "hotspot": scraft.HotspotLeftCenter })
        self.LevelCompleteDialog["Text"]["TextEarned"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 580, "y": 277, "hotspot": scraft.HotspotLeftCenter })
        
        self.LevelCompleteDialog["Buttons"]["Continue"] = PushButton("LvCompleteNextLevel",
                self, Cmd_LvCompleteNextLevel, PState_NextLevel,
                "continue-button", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 450, 140, 50)
        self.LevelCompleteDialog["Buttons"]["Restart"] = PushButton("LvCompleteRestart",
                self, Cmd_LvCompleteRestart, PState_NextLevel,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 400, 120, 40,
                Str_LvCompleteRestart, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.LevelCompleteDialog["Buttons"]["No"] = PushButton("LvCompleteMainMenu",
                self, Cmd_LvCompleteMainMenu, PState_NextLevel,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 450, 120, 40,
                Str_LvCompleteMainMenu, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        
        #---------------
        # игра окончена
        #---------------
        self.GameOverDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.GameOverDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.GameOverDialog["Text"]["Title"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_GameOver_Title)
        self.GameOverDialog["Buttons"]["Hiscores"] = PushButton("GameOverHiscores",
                self, Cmd_GameOverHiscores, PState_GameOver,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 470, 120, 40,
                Str_GameOverHiscores, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.GameOverDialog["Buttons"]["MainMenu"] = PushButton("GameOverMainMenu",
                self, Cmd_GameOverMainMenu, PState_GameOver,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 460, 470, 120, 40,
                Str_GameOverMainMenu, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.GameOverDialog["Text"]["Message"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 320, 200)
        
        #---------
        # данетка
        #---------
        self.YesNoDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.YesNoDialog["Static"]["Back"] = MakeSimpleSprite(u"2nd-popup-background", Layer_2ndPopupBg)
        self.YesNoDialog["Text"]["QuestionText"] = MakeTextSprite(u"domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 250, scraft.HotspotCenterTop)
        self.YesNoDialog["Buttons"]["Yes"] = PushButton("Yes",
                self, Cmd_Yes, PState_YesNo,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 330, 342, 120, 40,
                Str_Yes, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.YesNoDialog["Buttons"]["No"] = PushButton("No",
                self, Cmd_No, PState_YesNo,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 470, 342, 120, 40,
                Str_No, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        
        #---------------
        # Yes-No-Cancel
        #---------------
        self.YesNoCancelDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.YesNoCancelDialog["Static"]["Back"] = MakeSimpleSprite(u"2nd-popup-background", Layer_2ndPopupBg)
        self.YesNoCancelDialog["Text"]["QuestionText"] = MakeTextSprite(u"domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 250, scraft.HotspotCenterTop)
        self.YesNoCancelDialog["Buttons"]["Yes"] = PushButton("Yes",
                self, Cmd_YncYes, PState_YesNoCancel,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 260, 342, 120, 40,
                Str_Yes, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.YesNoCancelDialog["Buttons"]["No"] = PushButton("No",
                self, Cmd_YncNo, PState_YesNoCancel,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 400, 342, 120, 40,
                Str_No, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.YesNoCancelDialog["Buttons"]["Cancel"] = PushButton("Cancel",
                self, Cmd_YncCancel, PState_YesNoCancel,
                u"button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 540, 342, 120, 40,
                Str_Cancel, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        
        #-------
        # опции
        #-------
        self.OptionsDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.OptionsDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.OptionsDialog["Text"]["Title"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Options_Title)
        self.OptionsDialog["Text"]["Label_Sound"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 300, 230,
                                                                   scraft.HotspotCenter, Str_Options_LabelSound)
        self.OptionsDialog["Text"]["Label_Music"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 300, 280,
                                                                   scraft.HotspotCenter, Str_Options_LabelMusic)
        self.OptionsDialog["Buttons"]["Slider_Sound"] = Slider("SliderSound", globalvars.GameConfig, 'Sound',
                PState_Options, u"options-slider", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 250, 250, 40, (310, 490), (250, 250), u"slider-background")
        self.OptionsDialog["Buttons"]["Slider_Music"] = Slider("SliderMusic", globalvars.GameConfig, 'Music',
                PState_Options, u"options-slider", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 300, 250, 40, (310, 490), (300, 300), u"slider-background")
        self.OptionsDialog["Text"]["Label_Mute"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 335, 343,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelMute)
        self.OptionsDialog["Text"]["Label_Hints"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 335, 373,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelHints)
        self.OptionsDialog["Text"]["Label_Fullscreen"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 335, 403,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelFullscreen)
        self.OptionsDialog["Buttons"]["Mute"] = PushButton("OptionsMute",
                self, Cmd_OptionsMute, PState_Options,
                u"options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 340, 30, 30)
        self.OptionsDialog["Buttons"]["Hints"] = PushButton("OptionsHints",
                self, Cmd_OptionsHints, PState_Options,
                u"options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 370, 30, 30)
        self.OptionsDialog["Buttons"]["Fullscreen"] = PushButton("OptionsFullscreen",
                self, Cmd_OptionsFullscreen, PState_Options,
                u"options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 400, 30, 30)
        self.OptionsDialog["Static"]["Galka_Mute"] = MakeSimpleSprite(u"options-galka", Layer_PopupBtnTxt2, 320, 340)
        self.OptionsDialog["Static"]["Galka_Hints"] = MakeSimpleSprite(u"options-galka", Layer_PopupBtnTxt2, 320, 370)
        self.OptionsDialog["Static"]["Galka_Fullscreen"] = MakeSimpleSprite(u"options-galka", Layer_PopupBtnTxt2, 320, 400)
        self.OptionsDialog["Buttons"]["Ok"] = PushButton("OptionsOk",
                self, Cmd_OptionsOk, PState_Options,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 400, 470, 120, 40,
                Str_OptionsOk, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        #self.OptionsDialog["Buttons"]["Cancel"] = PushButton("Cmd_OptionsCancel",
        #        self, Cmd_OptionsCancel, PState_Options,
        #        u"button-4st", [0, 1, 2], 
        #        Layer_PopupBtnTxt, 460, 470, 120, 40,
        #        Str_OptionsCancel, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.OptionsDialog["Buttons"]["Resume"] = PushButton("OptionsResume",
                self, Cmd_IGM_Resume, PState_Options,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 240, 470, 120, 40,
                Str_OptionsResume, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        self.OptionsDialog["Buttons"]["Restart"] = PushButton("OptionsRestart",
                self, Cmd_IGM_Restart, PState_Options,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 400, 470, 120, 40,
                Str_OptionsRestart, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.OptionsDialog["Buttons"]["EndGame"] = PushButton("OptionsEndGame",
                self, Cmd_IGM_EndGame, PState_Options,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 560, 470, 120, 40,
                Str_OptionsEndGame, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        
        #---------
        # рекорды
        #---------
        self.HiscoresDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.HiscoresDialog["Static"]["Back"] = MakeSimpleSprite(u"popup-background", Layer_PopupBg)
        self.HiscoresDialog["Text"]["Title"] = MakeTextSprite(u"domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Hiscores_Title)
        self.HiscoresDialog["Buttons"]["Reset"] = PushButton("HiscoresReset",
                self, Cmd_HiscoresReset, PState_Hiscores,
                u"button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 330, 500, 120, 40,
                Str_HiscoresReset, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.HiscoresDialog["Buttons"]["Close"] = PushButton("HiscoresClose",
                self, Cmd_HiscoresClose, PState_Hiscores,
                u"button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 470, 500, 120, 40,
                Str_HiscoresClose, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down"])
        for i in range(Max_Scores):
            self.HiscoresDialog["Text"]["Name_"+str(i)] = MakeTextSprite(u"domcasual-10-up",
                Layer_PopupBtnTxt, 280, 220 + 30* i, scraft.HotspotLeftCenter)
            self.HiscoresDialog["Text"]["Score_"+str(i)] = MakeTextSprite(u"domcasual-10-up",
                Layer_PopupBtnTxt, 520, 220 + 30* i, scraft.HotspotRightCenter)
        
        #-------
        # экран с комиксом
        #-------
        self.ComicScreen = {"Static": {}, "Text": {}, "Buttons": {}}
        self.ComicScreen["Buttons"]["Back"] = PushButton("",
                self, Cmd_ComicsNext, PState_Comics, u"$spritecraft$dummy$", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.ComicScreen["Buttons"]["Next"] = PushButton("ComicsNext",
                self, Cmd_ComicsNext, PState_Comics,
                u"comics.next-button", [0, 1, 2, 3], 
                Layer_BtnText, 760, 550, 80, 100)
        
        #-------
        # вводный экран
        #-------
        self.IntroScreen = {"Static": {}, "Text": {}, "Buttons": {}}
        self.IntroScreen["Buttons"]["Back"] = PushButton("",
                self, Cmd_IntroNext, PState_Intro, "$spritecraft$dummy$", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.IntroScreen["Buttons"]["Next"] = PushButton("IntroNext",
                self, Cmd_IntroNext, PState_Intro,
                "continue-button", [0, 1, 2], 
                Layer_BtnText, 330, 555, 140, 50)
        self.IntroScreen["Static"]["Logo"] = MakeSimpleSprite("intro.logo", Layer_Static, 230, 35)
        self.IntroScreen["Text"]["Title"] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 360, "y": 35, "hotspot": scraft.HotspotCenter } )
        self.IntroScreen["Static"]["IntroPane"] = MakeSimpleSprite("$spritecraft$dummy$", Layer_Static, 490, 18)
        self.IntroScreen["Static"]["Presenter"] = MakeSimpleSprite("comics.presenter", Layer_BtnText, 460, 520)
        self.IntroScreen["Static"]["Balloon"] = MakeSimpleSprite("intro.balloon", Layer_Static, 270, 370)
        self.IntroScreen["Text"]["Competitors"] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 640, "y": 270, "hotspot": scraft.HotspotCenter, "text": Str_IntroCompetitors } )
        for i in range(self.MaxPeopleOnLevel):
            self.IntroScreen["Static"]["Character"+str(i)] = MakeSimpleSprite("$spritecraft$dummy$", Layer_BtnText,
                                                    Crd_CharIntroPositions[i][0], Crd_CharIntroPositions[i][1])
            self.IntroScreen["Text"]["Character"+str(i)] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 640, "y": 340+25*i, "hotspot": scraft.HotspotCenter } )
        
        #-------
        # завершение уровня
        #-------
        self.OutroScreen = {"Static": {}, "Text": {}, "Buttons": {}}
        self.OutroScreen["Buttons"]["Back"] = PushButton("",
                self, Cmd_OutroNext, PState_Outro, "$spritecraft$dummy$", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.OutroScreen["Buttons"]["Next"] = PushButton("IntroNext",
                self, Cmd_OutroNext, PState_Outro,
                "continue-button", [0, 1, 2], 
                Layer_BtnText, 650, 570, 140, 50)
        self.OutroScreen["Static"]["Logo"] = MakeSimpleSprite("outro.bg-pane", Layer_BtnText, 230, 35)
        self.OutroScreen["Text"]["Title"] = MakeSprite("domcasual-10-up", Layer_BtnText-1,
                { "x": 230, "y": 35, "hotspot": scraft.HotspotCenter } )
        self.OutroScreen["Text"]["Speech"] = MakeSprite("domcasual-10-up", Layer_BtnText-1,
                { "x": 220, "y": 440, "hotspot": scraft.HotspotCenter } )
        self.OutroScreen["Static"]["IntroPane"] = MakeSimpleSprite("$spritecraft$dummy$", Layer_Static, 490, 18)
        self.OutroScreen["Static"]["Separator"] = MakeSimpleSprite("outro.separator", Layer_Static-1, 650, 408)
        self.OutroScreen["Static"]["Presenter"] = MakeSimpleSprite("comics.presenter", Layer_BtnText, 460, 420)
        self.OutroScreen["Static"]["Balloon"] = MakeSimpleSprite("outro.balloon", Layer_Static, 220, 440)
        self.OutroScreen["Text"]["Competitors"] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 580, "y": 270, "hotspot": scraft.HotspotCenter, "text": Str_OutroCompetitors } )
        self.OutroScreen["Text"]["Points"] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 700, "y": 270, "hotspot": scraft.HotspotCenter, "text": Str_OutroPoints } )
        for i in range(self.MaxPeopleOnOutro):
            self.OutroScreen["Static"]["Character"+str(i)] = MakeSprite("$spritecraft$dummy$", Layer_Static-1)
            self.OutroScreen["Static"]["Medallion"+str(i)] = MakeSprite("$spritecraft$dummy$", Layer_Static-1,
                                    { "parent": self.OutroScreen["Static"]["Character"+str(i)],
                                    "x":0, "y":-200, "hotspot": scraft.HotspotCenter })
            self.OutroScreen["Static"]["Light"+str(i)] = MakeSprite("$spritecraft$dummy$", Layer_Static,
                                    { "parent": self.OutroScreen["Static"]["Character"+str(i)], "x":0, "y":40 })
            self.OutroScreen["Text"]["Number"+str(i)] = MakeSprite("domcasual-20-orange", Layer_Static-2,
                                    { "parent": self.OutroScreen["Static"]["Character"+str(i)],
                                    "x": 0, "y": -200, "hotspot": scraft.HotspotCenter } )
            self.OutroScreen["Text"]["Name"+str(i)] = MakeSprite("mainmenu.domcasual", Layer_Static-2,
                                    { "parent": self.OutroScreen["Static"]["Character"+str(i)],
                                    "x": 0, "y": -170, "hotspot": scraft.HotspotCenter } )
        for i in range(self.MaxPeopleOnLevel):
            self.OutroScreen["Text"]["Character"+str(i)] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 600, "y": 340+25*i, "hotspot": scraft.HotspotCenter } )
            self.OutroScreen["Text"]["Score"+str(i)] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 720, "y": 340+25*i, "hotspot": scraft.HotspotCenter } )
        
        #-------
        # карта карьерного режима
        #-------
        self.MapCareerDialog = {"Static": {}, "Text": {}, "Buttons": {}, "Animations": {}}
        self.MapCareerDialog["Static"]["Back"] = MakeSimpleSprite("map-background", Layer_Background)
        self.MapCareerDialog["Static"]["Jane"] = MakeSprite("map.jane", Layer_Background-1, { "x": 300, "y": 140 } )
        self.MapCareerDialog["Static"]["JaneEyes"] = MakeSprite("map.jane.eyes", Layer_Background-2, { "x": 400, "y": 270 } )
        self.MapCareerDialog["Animations"]["JaneEyes"] = CustomersAnimator(self.MapCareerDialog["Static"]["JaneEyes"],
                                                globalvars.CustomerAnimations.GetSubtag("animation.map.janeeyes"))
        self.MapCareerDialog["Animations"]["JaneEyes"].SetState("None")
        self.MapCareerDialog["Animations"]["JaneEyes"].Freeze(True)
        self.MapCareerDialog["Static"]["Tablet"] = MakeSprite("map.tablet", Layer_Background-1, { "x": 30, "y": 385 } )
        self.MapCareerDialog["Text"]["BestResult"] = MakeSprite("domcasual-10-up", Layer_BtnText,
                                                { "x": 170, "y": 500, "hotspot": scraft.HotspotCenter } )
        self.MapCareerDialog["Buttons"]["Start"] = PushButton("MapStart",
                self, Cmd_MapStart, PState_MapCareer,
                u"map.play.button", [0, 1, 2, 3], 
                Layer_BtnText, 170, 540, 130, 50,
                Str_MapStart, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.MapCareerDialog["Buttons"]["ViewResults"] = PushButton("ViewResults",
                self, Cmd_MapViewResults, PState_MapCareer,
                u"map.play.button", [0, 1, 2, 3], 
                Layer_BtnText, 170, 540, 130, 50,
                Str_MapViewResults, [u"domcasual-10-up", u"domcasual-10-roll", u"domcasual-10-down", u"domcasual-10-inert"])
        self.MapCareerDialog["Buttons"]["MainMenu"] = PushButton("MapMainMenu",
                self, Cmd_MapMainMenu, PState_MapCareer,
                u"map.back-button", [0, 1, 2, 3], 
                Layer_BtnText, 30, 25, 50, 50)
        for tmp in globalvars.LevelProgress.GetTag("Episodes").Tags("episode"):
            self.MapCareerDialog["Static"][tmp.GetContent()] = MakeSprite(tmp.GetStrAttr("image"), Layer_Static,
                { "x": tmp.GetIntAttr("x"), "y": tmp.GetIntAttr("y"), "hotspot": scraft.HotspotCenter })
        for tmp in globalvars.LevelProgress.GetTag("Levels").Tags("level"):
            self.MapCareerDialog["Buttons"][tmp.GetContent()] = PushButton("",
                self, Cmd_MapLevel + tmp.GetIntAttr(u"no"), PState_MapCareer,
                u"level-pointers", [0, 1, 2, 3, 4], Layer_BtnText,
                tmp.GetIntAttr(u"x"), tmp.GetIntAttr(u"y"), 30, 30)
        for tmp in globalvars.LevelProgress.GetTag("Levels").Tags("outro"):
            self.MapCareerDialog["Buttons"][tmp.GetContent()] = PushButton("",
                self,
                Cmd_MapOutro + eval(globalvars.GameSettings.GetStrAttr("settings")).index(tmp.GetStrAttr("episode")),
                PState_MapCareer,
                u"outro-pointers", [0, 1, 2, 3, 4], Layer_BtnText,
                tmp.GetIntAttr(u"x"), tmp.GetIntAttr(u"y"), 30, 30)
        
        globalvars.BlackBoard.Update(BBTag_Cursor, {"state": GameCursorState_Default})
        globalvars.BlackBoard.Update(BBTag_Cursor, {"button": ButtonState_Up})
        globalvars.BlackBoard.Update(BBTag_Cursor, {"red": False})
        self._SetState(PState_DevLogo)    
        self.QueNo = oE.executor.Schedule(self)
        
        
    def _ShowDialog(self, dialog, flag):
        for spr in dialog["Static"].values() + dialog["Text"].values():
            spr.visible = flag
        for btn in dialog["Buttons"].values():
            btn.Show(flag)
        if not flag and dialog.has_key("Animations"):
            for tmp in dialog["Animations"].keys():
                dialog["Animations"][tmp].SetState("None")
                dialog["Animations"][tmp].Freeze(True)
        
    def CallInternalMenu(self):
        self._SetState(PState_Options)
        
    def CallLevelCompleteDialog(self, flag, params = {}):
        self._SetState(PState_NextLevel)
        #фон
        if not flag:
            self.LevelCompleteDialog["Static"]["Back"].ChangeKlassTo("level-results.bg.bad")
        elif not params["expert"]:
            self.LevelCompleteDialog["Static"]["Back"].ChangeKlassTo("level-results.bg.good")
        else:
            self.LevelCompleteDialog["Static"]["Back"].ChangeKlassTo("level-results.bg.expert")
            
        self.LevelCompleteDialog["Text"]["TextServed"].text = str(params["served"])
        self.LevelCompleteDialog["Text"]["TextLost"].text = str(params["lost"])
        self.LevelCompleteDialog["Text"]["TextEarned"].text = str(params["score"])
        tmpBest = globalvars.BestResults.GetSubtag(globalvars.CurrentPlayer.GetLevel().GetContent())
        self.LevelCompleteDialog["Text"]["Text3"].text = Str_LvComplete_BestScore + str(tmpBest.GetIntAttr("hiscore"))
        self.LevelCompleteDialog["Text"]["Text4"].text = Str_LvComplete_AchievedBy + str(tmpBest.GetStrAttr("player"))
        self.LevelCompleteDialog["Text"]["Text5"].text = (params["expert"])*Str_LvComplete_Expert + \
            (params["score"]==tmpBest.GetIntAttr("hiscore"))*Str_LvComplete_Hiscore
        if flag:
            self.LevelCompleteDialog["Buttons"]["Continue"].Show(True)
            self.LevelCompleteDialog["Buttons"]["Restart"].Show(False)
            self.LevelCompleteDialog["Buttons"]["No"].Show(False)
        else:
            self.LevelCompleteDialog["Buttons"]["Continue"].Show(False)
            self.LevelCompleteDialog["Buttons"]["Restart"].Show(True)
            self.LevelCompleteDialog["Buttons"]["No"].Show(True)
        
    def CallGameOverDialog(self, flag):
        self._SetState(PState_GameOver)
        
    def _Ask(self, question, answerYes = "Yes", answerNo = "No"):
        self._SetState(PState_YesNo)
        self.YesNoDialog["Text"]["QuestionText"].text = question
        self.YesNoDialog["Buttons"]["Yes"].SetText(answerYes)
        self.YesNoDialog["Buttons"]["No"].SetText(answerNo)
        
    def _AskYnc(self, question, answerYes = "Yes", answerNo = "No", answerCancel = "Cancel"):
        self._SetState(PState_YesNoCancel)
        self.YesNoCancelDialog["Text"]["QuestionText"].text = question
        self.YesNoCancelDialog["Buttons"]["Yes"].SetText(answerYes)
        self.YesNoCancelDialog["Buttons"]["No"].SetText(answerNo)
        self.YesNoCancelDialog["Buttons"]["Cancel"].SetText(answerCancel)
        
    #----------------------------
    #отображает заданную страницу кулинарной книги
    #----------------------------
    def _ShowCookBookPage(self, no):
        #коррекция в случае переключения на другой профиль игрока:
        #не показывать не разлоченные страницы книги
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
        while not globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no]).GetBoolAttr("unlocked") and no>0:
            no -= 1
        tmpSetting = tmpAllSettings[no]
        self.CurrentCookbookPage = no
        
        #нарисовать страницу сеттинга
        self.CookbookDialog["Static"]["Back"].ChangeKlassTo(globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("background"))
        self.CookbookDialog["Static"]["Logo"].ChangeKlassTo(globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("logo"))
        
        #проверить рецепты: известные или нет, новые или старые
        tmpRecipes = filter(lambda x: globalvars.RecipeInfo.GetSubtag(x).GetStrAttr("setting") == tmpSetting,
                                map(lambda x: x.GetContent(), globalvars.RecipeInfo.Tags()))
        tmpNewRecipes = globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting)
        for i in range(self.TotalRecipesOnPage):
            self.CookbookDialog["Static"]["Recipe"+str(i+1)].x = globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeX")
            self.CookbookDialog["Static"]["Recipe"+str(i+1)].y = globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetIntAttr("badgeY")
            if globalvars.CurrentPlayer.GetLevelParams(tmpRecipes[i]).GetBoolAttr("unlocked"):
                self.CookbookDialog["Static"]["Recipe"+str(i+1)].ChangeKlassTo(globalvars.RecipeInfo.GetSubtag(tmpRecipes[i]).GetStrAttr("badge"))
                if tmpRecipes[i] in tmpNewRecipes:
                    self.CookbookDialog["Static"]["Recipe"+str(i+1)].transparency = 20
                    globalvars.CurrentPlayer.SetLevelParams(tmpRecipes[i], { "seen": True })
                    j = tmpNewRecipes.index(tmpRecipes[i])
                    self.CookbookDialog["Static"]["NewRecipe"+str(j+1)].x = self.CookbookDialog["Static"]["Recipe"+str(i+1)].x
                    self.CookbookDialog["Static"]["NewRecipe"+str(j+1)].y = self.CookbookDialog["Static"]["Recipe"+str(i+1)].y
                    self.CookbookDialog["Animations"]["NewRecipe"+str(j+1)].SetState("First")
                    self.CookbookDialog["Animations"]["NewRecipe"+str(j+1)].Freeze(False)
                else:
                    self.CookbookDialog["Static"]["Recipe"+str(i+1)].transparency = 0
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

    #----------------------------
    #переходит к заданной странице справки
    #----------------------------
    def _ShowHelpPage(self, no):
        if no == 0:
            self.RulesDialog["Buttons"]["HelpPrev"].SetState(ButtonState_Inert)
        else:
            self.RulesDialog["Buttons"]["HelpPrev"].SetState(ButtonState_Up)
        if no == self.TotalHelpPages-1:
            self.RulesDialog["Buttons"]["HelpNext"].SetState(ButtonState_Inert)
        else:
            self.RulesDialog["Buttons"]["HelpNext"].SetState(ButtonState_Up)
        self.RulesDialog["Static"]["Back"].ChangeKlassTo(u"help-page"+str(no+1))
        self.CurrentHelpPage = no
        
    def _DrawPlayersList(self):
        if globalvars.GameConfig.GetStrAttr("Player") != "":
            tmpName = globalvars.GameConfig.GetStrAttr("Player")
            tmpList = globalvars.PlayerList.GetPlayerList()
            if self.SelectedPlayer == "":
                self.SelectedPlayer = tmpName
            if tmpList.count(self.SelectedPlayer) > 0:
                tmpInd = tmpList.index(self.SelectedPlayer)
                if tmpInd < self.TotalPlayersOnScreen:
                    self.FirstPlayer = 0
                else:
                    self.FirstPlayer = tmpInd - self.TotalPlayersOnScreen+1
        self._UpdatePlayersList()
                
    def _UpdatePlayersList(self):
        tmpList = globalvars.PlayerList.GetPlayerList()
        tmpCount = min(self.TotalPlayersOnScreen, len(tmpList))
        for i in range(tmpCount):
            if tmpList[self.FirstPlayer + i] == self.SelectedPlayer:
                self.PlayersDialog["Buttons"]["Player_"+str(i)].SetState(ButtonState_Selected)
            else:
                self.PlayersDialog["Buttons"]["Player_"+str(i)].SetState(ButtonState_Up)
            self.PlayersDialog["Buttons"]["Player_"+str(i)].Show(True)
            self.PlayersDialog["Buttons"]["Player_"+str(i)].SetText(tmpList[self.FirstPlayer+i])
        if tmpCount < self.TotalPlayersOnScreen:
            for i in range(tmpCount, self.TotalPlayersOnScreen):
                self.PlayersDialog["Buttons"]["Player_"+str(i)].Show(False)
        if self.FirstPlayer > 0:
            self.PlayersDialog["Buttons"]["Up"].SetState(ButtonState_Up)
        else:
            self.PlayersDialog["Buttons"]["Up"].SetState(ButtonState_Inert)
        if self.FirstPlayer + self.TotalPlayersOnScreen < len(tmpList):
            self.PlayersDialog["Buttons"]["Down"].SetState(ButtonState_Up)
        else:
            self.PlayersDialog["Buttons"]["Down"].SetState(ButtonState_Inert)
        if self.SelectedPlayer != "":
            self.PlayersDialog["Buttons"]["Remove"].SetState(ButtonState_Up)
            self.PlayersDialog["Buttons"]["Ok"].SetState(ButtonState_Up)
            self.PlayersDialog["Buttons"]["Cancel"].SetState(ButtonState_Up)
        else:
            self.PlayersDialog["Buttons"]["Remove"].SetState(ButtonState_Inert)
            self.PlayersDialog["Buttons"]["Ok"].SetState(ButtonState_Inert)
            self.PlayersDialog["Buttons"]["Cancel"].SetState(ButtonState_Inert)
        
    #----------------------------
    #обновляет кнопки cancel и ok в диалоге ввода имени:
    #если ничего не введено и список игроков пуст, кнопка cancel должна быть инертной
    #евсли ничего не введено, кнопка ok должна быть инертной
    #----------------------------
    def _UpdateEnterNameDialog(self):
        if len(globalvars.PlayerList.GetPlayerList())<=1 and self.EnterNameDialog["Text"]["Name"].text == "":
            self.EnterNameDialog["Buttons"]["Cancel"].SetState(ButtonState_Inert)
        else:
            self.EnterNameDialog["Buttons"]["Cancel"].SetState(ButtonState_Up)
        if self.EnterNameDialog["Text"]["Name"].text == "":
            self.EnterNameDialog["Buttons"]["Ok"].SetState(ButtonState_Inert)
        else:
            self.EnterNameDialog["Buttons"]["Ok"].SetState(ButtonState_Up)
        
    def _UpdateHiscoresDialog(self):
        tmpTotalScores = len(globalvars.HiscoresList)
        for i in range(tmpTotalScores):
            tmpScore = globalvars.HiscoresList[i]
            self.HiscoresDialog["Text"]["Name_"+str(i)].text = tmpScore["Name"]
            self.HiscoresDialog["Text"]["Score_"+str(i)].text = str(tmpScore["Score"])
            if tmpScore["Active"]:
                self.HiscoresDialog["Text"]["Name_"+str(i)].cfilt.color = CFilt_CurScore
                self.HiscoresDialog["Text"]["Score_"+str(i)].cfilt.color = CFilt_CurScore
                tmpScore["Active"] = False
            else:
                self.HiscoresDialog["Text"]["Name_"+str(i)].cfilt.color = CFilt_None
                self.HiscoresDialog["Text"]["Score_"+str(i)].cfilt.color = CFilt_None
        if tmpTotalScores < Max_Scores:
            for i in range(tmpTotalScores, Max_Scores):
                self.HiscoresDialog["Text"]["Name_"+str(i)].text = u""
                self.HiscoresDialog["Text"]["Score_"+str(i)].text = u""
        if tmpTotalScores == 0:
            self.HiscoresDialog["Buttons"]["Reset"].SetState(ButtonState_Inert)
        else:
            self.HiscoresDialog["Buttons"]["Reset"].SetState(ButtonState_Up)
        
    #----------------------------
    # перерисовывает окно карты
    # подсвечивает открытые и закрытые уровни
    #----------------------------
    def _UpdateMapWindow(self):
        #список кнопок на карте, обозначающих уровни, он же список файлов уровней - так проще получить этот список
        tmpOutroKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
        for level in tmpOutroKeys:
            #читаем запись из профиля игрока
            tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(level)
            if tmpPlayerResult.GetBoolAttr(u"expert"):
                self.MapCareerDialog["Buttons"][level].SetButtonKlass(u"outro-pointers-expert")
            else:
                self.MapCareerDialog["Buttons"][level].SetButtonKlass(u"outro-pointers")
            if tmpPlayerResult.GetBoolAttr(u"unlocked"):
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Up)
            else:
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Inert)
        
        tmpLevelKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("level"))
        for level in tmpLevelKeys:
            #читаем запись из профиля игрока
            tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(level)
            if tmpPlayerResult.GetBoolAttr(u"expert"):
                self.MapCareerDialog["Buttons"][level].SetButtonKlass(u"level-pointers-expert")
            else:
                self.MapCareerDialog["Buttons"][level].SetButtonKlass(u"level-pointers")
            if tmpPlayerResult.GetBoolAttr(u"unlocked"):
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Up)
            else:
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Inert)
        
        #если выбран уровень 
        if self.SelectedLevel in tmpLevelKeys:
            self.MapCareerDialog["Buttons"]["ViewResults"].Show(False)
            self.MapCareerDialog["Buttons"]["Start"].Show(True)
            self.MapCareerDialog["Buttons"]["Start"].SetState(ButtonState_Up)
            self.MapCareerDialog["Buttons"][self.SelectedLevel].SetState(ButtonState_Selected)
            tmpBest = globalvars.BestResults.GetSubtag(self.SelectedLevel)
            if tmpBest.GetIntAttr("hiscore") != 0 and tmpBest.GetStrAttr("player") != "":
                self.MapCareerDialog["Text"]["BestResult"].text = Str_MapHiscore + str(tmpBest.GetIntAttr("hiscore")) + \
                    Str_MapAchievedBy + tmpBest.GetStrAttr("player")
            else:
                self.MapCareerDialog["Text"]["BestResult"].text = Str_MapHiscore + str(tmpBest.GetIntAttr("hiscore"))
        #исправить
        elif self.SelectedLevel in tmpOutroKeys:
            self.MapCareerDialog["Buttons"]["ViewResults"].Show(True)
            self.MapCareerDialog["Buttons"]["Start"].Show(False)
            self.MapCareerDialog["Buttons"][self.SelectedLevel].SetState(ButtonState_Selected)
            self.MapCareerDialog["Text"]["BestResult"].text = self.SelectedLevel
        else:
            self.MapCareerDialog["Buttons"]["ViewResults"].Show(False)
            self.MapCareerDialog["Buttons"]["Start"].Show(True)
            self.MapCareerDialog["Buttons"]["Start"].SetState(ButtonState_Inert)
            self.MapCareerDialog["Text"]["BestResult"].text = ""
        #отрисовать картинки эпизодов - разлочены они или нет
        for tmp in globalvars.LevelProgress.GetTag("Episodes").Tags("episode"):
            if globalvars.CurrentPlayer.GetLevelParams(tmp.GetContent()).GetBoolAttr("unlocked"):
                self.MapCareerDialog["Static"][tmp.GetContent()].frno = 0
            else:
                self.MapCareerDialog["Static"][tmp.GetContent()].frno = 1
        self.MapCareerDialog["Animations"]["JaneEyes"].SetState("Smile")
        self.MapCareerDialog["Animations"]["JaneEyes"].Freeze(False)
        
    #-------------------------------------------
    # показать текущий кадр комикса
    #-------------------------------------------
    def _UpdateComics(self):
        tmp = globalvars.CurrentPlayer.GetLevel()
        self.ComicScreen["Buttons"]["Back"].SetButtonKlass(tmp.GetStrAttr("image"))
        self.ComicScreen["Buttons"]["Next"].SetButtonKlass(tmp.GetStrAttr("button"))
        
    #-------------------------------------------
    # показать вводный экран очередного эпизода
    #-------------------------------------------
    def _ShowEpisodeIntro(self):
        tmpEpisode = globalvars.CurrentPlayer.GetLevel().GetStrAttr("episode")
        tmp = globalvars.ThemesInfo.GetSubtag(tmpEpisode)
        tmpCharacters = eval(globalvars.LevelProgress.GetTag("People").GetSubtag(tmpEpisode).GetStrAttr("people")).keys()
        #shuffle(tmpCharacters)
        self.IntroScreen["Buttons"]["Back"].SetButtonKlass(tmp.GetStrAttr("background"))
        self.IntroScreen["Static"]["IntroPane"].ChangeKlassTo(tmp.GetStrAttr("introPane"))
        self.IntroScreen["Text"]["Title"].text = globalvars.CurrentPlayer.GetLevel().GetStrAttr("title")
        for i in range(self.MaxPeopleOnLevel):
            if i < len(tmpCharacters):
                self.IntroScreen["Static"]["Character"+str(i)].\
                    ChangeKlassTo(globalvars.CompetitorsInfo.GetSubtag(tmpCharacters[i]).GetStrAttr("src"))
                self.IntroScreen["Static"]["Character"+str(i)].hotspot = scraft.HotspotCenterBottom
                self.IntroScreen["Text"]["Character"+str(i)].text = str(i+1)+". "+tmpCharacters[i]
            else:
                self.IntroScreen["Static"]["Character"+str(i)].ChangeKlassTo("$spritecraft$dummy$")
                self.IntroScreen["Text"]["Character"+str(i)].text = ""
        
    #-------------------------------------------
    # показать итоговый экран очередного эпизода
    #-------------------------------------------
    def _ShowEpisodeOutro(self):
        tmpLevel = globalvars.CurrentPlayer.GetLevel()
        tmpEpisode = tmpLevel.GetStrAttr("episode")
        tmp = globalvars.ThemesInfo.GetSubtag(tmpEpisode)
        tmpResults = globalvars.CurrentPlayer.GetScoresPlaceAndCondition()
        
        self.OutroScreen["Buttons"]["Back"].SetButtonKlass(tmp.GetStrAttr("background"))
        self.OutroScreen["Static"]["IntroPane"].ChangeKlassTo(tmp.GetStrAttr("introPane"))
        self.OutroScreen["Text"]["Title"].text = globalvars.CurrentPlayer.GetLevel().GetStrAttr("title")
        tmpStr = Str_OutroSpeech+"\n"
        for i in range(tmpLevel.GetIntAttr("PassFurther")):
            tmpStr += (tmpResults["scores"][i][0]+"\n")
        if not tmpResults["pass"]:
            tmpStr += Str_OutroNotPass
        self.OutroScreen["Text"]["Speech"].text = tmpStr
        for i in range(self.MaxPeopleOnOutro):
            if i < tmpLevel.GetIntAttr("PassFurther"):
                self.OutroScreen["Static"]["Character"+str(i)].\
                        ChangeKlassTo(globalvars.CompetitorsInfo.GetSubtag(tmpResults["scores"][i][0]).GetStrAttr("src"))
                self.OutroScreen["Static"]["Character"+str(i)].x, self.OutroScreen["Static"]["Character"+str(i)].y = \
                    Crd_CharOutroPositions[tmpLevel.GetIntAttr("PassFurther")][i]
                self.OutroScreen["Static"]["Character"+str(i)].hotspot = scraft.HotspotCenterBottom
                self.OutroScreen["Static"]["Light"+str(i)].ChangeKlassTo("outro.light")
                self.OutroScreen["Static"]["Light"+str(i)].hotspot = scraft.HotspotCenterBottom
                self.OutroScreen["Static"]["Medallion"+str(i)].ChangeKlassTo(tmp.GetStrAttr("winnerSign"))
                self.OutroScreen["Static"]["Medallion"+str(i)].hotspot = scraft.HotspotCenter
                self.OutroScreen["Text"]["Number"+str(i)].text = str(i+1)
                self.OutroScreen["Text"]["Name"+str(i)].text = tmpResults["scores"][i][0]
            else:
                self.OutroScreen["Static"]["Character"+str(i)].ChangeKlassTo("$spritecraft$dummy$")
                self.OutroScreen["Static"]["Light"+str(i)].ChangeKlassTo("$spritecraft$dummy$")
                self.OutroScreen["Static"]["Medallion"+str(i)].ChangeKlassTo("$spritecraft$dummy$")
                self.OutroScreen["Text"]["Number"+str(i)].text = ""
                self.OutroScreen["Text"]["Name"+str(i)].text = ""
        for i in range(self.MaxPeopleOnLevel):
            if i < len(tmpResults["scores"]):
                self.OutroScreen["Text"]["Character"+str(i)].text = tmpResults["scores"][i][0]
                self.OutroScreen["Text"]["Score"+str(i)].text = str(tmpResults["scores"][i][1])
            else:
                self.OutroScreen["Text"]["Character"+str(i)].text = ""
                self.OutroScreen["Text"]["Score"+str(i)].text = ""
                
        
    #-------------------------------------------
    # обновить данные в диалоге "цели уровня", при старте уровня
    #-------------------------------------------
    def _UpdateLevelGoals(self):
        self.LevelGoalsDialog["Text"]["Title"].text = globalvars.LevelSettings.GetTag(u"LevelSettings").GetStrAttr("title")
        self.LevelGoalsDialog["Text"]["Text1"].text = "Level goal: "+str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("moneyGoal"))
        self.LevelGoalsDialog["Text"]["Text2"].text = "Expert goal: "+str(globalvars.LevelSettings.GetTag(u"LevelSettings").GetIntAttr("expertGoal"))
        
    #-------------------------------------------
    # показать диалог с опциями - обновить данные по текущим опциям
    #-------------------------------------------
    def _UpdateOptionsDialog(self):
        self.OptionsDialog["Static"]["Galka_Fullscreen"].visible = globalvars.GameConfig.GetBoolAttr("Fullscreen")
        self.OptionsDialog["Static"]["Galka_Mute"].visible = globalvars.GameConfig.GetBoolAttr("Mute")
        self.OptionsDialog["Static"]["Galka_Hints"].visible = globalvars.GameConfig.GetBoolAttr("Hints")
        self.OptionsDialog["Buttons"]["Slider_Sound"].SetValue(globalvars.GameConfig.GetIntAttr("Sound"))
        self.OptionsDialog["Buttons"]["Slider_Music"].SetValue(globalvars.GameConfig.GetIntAttr("Music"))
        if globalvars.StateStack[-2] == PState_Game:
            self.OptionsDialog["Buttons"]["Resume"].Show(True)
            self.OptionsDialog["Buttons"]["Restart"].Show(True)
            self.OptionsDialog["Buttons"]["EndGame"].Show(True)
            self.OptionsDialog["Buttons"]["Ok"].Show(False)
        else:
            self.OptionsDialog["Buttons"]["Resume"].Show(False)
            self.OptionsDialog["Buttons"]["Restart"].Show(False)
            self.OptionsDialog["Buttons"]["EndGame"].Show(False)
            self.OptionsDialog["Buttons"]["Ok"].Show(True)
        
    #-------------------------------------------
    # закрыть диалог с опциями или внутри-игровое меню - применить измененные опции
    #-------------------------------------------
    def _CloseOptionsDialog(self, flag):
        if flag:
            globalvars.GameConfig.SetBoolAttr("Fullscreen", self.OptionsDialog["Static"]["Galka_Fullscreen"].visible)
            globalvars.GameConfig.SetBoolAttr("Mute", self.OptionsDialog["Static"]["Galka_Mute"].visible)
            globalvars.GameConfig.SetBoolAttr("Hints", self.OptionsDialog["Static"]["Galka_Hints"].visible)
        else:
            globalvars.GameConfig.SetIntAttr("Sound", self.SavedOptions.GetIntAttr("Sound"))
            globalvars.GameConfig.SetIntAttr("Music", self.SavedOptions.GetIntAttr("Music"))
        config.ApplyOptions()
        self._ReleaseState(PState_Options)
        
    #-------------------------------------------
    # переход к следующему комиксу или уровню
    # функция вызывается при вызове карты и при закрытии комикса
    #-------------------------------------------
    def NextCareerStage(self):
        try:
            self._ReleaseState(PState_Comics)
            self._ReleaseState(PState_Intro)
            self._ReleaseState(PState_Outro)
            #проходим по списку уровней и находим последний разлоченный
            tmpAllUnlocked = filter(lambda x: globalvars.CurrentPlayer.GetLevelParams(x.GetContent()).GetBoolAttr(u"unlocked"),
                                        globalvars.LevelProgress.GetTag("Levels").Tags())
            tmpLastUnlocked = tmpAllUnlocked[-1]
            tmpNoUnlockedLevels = len(filter(lambda x: x.GetName() == u"level", tmpAllUnlocked))
            
            #если последний разлоченный - комикс, то показать комикс
            if tmpLastUnlocked.GetName() == u"comic":
                #если это последний комикс, и его уже видели - показать опять карту
                if not tmpLastUnlocked.Next() and \
                        globalvars.CurrentPlayer.GetLevelParams(tmpLastUnlocked.GetContent()).GetBoolAttr("seen"):
                    self._SetState(PState_MapCareer)
                else:
                    globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
                    self._SetState(PState_Comics)
            #вводная страница эпизода
            elif tmpLastUnlocked.GetName() == "intro":
                globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
                self._SetState(PState_Intro)
            #иначе: смотрим количество разлоченных уровней
            #если больше 1, то показываем карту
            elif tmpNoUnlockedLevels > 1:
                self._SetState(PState_MapCareer)
            #иначе запускаем первый уровень
            else:
                globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
                self._SetState(PState_StartLevel)
        except:
            oE.Log("Next stage fatal error")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
        
    #-------------------------------------------
    # обработка команд от кнопок
    #-------------------------------------------
    def SendCommand(self, cmd):
        try:
            #developer logo
            if globalvars.StateStack[-1] == PState_DevLogo:
                if cmd == Cmd_DevLogoClose:
                    self._SetState(PState_PubLogo)
                
            #publisher logo
            elif globalvars.StateStack[-1] == PState_PubLogo:
                if cmd == Cmd_PubLogoClose:
                    self._SetState(PState_MainMenu)
                
            #main menu
            elif globalvars.StateStack[-1] == PState_MainMenu:
                if cmd == Cmd_Menu_PlayCareer:
                    self.NextCareerStage()
                elif cmd == Cmd_Menu_Players:
                    self._SetState(PState_Players)
                elif cmd == Cmd_Menu_Options:
                    self._SetState(PState_Options)
                elif cmd == Cmd_Menu_Rules:
                    self._SetState(PState_Help)
                elif cmd == Cmd_Menu_Cookbook:
                    self._SetState(PState_Cookbook)
                    #self._ShowCookBookPage(self.CurrentCookbookPage)
                elif cmd == Cmd_Menu_Hiscores:
                    self._SetState(PState_Hiscores)
                elif cmd == Cmd_Menu_Quit:
                    self._SetState(PState_EndGame)
                    
            #comics
            elif globalvars.StateStack[-1] == PState_Comics:
                if cmd == Cmd_ComicsNext:
                    self.NextCareerStage()
                
            #intro
            elif globalvars.StateStack[-1] == PState_Intro:
                if cmd == Cmd_IntroNext:
                    self.NextCareerStage()
                
            #outro
            elif globalvars.StateStack[-1] == PState_Outro:
                if cmd == Cmd_OutroNext:
                    self.NextCareerStage()
                
            #map window
            elif globalvars.StateStack[-1] == PState_MapCareer:
                if cmd == Cmd_MapStart:
                    #self.NextCareerStage()
                    self._ReleaseState(PState_MapCareer)
                    globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").GetSubtag(self.SelectedLevel))
                    self._SetState(PState_StartLevel)
                elif cmd == Cmd_MapViewResults:
                    self._ReleaseState(PState_MapCareer)
                    self._SetState(PState_Outro)
                elif cmd == Cmd_MapMainMenu:
                    self._ReleaseState(PState_MapCareer)
                else:
                    if cmd >= Cmd_MapOutro:
                        self.SelectedLevel = defs.GetTagWithAttribute(globalvars.LevelProgress.GetTag("Levels"),
                                u"outro", u"episode",
                                eval(globalvars.GameSettings.GetStrAttr("settings"))[cmd-Cmd_MapOutro]).GetContent()
                    else:
                        self.SelectedLevel = defs.GetTagWithAttribute(globalvars.LevelProgress.GetTag("Levels"),
                                            u"level", u"no", str(cmd-Cmd_MapLevel)).GetContent()
                    self._UpdateMapWindow()
                
            #cookbook
            elif globalvars.StateStack[-1] == PState_Cookbook:
                if cmd == Cmd_CookbookPrev:
                    self._ShowCookBookPage(self.CurrentCookbookPage-1)
                elif cmd == Cmd_CookbookNext:
                    self._ShowCookBookPage(self.CurrentCookbookPage+1)
                elif cmd == Cmd_CookbookClose:
                    self._ReleaseState(PState_Cookbook)
                    if self.NextState != PState_None:
                        self.NextState = PState_None
                        self.NextCareerStage()
            
            #rules dialog
            elif globalvars.StateStack[-1] == PState_Help:
                if cmd == Cmd_HelpPrev:
                    self._ShowHelpPage(self.CurrentHelpPage-1)
                elif cmd == Cmd_HelpNext:
                    self._ShowHelpPage(self.CurrentHelpPage+1)
                elif cmd == Cmd_HelpClose:
                    self._ReleaseState(PState_Help)    
                
            #players dialog
            elif globalvars.StateStack[-1] == PState_Players:
                if cmd == Cmd_PlayersRemove:
                    self._Ask(Str_Question_RemovePlayer)
                elif cmd == Cmd_PlayersOk:
                    if self.SelectedPlayer != "":
                        globalvars.PlayerList.SelectPlayer(self.SelectedPlayer)
                    self._ReleaseState(PState_Players)
                elif cmd == Cmd_PlayersCancel:
                    self.SelectedPlayer = ""
                    self._ReleaseState(PState_Players)
                elif cmd == Cmd_PlayersUp:
                    self.FirstPlayer -= 1
                    self._UpdatePlayersList()
                elif cmd == Cmd_PlayersDown:
                    self.FirstPlayer += 1
                    self._UpdatePlayersList()
                elif cmd == Cmd_PlayersNew:
                    self._SetState(PState_EnterName)
                elif cmd in range(Cmd_PlayersSelect, \
                        Cmd_PlayersSelect+self.TotalPlayersOnScreen):
                    #if cmd == Cmd_PlayersSelect and self.FirstPlayer == 0:
                    #    self._SetState(PState_EnterName)
                    #else:
                    self.SelectedPlayer = globalvars.PlayerList.GetPlayerList()[self.FirstPlayer + cmd - Cmd_PlayersSelect]
                    self._UpdatePlayersList()
            
            #options dialog
            elif globalvars.StateStack[-1] == PState_Options:
                if cmd == Cmd_OptionsOk:
                    self._CloseOptionsDialog(True)
                elif cmd == Cmd_OptionsCancel:
                    self._CloseOptionsDialog(False)
                elif cmd == Cmd_OptionsMute:
                    self.OptionsDialog["Static"]["Galka_Mute"].visible = not(self.OptionsDialog["Static"]["Galka_Mute"].visible)
                elif cmd == Cmd_OptionsHints:
                    self.OptionsDialog["Static"]["Galka_Hints"].visible = not(self.OptionsDialog["Static"]["Galka_Hints"].visible)
                elif cmd == Cmd_OptionsFullscreen:
                    self.OptionsDialog["Static"]["Galka_Fullscreen"].visible = not(self.OptionsDialog["Static"]["Galka_Fullscreen"].visible)
                elif cmd == Cmd_IGM_Resume:
                    self._CloseOptionsDialog(True)
                elif cmd == Cmd_IGM_Restart:
                    self._Ask(Str_Question_RestartLevel)
                elif cmd == Cmd_IGM_EndGame:
                    self._ReleaseState(PState_Options)
                    self._ReleaseState(PState_Game)
                    self._SetState(PState_MainMenu)    
                
            #hiscores dialog
            elif globalvars.StateStack[-1] == PState_Hiscores:
                if cmd == Cmd_HiscoresReset:
                    self._Ask(Str_Question_ClearHiscores)
                elif cmd == Cmd_HiscoresClose:
                    self._ReleaseState(PState_Hiscores)
            
            #entername dialog
            elif globalvars.StateStack[-1] == PState_EnterName:
                if cmd == Cmd_EnterNameOk:
                    tmpName = self.EnterNameDialog["Text"]["Name"].text
                    if len(tmpName) == 0:
                        self.EnterNameDialog["Text"]["NameErrors"].text = Str_EnterName_Error_Empty
                        return
                    elif tmpName == 'None':
                        self.EnterNameDialog["Text"]["NameErrors"].text = Str_EnterName_Error_Bad
                        return
                    elif globalvars.PlayerList.GetPlayerList().count(tmpName) > 0:
                        self.EnterNameDialog["Text"]["NameErrors"].text = Str_EnterName_Error_Exist
                        return
                    else:
                        globalvars.PlayerList.CreatePlayer(tmpName)
                        self.SelectedPlayer = tmpName
                        self._DrawPlayersList()
                elif cmd == Cmd_EnterNameCancel:
                    pass
                self.EnterNameDialog["Text"]["Name"].text = u""
                self.EnterNameDialog["Static"]["TextCursor"].x = self.EnterNameDialog["Text"]["Name"].x
                self._ReleaseState(PState_EnterName)
            
            #yes-no dialog
            elif globalvars.StateStack[-1] == PState_YesNo:
                self._ReleaseState(PState_YesNo)
                if cmd == Cmd_Yes:
                    #remove player
                    if globalvars.StateStack[-1] == PState_Players:
                        globalvars.PlayerList.DelPlayer(self.SelectedPlayer)
                        self.SelectedPlayer = ""
                        self._DrawPlayersList()
                    #clear hiscores
                    elif globalvars.StateStack[-1] == PState_Hiscores:
                        config.ClearHiscores()
                    #restart game
                    elif globalvars.StateStack[-1] == PState_Options:
                        self._ReleaseState(PState_Options)
                        #globalvars.Board.Clear()
                        self._ReleaseState(PState_Game)
                        #globalvars.Board.Clear()
                        self._SetState(PState_StartLevel)
                        #globalvars.Board.Restart()
                    
            elif globalvars.StateStack[-1] == PState_YesNoCancel:
                self._ReleaseState(PState_YesNoCancel)
                if cmd == Cmd_YncYes:
                    #continue game
                    if globalvars.StateStack[-1] == PState_MainMenu:
                        self._SetState(PState_StartLevel)
                elif cmd == Cmd_YncNo:
                    #start new game
                    if globalvars.StateStack[-1] == PState_MainMenu:
                        globalvars.CurrentPlayer["Game"] = False
                        globalvars.CurrentPlayer["Playing"] = False
                        self._SetState(PState_MapCareer)
                elif cmd == Cmd_YncCancel:
                    pass
                    
            #level goals dialog
            elif globalvars.StateStack[-1] == PState_StartLevel:
                self._ReleaseState(PState_StartLevel)
                if cmd == Cmd_LvGoalsPlay:
                    globalvars.Board.Freeze(False)
            
            #level complete dialog
            elif globalvars.StateStack[-1] == PState_NextLevel:
                self._ReleaseState(PState_NextLevel)
                self._ReleaseState(PState_Game)
                if cmd == Cmd_LvCompleteNextLevel:
                    tmpSetting = globalvars.LevelSettings.GetTag("Layout").GetStrAttr(u"theme")
                    if globalvars.CurrentPlayer.JustUnlockedRecipes(tmpSetting) != []:
                        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
                        self.CurrentCookbookPage = tmpAllSettings.index(tmpSetting)
                        self.NextState = PState_Game
                        self._SetState(PState_Cookbook)
                    else:
                        self.NextCareerStage()
                elif cmd == Cmd_LvCompleteRestart:
                    self._SetState(PState_StartLevel)
                elif cmd == Cmd_LvCompleteMainMenu:
                    pass
                
            #end game dialog
            elif globalvars.StateStack[-1] == PState_GameOver:
                self._ReleaseState(PState_GameOver)
                self._ReleaseState(PState_Game)
                if cmd == Cmd_GameOverHiscores:
                    self._SetState(PState_Hiscores)
                elif cmd == Cmd_GameOverMainMenu:
                    self._SetState(PState_MainMenu)
                #self._ReleaseState(PState_Game)
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
        
    def _OnExecute(self, que):
        try:
            #показываем логотипы разработчика и паблишера - ждем заданное время
            if globalvars.StateStack[-1] == PState_DevLogo:
                self.NextStateTime -= que.delta
                if self.NextStateTime <= 0:
                    self.SendCommand(Cmd_DevLogoClose)
            if globalvars.StateStack[-1] == PState_PubLogo:
                self.NextStateTime -= que.delta
                if self.NextStateTime <= 0:
                    self.SendCommand(Cmd_PubLogoClose)
                
            #пауза в игре, быстрое прохождение уровня
            if globalvars.GameSettings.GetBoolAttr("debugMode"):
                if globalvars.StateStack[-1] == PState_Game:
                    if oE.EvtIsKeyDown():
                        if oE.EvtKey() == scraft.Key_F5:
                            globalvars.Frozen = not globalvars.Frozen
                            globalvars.Board.Freeze(globalvars.Frozen)
                        elif oE.EvtKey() == scraft.Key_F6:
                            globalvars.Board.SendCommand(Cmd_DebugFinishLevel)
                        elif oE.EvtKey() == scraft.Key_F7:
                            globalvars.Board.SendCommand(Cmd_DebugLastCustomer)
            
            #обрабатываем ввод имени игрока с клавиатуры
            if globalvars.StateStack[-1] == PState_EnterName:
                if oE.EvtIsKeyDown():
                    self.EnterNameDialog["Text"]["NameErrors"].text = u""
                    tmpName = self.EnterNameDialog["Text"]["Name"].text
                    if scraft.Key_A <= oE.EvtKey() <= scraft.Key_Z:
                        tmpLetter = Const_AllChars[oE.EvtKey() - scraft.Key_A]
                        if oE.IsKeyPressed(scraft.Key_SHIFT) or oE.IsKeyPressed(scraft.Key_RSHIFT):
                            pass
                        else:
                            tmpLetter = string.lower(tmpLetter)
                        tmpName += tmpLetter
                    elif scraft.Key_0 <= oE.EvtKey() <= scraft.Key_9:
                        tmpName += str(oE.EvtKey() - scraft.Key_0)
                    elif oE.EvtKey() == scraft.Key_SPACE:
                        tmpName += " "
                    elif oE.EvtKey() == scraft.Key_BACKSPACE:
                        tmpName = tmpName[0:len(tmpName)-1]
                    elif oE.EvtKey() == scraft.Key_ESC:
                        self.SendCommand(Cmd_EnterNameCancel)
                    elif oE.EvtKey() == scraft.Key_ENTER:
                        self.SendCommand(Cmd_EnterNameOk)
                    if len(tmpName) > Max_NameLen:
                        tmpName = tmpName[0:len(tmpName)-1]
                    self.EnterNameDialog["Text"]["Name"].text = tmpName
                    self.EnterNameDialog["Static"]["TextCursor"].x = self.EnterNameDialog["Text"]["Name"].x + \
                        self.EnterNameDialog["Text"]["Name"].width/2
                    self._UpdateEnterNameDialog()
                
            if oE.EvtIsESC():
                if globalvars.StateStack[-1] == PState_DevLogo:
                    self.SendCommand(Cmd_DevLogoClose)
                elif globalvars.StateStack[-1] == PState_PubLogo:
                    self.SendCommand(Cmd_PubLogoClose)
                elif globalvars.StateStack[-1] == PState_MainMenu:    
                    self._SetState(PState_EndGame)
                elif globalvars.StateStack[-1] == PState_Game:
                    if globalvars.RunMode == RunMode_Test:
                        self._SetState(PState_EndGame)
                    else:
                        self.CallInternalMenu()
                elif globalvars.StateStack[-1] == PState_Help:
                    self.SendCommand(Cmd_HelpClose)
                elif globalvars.StateStack[-1] == PState_Cookbook:
                    self.SendCommand(Cmd_CookbookClose)
                elif globalvars.StateStack[-1] == PState_Options:
                    self._CloseOptionsDialog(False)
                elif globalvars.StateStack[-1] == PState_YesNo:
                    self.SendCommand(Cmd_No)
                elif globalvars.StateStack[-1] == PState_YesNoCancel:
                    self.SendCommand(Cmd_YncCancel)
                elif globalvars.StateStack[-1] == PState_Hiscores:
                    self.SendCommand(Cmd_HiscoresClose)
                elif globalvars.StateStack[-1] == PState_Players:
                    self.SendCommand(Cmd_PlayersCancel)
                elif globalvars.StateStack[-1] == PState_MapCareer:
                    self.SendCommand(Cmd_MapMainMenu)
                elif globalvars.StateStack[-1] == PState_EnterName:
                    self.SendCommand(Cmd_EnterNameCancel)
                elif globalvars.StateStack[-1] == PState_NextLevel:
                    self.SendCommand(Cmd_LvCompleteMainMenu)
                elif globalvars.StateStack[-1] == PState_GameOver:
                    self.SendCommand(Cmd_GameOverMainMenu)
            
            if oE.EvtIsQuit():
                if globalvars.StateStack[-1] == PState_Game:
                    if globalvars.RunMode == RunMode_Test:
                        self._SetState(PState_EndGame)
                    else:
                        self.CallInternalMenu()
                else:
                    self._SetState(PState_EndGame)
        except:
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            
            
        return scraft.CommandStateRepeat
        
    def _ReleaseState(self, state):
        if state == PState_DevLogo:
            self._ShowDialog(self.DevLogo, False)
        elif state == PState_PubLogo:
            self._ShowDialog(self.PubLogo, False)
        elif state == PState_MainMenu:
            self._ShowDialog(self.MainMenuDialog, False)
        elif state == PState_MapCareer:
            self._ShowDialog(self.MapCareerDialog, False)
        elif state == PState_Cookbook:
            self._ShowDialog(self.CookbookDialog, False)
        elif state == PState_Comics:
            self._ShowDialog(self.ComicScreen, False)
        elif state == PState_Intro:
            self._ShowDialog(self.IntroScreen, False)
        elif state == PState_Outro:
            self._ShowDialog(self.OutroScreen, False)
        elif state == PState_StartLevel:
            self._ShowDialog(self.LevelGoalsDialog, False)
        elif state == PState_NextLevel:
            self._ShowDialog(self.LevelCompleteDialog, False)
        elif state == PState_GameOver:
            self._ShowDialog(self.GameOverDialog, False)
        elif state == PState_Players:
            self._ShowDialog(self.PlayersDialog, False)
        elif state == PState_EnterName:
            self._ShowDialog(self.EnterNameDialog, False)
        elif state == PState_Help:
            self._ShowDialog(self.RulesDialog, False)
        elif state == PState_Hiscores:
            self._ShowDialog(self.HiscoresDialog, False)
        elif state == PState_Options:
            self._ShowDialog(self.OptionsDialog, False)
        elif state == PState_YesNo:
            self._ShowDialog(self.YesNoDialog, False)
        elif state == PState_YesNoCancel:
            self._ShowDialog(self.YesNoCancelDialog, False)
        elif state == PState_Game:
            globalvars.Board.Show(False)
            if globalvars.StateStack != [] and globalvars.StateStack[-1] == PState_Game:
                globalvars.Board.Clear()
        if globalvars.StateStack != [] and globalvars.StateStack[-1] == state:
            globalvars.StateStack.pop()
            if len(globalvars.StateStack)>0:
                self._SetState(globalvars.StateStack[-1])
        
    # запуск указанного уровня
    def JustRun(self):
        self._SetState(PState_StartLevel)
        
        
    def _SetState(self, state):
        if globalvars.StateStack == [] or globalvars.StateStack[-1] != state:
            globalvars.StateStack.append(state)
        if state in (PState_Game, PState_InGameMenu, PState_NextLevel,
                     PState_GameOver):
            globalvars.Musician.SetState(MusicState_Game)
        else:
            globalvars.Musician.SetState(MusicState_Menu)
            
        #серый спрайт рисуется под верхним попапом
        if state in (PState_StartLevel, PState_NextLevel, PState_Players, PState_Options):
            self.GraySprite.visible = True
            self.GraySprite.layer = Layer_PopupGray
        elif state in (PState_EnterName, PState_YesNo, PState_YesNoCancel):
            self.GraySprite.visible = True
            self.GraySprite.layer = Layer_2ndPopupGray
        else:
            self.GraySprite.visible = False
            
        if state == PState_StartLevel:
            globalvars.StateStack[-1] = PState_Game
            globalvars.StateStack.append(PState_StartLevel)
            self._ReleaseState(PState_MainMenu)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_PubLogo)
            self._ReleaseState(PState_DevLogo)
            self._ReleaseState(PState_Comics)
            self._ReleaseState(PState_Intro)
            self._ReleaseState(PState_Outro)
            globalvars.Board.Show(True)
            globalvars.Board.LaunchLevel()
            globalvars.Board.Freeze(True)
            self._ShowDialog(self.LevelGoalsDialog, True)
            self._UpdateLevelGoals()
            
        elif state == PState_Game:
            globalvars.Board.Freeze(False)
           
        elif state == PState_DevLogo:
            self._ShowDialog(self.DevLogo, True)
            self._ReleaseState(PState_PubLogo)
            self._ReleaseState(PState_MainMenu)
            self._ReleaseState(PState_Players)
            self._ReleaseState(PState_EnterName)
            self._ReleaseState(PState_Help)
            self._ReleaseState(PState_Options)
            self._ReleaseState(PState_Hiscores)
            self._ReleaseState(PState_YesNo)
            self._ReleaseState(PState_YesNoCancel)
            self._ReleaseState(PState_StartLevel)
            self._ReleaseState(PState_NextLevel)
            self._ReleaseState(PState_GameOver)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_Cookbook)
            self._ReleaseState(PState_Comics)
            self._ReleaseState(PState_Intro)
            self._ReleaseState(PState_Outro)
            self.NextStateTime = Time_DevLogoShow
            
        elif state == PState_PubLogo:
            self._ShowDialog(self.PubLogo, True)
            self._ReleaseState(PState_DevLogo)
            self.NextStateTime = Time_PubLogoShow
            
        elif state == PState_MainMenu:
            self._ShowDialog(self.MainMenuDialog, True)
            self._ReleaseState(PState_PubLogo)
            self._ReleaseState(PState_Players)
            self._ReleaseState(PState_EnterName)
            self._ReleaseState(PState_Help)
            self._ReleaseState(PState_Options)
            self._ReleaseState(PState_Hiscores)
            self._ReleaseState(PState_YesNo)
            self._ReleaseState(PState_YesNoCancel)
            self._ReleaseState(PState_NextLevel)
            self._ReleaseState(PState_GameOver)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_Cookbook)
            if globalvars.GameConfig.GetStrAttr("Player") == "":
                self.MainMenuDialog["Text"]["WelcomeMessage"].visible = False
                self.MainMenuDialog["Buttons"]["Players"].Show(False)
                if len(globalvars.PlayerList.GetPlayerList()) <= 1:
                    self._SetState(PState_EnterName)
                else:
                    self._SetState(PState_Players)
            else:
                self.MainMenuDialog["Buttons"]["Players"].Show(True)
                self.MainMenuDialog["Text"]["WelcomeMessage"].visible = True
                self.MainMenuDialog["Text"]["WelcomeMessage"].text = Str_Menu_Welcome + globalvars.GameConfig.GetStrAttr("Player")
            self.MainMenuDialog["Animations"]["JaneEyes"].SetState("Smile")
            self.MainMenuDialog["Animations"]["JaneEyes"].Freeze(False)
            self.MainMenuDialog["Animations"]["Vapor"].SetState("Play")
            self.MainMenuDialog["Animations"]["Vapor"].Freeze(False)
            
        elif state == PState_MapCareer:
            self._ReleaseState(PState_MainMenu)
            tmpLastLevel = globalvars.CurrentPlayer.LastUnlockedLevel()
            if tmpLastLevel:
                self.SelectedLevel = tmpLastLevel.GetContent()
            else:
                self.SelectedLevel = ""
            self._ShowDialog(self.MapCareerDialog, True)
            self._UpdateMapWindow()
            
        elif state == PState_Comics:
            self._ShowDialog(self.ComicScreen, True)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_MainMenu)
            self._UpdateComics()
            
        elif state == PState_Intro:
            self._ShowDialog(self.IntroScreen, True)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_MainMenu)
            self._ShowEpisodeIntro()
            
        elif state == PState_Outro:
            globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").GetSubtag(self.SelectedLevel))
            self._ShowDialog(self.OutroScreen, True)
            self._ReleaseState(PState_MapCareer)
            self._ReleaseState(PState_MainMenu)
            self._ShowEpisodeOutro()
            
        elif state == PState_NextLevel:
            globalvars.Board.Freeze(True)
            self._ShowDialog(self.LevelCompleteDialog, True)
            
        elif state == PState_GameOver:
            globalvars.Board.Freeze(True)
            self._ShowDialog(self.GameOverDialog, True)
            
        elif state == PState_Players:
            self._ShowDialog(self.PlayersDialog, True)
            self._DrawPlayersList()
            
        elif state == PState_EnterName:
            self._ShowDialog(self.EnterNameDialog, True)
            self._UpdateEnterNameDialog()
            
        elif state == PState_Cookbook:
            self._ShowDialog(self.CookbookDialog, True)
            self._ShowCookBookPage(self.CurrentCookbookPage)
            
        elif state == PState_Help:
            self._ReleaseState(PState_MainMenu)
            self._ShowDialog(self.RulesDialog, True)
            self._ShowHelpPage(self.CurrentHelpPage)
            
        elif state == PState_Hiscores:
            self._ShowDialog(self.MainMenuDialog, True)
            config.UpdateHiscores()
            self._ShowDialog(self.HiscoresDialog, True)
            self._UpdateHiscoresDialog()
            
        elif state == PState_Options:
            globalvars.Board.Freeze(True)
            self.SavedOptions = globalvars.GameConfig.Clone()
            self._ShowDialog(self.OptionsDialog, True)
            self._UpdateOptionsDialog()
            
        elif state == PState_YesNo:
            self._ShowDialog(self.YesNoDialog, True)
            
        elif state == PState_YesNoCancel:
            self._ShowDialog(self.YesNoCancelDialog, True)
            
        elif state == PState_EndGame:
            pass
        
