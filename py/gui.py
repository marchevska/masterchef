#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
���
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
        self.SelectedPlayer = ""                #��� ���������� ������
        self.SelectedLevel = ""                 #�������� ���������� ������ (��� �����)
        self.HilightedLevel = ""      
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
        # �������� ������������ � ��������
        #--------------
        self.DevLogo = { "Static": {}, "Text": {}, "Buttons": {} }
        self.DevLogo["Buttons"]["Back"] = PushButton("",
                self, Cmd_DevLogoClose, PState_DevLogo, "developer-logo", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.PubLogo = { "Static": {}, "Text": {}, "Buttons": {} }
        self.PubLogo["Buttons"]["Back"] = PushButton("",
                self, Cmd_PubLogoClose, PState_PubLogo, "publisher-logo", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
           
        #--------------
        # ������� ����
        #--------------
        self.MainMenuDialog = { "Static": {}, "Text": {}, "Buttons": {}, "Animations": {} }
        self.MainMenuDialog["Static"]["Back"] = MakeSimpleSprite("mainmenu-background", Layer_Background)
        #self.MainMenuDialog["Static"]["Tablet"] = MakeSprite("mainmenu.tablet", Layer_Static,
        #        { "x": 675, "y": 100, "hotspot": scraft.HotspotCenter } )
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
                Str_Menu_Players, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.MainMenuDialog["Text"]["WelcomeMessage"] = MakeSprite("mainmenu.domcasual", Layer_BtnText,
                { "x": 765, "y": 110, "hotspot": scraft.HotspotRightCenter  } )
        self.MainMenuDialog["Text"]["WelcomeName"] = MakeSprite("mainmenu.domcasual", Layer_BtnText,
                { "x": 765, "y": 135, "hotspot": scraft.HotspotRightCenter  } )
        
        #---------
        # �������
        #---------
        self.RulesDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.RulesDialog["Static"]["Back"] = MakeSimpleSprite("help-page1", Layer_Background)
        self.RulesDialog["Buttons"]["HelpPrev"] = PushButton("HelpPrev",
                self, Cmd_HelpPrev, PState_Help,
                "button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 100, 570, 120, 40,
                Str_HelpPrev, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.RulesDialog["Buttons"]["HelpNext"] = PushButton("HelpNext",
                self, Cmd_HelpNext, PState_Help,
                "button-4st", [0, 1, 2, 3], 
                Layer_BtnText, 260, 570, 120, 40,
                Str_HelpNext, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.RulesDialog["Buttons"]["HelpClose"] = PushButton("HelpClose",
                self, Cmd_HelpClose, PState_Help,
                "button-4st", [0, 1, 2], 
                Layer_BtnText, 700, 570, 120, 40,
                Str_HelpClose, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        
        #----------------
        # ���������� �����
        #----------------
        self.CookbookDialog = {"Static": {}, "Text": {}, "Buttons": {}, "Animations": {}}
        self.CookbookDialog["Static"]["Back"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBg)
        self.CookbookDialog["Static"]["Logo"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBtnTxt,
                                                { "x": 50, "y": 50 })
        self.CookbookDialog["Buttons"]["CookbookClose"] = PushButton("CookbookClose",
                self, Cmd_CookbookClose, PState_Cookbook,
                "cookbook.close-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 390, 527, 100, 130)
        self.CookbookDialog["Buttons"]["CookbookContinue"] = PushButton("CookbookContinue",
                self, Cmd_CookbookClose, PState_Cookbook,
                "continue-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 600, 550, 140, 50)
        self.CookbookDialog["Buttons"]["CookbookNext"] = PushButton("CookbookNext",
                self, Cmd_CookbookNext, PState_Cookbook,
                "cookbook.next-button", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 700, 550, 100, 130)
        self.CookbookDialog["Buttons"]["CookbookPrev"] = PushButton("CookbookPrev",
                self, Cmd_CookbookPrev, PState_Cookbook,
                "cookbook.prev-button", [0, 1, 2, 3], 
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
        # ������ �������
        #----------------
        self.PlayersDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.PlayersDialog["Static"]["Back"] = MakeSimpleSprite("popup-background", Layer_PopupBg)
        self.PlayersDialog["Static"]["ListBack"] = MakeSimpleSprite("players-list-background", Layer_PopupStatic, 490, 330)
        self.PlayersDialog["Text"]["Title"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 460, 140,
                                                                   scraft.HotspotCenter, Str_Players_Title)
        self.PlayersDialog["Buttons"]["Remove"] = PushButton("PlayersRemove",
                self, Cmd_PlayersRemove, PState_Players,
                "button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 310, 460, 120, 40,
                Str_PlayersRemove, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.PlayersDialog["Buttons"]["Ok"] = PushButton("PlayersOk",
                self, Cmd_PlayersOk, PState_Players,
                "button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 450, 460, 120, 40,
                Str_PlayersOk, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.PlayersDialog["Buttons"]["Cancel"] = PushButton("PlayersCancel",
                self, Cmd_PlayersCancel, PState_Players,
                "button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 590, 460, 120, 40,
                Str_PlayersCancel, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.PlayersDialog["Buttons"]["Up"] = PushButton("PlayersUp",
                self, Cmd_PlayersUp, PState_Players,
                "players-arrow-up", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 626, 248, 30, 30)
        self.PlayersDialog["Buttons"]["Down"] = PushButton("PlayersDown",
                self, Cmd_PlayersDown, PState_Players,
                "players-arrow-down", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 626, 418, 30, 30)
        self.PlayersDialog["Buttons"]["New"] = PushButton("NewPlayer",
                self, Cmd_PlayersNew, PState_Players,
                "button-4st-300", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 490, 200, 300, 30,
                Str_PlayersNew, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        for i in range(self.TotalPlayersOnScreen):
            self.PlayersDialog["Buttons"]["Player_"+str(i)] = PushButton("PlayerNo"+str(i),
                self, Cmd_PlayersSelect+i, PState_Players,
                "players-select-button", [0, 1, 2, 4, 3], 
                Layer_PopupBtnTxt, 485, 250 + 30 * i, 240, 30,
                "", ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-up", "domcasual-10-up"])
        
        #------------
        # ���� �����
        #------------
        self.EnterNameDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.EnterNameDialog["Static"]["Back"] = MakeSimpleSprite("2nd-popup-background", Layer_2ndPopupBg)
        self.EnterNameDialog["Static"]["TextField"] = MakeSimpleSprite("entername.text-field", Layer_2ndPopupStatic, 400, 293)
        self.EnterNameDialog["Text"]["Title"] = MakeTextSprite("mainmenu.domcasual", Layer_2ndPopupBtnTxt, 400, 248,
                                                    scraft.HotspotCenterTop, Str_EnterName_Title)
        self.EnterNameDialog["Static"]["TextCursor"] = MakeSimpleSprite("textcursor", Layer_2ndPopupBtnTxt, 400, 291)
        self.EnterNameDialog["Static"]["TextCursor"].AnimateLoop(2)
        self.EnterNameDialog["Buttons"]["Ok"] = PushButton("EnterNameOk",
                self, Cmd_EnterNameOk, PState_EnterName,
                "button-4st", [0, 1, 2, 3], 
                Layer_2ndPopupBtnTxt, 330, 342, 120, 40,
                Str_EnterNameOk, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.EnterNameDialog["Buttons"]["Cancel"] = PushButton("EnterNameCancel",
                self, Cmd_EnterNameCancel, PState_EnterName,
                "button-4st", [0, 1, 2, 3], 
                Layer_2ndPopupBtnTxt, 470, 342, 120, 40,
                Str_EnterNameCancel, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.EnterNameDialog["Text"]["Name"] = MakeTextSprite("mainmenu.domcasual", Layer_2ndPopupBtnTxt, 400, 293)
        self.EnterNameDialog["Text"]["NameErrors"] = MakeTextSprite("domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 320)
        self.EnterNameDialog["Text"]["NameErrors"].xScale, self.EnterNameDialog["Text"]["NameErrors"].yScale = 50,50
        
        #------------------
        # ����� ������
        #------------------
        self.LevelGoalsDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.LevelGoalsDialog["Static"]["Back"] = MakeSimpleSprite("level-start.background", Layer_PopupBg)
        self.LevelGoalsDialog["Text"]["Title"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 470, 130,
                                                                scraft.HotspotCenter, Str_LvGoals_Title)
        #level goal parameters
        self.LevelGoalsDialog["Static"]["Indicator1"] = MakeSimpleSprite("level-results.indicator", Layer_PopupStatic, 620, 220)
        self.LevelGoalsDialog["Static"]["Indicator2"] = MakeSimpleSprite("level-results.indicator", Layer_PopupStatic, 620, 270)
        self.LevelGoalsDialog["Static"]["Indicator3"] = MakeSimpleSprite("level-results.indicator", Layer_PopupStatic, 620, 320)
        self.LevelGoalsDialog["Text"]["LabelLevel"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 360, "y": 221, "hotspot": scraft.HotspotLeftCenter, "text": Str_LvGoals_Level })
        self.LevelGoalsDialog["Text"]["LabelGoal"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 360, "y": 271, "hotspot": scraft.HotspotLeftCenter, "text": Str_LvGoals_Goal })
        self.LevelGoalsDialog["Text"]["LabelExpert"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 360, "y": 321, "hotspot": scraft.HotspotLeftCenter, "text": Str_LvGoals_Expert })
        self.LevelGoalsDialog["Text"]["TextLevel"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 583, "y": 221, "hotspot": scraft.HotspotLeftCenter })
        self.LevelGoalsDialog["Text"]["TextGoal"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 583, "y": 271, "hotspot": scraft.HotspotLeftCenter })
        self.LevelGoalsDialog["Text"]["TextExpert"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 583, "y": 321, "hotspot": scraft.HotspotLeftCenter })
        #intro comments and pictures
        self.LevelGoalsDialog["Text"]["IntroTitle"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBtnTxt,
                    { "hotspot": scraft.HotspotCenter })
        self.LevelGoalsDialog["Static"]["IntroPicture"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBtnTxt,
                    { "hotspot": scraft.HotspotCenter })
        self.LevelGoalsDialog["Buttons"]["IntroText"] = TextArea("arial-italic-20", Layer_PopupBtnTxt)
        
        self.LevelGoalsDialog["Buttons"]["Continue"] = PushButton("PlayLevel",
                self, Cmd_LvGoalsPlay, PState_StartLevel,
                "continue-button", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 450, 140, 50)
        
        #------------------
        # ������� ��������
        #------------------
        self.LevelCompleteDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.LevelCompleteDialog["Static"]["Back"] = MakeSprite("$spritecraft$dummy$", Layer_PopupBg)
        self.LevelCompleteDialog["Text"]["Title"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 470, 130,
                                                                   scraft.HotspotCenter, Str_LvComplete_Title)
        self.LevelCompleteDialog["Static"]["Indicator1"] = MakeSimpleSprite("level-results.indicator", Layer_PopupStatic, 620, 206)
        self.LevelCompleteDialog["Static"]["Indicator2"] = MakeSimpleSprite("level-results.indicator", Layer_PopupStatic, 620, 241)
        self.LevelCompleteDialog["Static"]["Indicator3"] = MakeSimpleSprite("level-results.indicator", Layer_PopupStatic, 620, 276)
        self.LevelCompleteDialog["Text"]["LabelServed"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 570, "y": 207, "hotspot": scraft.HotspotRightCenter, "text": Str_LvComplete_Served })
        self.LevelCompleteDialog["Text"]["LabelLost"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 570, "y": 242, "hotspot": scraft.HotspotRightCenter, "text": Str_LvComplete_Lost })
        self.LevelCompleteDialog["Text"]["LabelEarned"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 570, "y": 277, "hotspot": scraft.HotspotRightCenter, "text": Str_LvComplete_Score })
        self.LevelCompleteDialog["Text"]["TextServed"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 583, "y": 207, "hotspot": scraft.HotspotLeftCenter })
        self.LevelCompleteDialog["Text"]["TextLost"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 583, "y": 242, "hotspot": scraft.HotspotLeftCenter })
        self.LevelCompleteDialog["Text"]["TextEarned"] = MakeSprite("mainmenu.domcasual", Layer_PopupBtnTxt,
                    { "x": 583, "y": 277, "hotspot": scraft.HotspotLeftCenter })
        self.LevelCompleteDialog["Buttons"]["Comment"] = TextArea("arial-italic-20", Layer_PopupBtnTxt)
        
        self.LevelCompleteDialog["Static"]["BestSign"] = MakeSimpleSprite("level-results.best-sign",
                                                        Layer_PopupStatic, 500, 365)
        self.LevelCompleteDialog["Static"]["ExpertSign"] = MakeSimpleSprite("level-results.expert-sign",
                                                        Layer_PopupStatic, 610, 365)
        self.LevelCompleteDialog["Buttons"]["Continue"] = PushButton("LvCompleteNextLevel",
                self, Cmd_LvCompleteNextLevel, PState_NextLevel,
                "continue-button", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 450, 140, 50)
        self.LevelCompleteDialog["Buttons"]["Restart"] = PushButton("LvCompleteRestart",
                self, Cmd_LvCompleteRestart, PState_NextLevel,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 400, 120, 40,
                Str_LvCompleteRestart, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.LevelCompleteDialog["Buttons"]["No"] = PushButton("LvCompleteMainMenu",
                self, Cmd_LvCompleteMainMenu, PState_NextLevel,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 600, 450, 120, 40,
                Str_LvCompleteMainMenu, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        
        #---------------
        # ���� ��������
        #---------------
        self.GameOverDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.GameOverDialog["Static"]["Back"] = MakeSimpleSprite("popup-background", Layer_PopupBg)
        self.GameOverDialog["Text"]["Title"] = MakeTextSprite("domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_GameOver_Title)
        self.GameOverDialog["Buttons"]["Hiscores"] = PushButton("GameOverHiscores",
                self, Cmd_GameOverHiscores, PState_GameOver,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 320, 470, 120, 40,
                Str_GameOverHiscores, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.GameOverDialog["Buttons"]["MainMenu"] = PushButton("GameOverMainMenu",
                self, Cmd_GameOverMainMenu, PState_GameOver,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 460, 470, 120, 40,
                Str_GameOverMainMenu, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.GameOverDialog["Text"]["Message"] = MakeTextSprite("domcasual-10-up", Layer_PopupBtnTxt, 320, 200)
        
        #---------
        # �������
        #---------
        self.YesNoDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.YesNoDialog["Static"]["Back"] = MakeSimpleSprite("2nd-popup-background", Layer_2ndPopupBg)
        self.YesNoDialog["Text"]["QuestionText"] = MakeTextSprite("domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 250, scraft.HotspotCenterTop)
        self.YesNoDialog["Buttons"]["Yes"] = PushButton("Yes",
                self, Cmd_Yes, PState_YesNo,
                "button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 330, 342, 120, 40,
                Str_Yes, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.YesNoDialog["Buttons"]["No"] = PushButton("No",
                self, Cmd_No, PState_YesNo,
                "button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 470, 342, 120, 40,
                Str_No, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        
        #---------------
        # Yes-No-Cancel
        #---------------
        self.YesNoCancelDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.YesNoCancelDialog["Static"]["Back"] = MakeSimpleSprite("2nd-popup-background", Layer_2ndPopupBg)
        self.YesNoCancelDialog["Text"]["QuestionText"] = MakeTextSprite("domcasual-10-up", Layer_2ndPopupBtnTxt, 400, 250, scraft.HotspotCenterTop)
        self.YesNoCancelDialog["Buttons"]["Yes"] = PushButton("Yes",
                self, Cmd_YncYes, PState_YesNoCancel,
                "button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 260, 342, 120, 40,
                Str_Yes, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.YesNoCancelDialog["Buttons"]["No"] = PushButton("No",
                self, Cmd_YncNo, PState_YesNoCancel,
                "button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 400, 342, 120, 40,
                Str_No, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.YesNoCancelDialog["Buttons"]["Cancel"] = PushButton("Cancel",
                self, Cmd_YncCancel, PState_YesNoCancel,
                "button-4st", [0, 1, 2], 
                Layer_2ndPopupBtnTxt, 540, 342, 120, 40,
                Str_Cancel, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        
        #-------
        # �����
        #-------
        self.OptionsDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.OptionsDialog["Static"]["Back"] = MakeSimpleSprite("popup-background", Layer_PopupBg)
        self.OptionsDialog["Text"]["Title"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 460, 140,
                                                                   scraft.HotspotCenter, Str_Options_Title)
        self.OptionsDialog["Text"]["Label_Sound"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 360, 220,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelSound)
        self.OptionsDialog["Text"]["Label_Music"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 360, 270,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelMusic)
        self.OptionsDialog["Buttons"]["Slider_Sound"] = Slider("SliderSound", globalvars.GameConfig, 'Sound',
                PState_Options, "options-slider", [0, 1, 2], 
                Layer_PopupBtnTxt, 555, 220, 220, 30, (460, 650), (220, 220), "slider-background")
        self.OptionsDialog["Buttons"]["Slider_Music"] = Slider("SliderMusic", globalvars.GameConfig, 'Music',
                PState_Options, "options-slider", [0, 1, 2], 
                Layer_PopupBtnTxt, 555, 270, 220, 30, (460, 650), (270, 270), "slider-background")
        self.OptionsDialog["Text"]["Label_Mute"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 390, 320,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelMute)
        self.OptionsDialog["Text"]["Label_Hints"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 390, 365,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelHints)
        self.OptionsDialog["Text"]["Label_Fullscreen"] = MakeTextSprite("mainmenu.domcasual", Layer_PopupBtnTxt, 390, 410,
                                                                   scraft.HotspotLeftCenter, Str_Options_LabelFullscreen)
        self.OptionsDialog["Buttons"]["Mute"] = PushButton("OptionsMute",
                self, Cmd_OptionsMute, PState_Options,
                "options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 372, 320, 30, 30)
        self.OptionsDialog["Buttons"]["Hints"] = PushButton("OptionsHints",
                self, Cmd_OptionsHints, PState_Options,
                "options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 372, 365, 30, 30)
        self.OptionsDialog["Buttons"]["Fullscreen"] = PushButton("OptionsFullscreen",
                self, Cmd_OptionsFullscreen, PState_Options,
                "options-checkbox", [0, 1, 2], 
                Layer_PopupBtnTxt, 372, 410, 30, 30)
        self.OptionsDialog["Static"]["Galka_Mute"] = MakeSimpleSprite("options-galka", Layer_PopupBtnTxt2, 372, 320)
        self.OptionsDialog["Static"]["Galka_Hints"] = MakeSimpleSprite("options-galka", Layer_PopupBtnTxt2, 372, 365)
        self.OptionsDialog["Static"]["Galka_Fullscreen"] = MakeSimpleSprite("options-galka", Layer_PopupBtnTxt2, 372, 410)
        self.OptionsDialog["Buttons"]["Ok"] = PushButton("OptionsOk",
                self, Cmd_OptionsOk, PState_Options,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 450, 460, 120, 40,
                Str_OptionsOk, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        #self.OptionsDialog["Buttons"]["Cancel"] = PushButton("Cmd_OptionsCancel",
        #        self, Cmd_OptionsCancel, PState_Options,
        #        "button-4st", [0, 1, 2], 
        #        Layer_PopupBtnTxt, 460, 460, 120, 40,
        #        Str_OptionsCancel, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.OptionsDialog["Buttons"]["Resume"] = PushButton("OptionsResume",
                self, Cmd_IGM_Resume, PState_Options,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 310, 460, 120, 40,
                Str_OptionsResume, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        self.OptionsDialog["Buttons"]["Restart"] = PushButton("OptionsRestart",
                self, Cmd_IGM_Restart, PState_Options,
                "button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 450, 460, 120, 40,
                Str_OptionsRestart, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.OptionsDialog["Buttons"]["EndGame"] = PushButton("OptionsEndGame",
                self, Cmd_IGM_EndGame, PState_Options,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 590, 460, 120, 40,
                Str_OptionsEndGame, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        
        #---------
        # �������
        #---------
        self.HiscoresDialog = {"Static": {}, "Text": {}, "Buttons": {}}
        self.HiscoresDialog["Static"]["Back"] = MakeSimpleSprite("popup-background", Layer_PopupBg)
        self.HiscoresDialog["Text"]["Title"] = MakeTextSprite("domcasual-10-up", Layer_PopupBtnTxt, 400, 165,
                                                                   scraft.HotspotCenter, Str_Hiscores_Title)
        self.HiscoresDialog["Buttons"]["Reset"] = PushButton("HiscoresReset",
                self, Cmd_HiscoresReset, PState_Hiscores,
                "button-4st", [0, 1, 2, 3], 
                Layer_PopupBtnTxt, 330, 500, 120, 40,
                Str_HiscoresReset, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.HiscoresDialog["Buttons"]["Close"] = PushButton("HiscoresClose",
                self, Cmd_HiscoresClose, PState_Hiscores,
                "button-4st", [0, 1, 2], 
                Layer_PopupBtnTxt, 470, 500, 120, 40,
                Str_HiscoresClose, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down"])
        for i in range(Max_Scores):
            self.HiscoresDialog["Text"]["Name_"+str(i)] = MakeTextSprite("domcasual-10-up",
                Layer_PopupBtnTxt, 280, 220 + 30* i, scraft.HotspotLeftCenter)
            self.HiscoresDialog["Text"]["Score_"+str(i)] = MakeTextSprite("domcasual-10-up",
                Layer_PopupBtnTxt, 520, 220 + 30* i, scraft.HotspotRightCenter)
        
        #-------
        # ����� � ��������
        #-------
        self.ComicScreen = {"Static": {}, "Text": {}, "Buttons": {}}
        self.ComicScreen["Buttons"]["Back"] = PushButton("",
                self, Cmd_ComicsNext, PState_Comics, "$spritecraft$dummy$", [0, 0, 0], 
                Layer_Background, 400, 300, 800, 600)
        self.ComicScreen["Buttons"]["Next"] = PushButton("ComicsNext",
                self, Cmd_ComicsNext, PState_Comics,
                "continue-button", [0, 1, 2, 3], 
                Layer_BtnText, 730, 578, 80, 100)
        
        #-------
        # ������� �����
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
            self.IntroScreen["Static"]["Character"+str(i)] = MakeSprite("$spritecraft$dummy$", Layer_BtnText)
            self.IntroScreen["Text"]["Character"+str(i)] = MakeSprite("domcasual-10-up", Layer_BtnText,
                { "x": 640, "y": 340+25*i, "hotspot": scraft.HotspotCenter } )
        
        #-------
        # ���������� ������
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
        # ����� ���������� ������
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
        self.MapCareerDialog["Text"]["LevelTitle"] = MakeSprite("mainmenu.domcasual", Layer_BtnText,
                                                { "x": 170, "y": 460, "hotspot": scraft.HotspotCenter } )
        self.MapCareerDialog["Text"]["BestResult"] = MakeSprite("domcasual-10-up", Layer_BtnText,
                                                { "x": 170, "y": 500, "hotspot": scraft.HotspotCenter } )
        self.MapCareerDialog["Buttons"]["Start"] = PushButton("MapStart",
                self, Cmd_MapStart, PState_MapCareer,
                "map.play.button", [0, 1, 2, 3], 
                Layer_BtnText, 170, 540, 130, 50,
                Str_MapStart, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.MapCareerDialog["Buttons"]["ViewResults"] = PushButton("ViewResults",
                self, Cmd_MapViewResults, PState_MapCareer,
                "map.play.button", [0, 1, 2, 3], 
                Layer_BtnText, 170, 540, 130, 50,
                Str_MapViewResults, ["domcasual-10-up", "domcasual-10-roll", "domcasual-10-down", "domcasual-10-inert"])
        self.MapCareerDialog["Buttons"]["MainMenu"] = PushButton("MapMainMenu",
                self, Cmd_MapMainMenu, PState_MapCareer,
                "map.back-button", [0, 1, 2, 3], 
                Layer_BtnText, 30, 25, 50, 50)
        for tmp in globalvars.LevelProgress.GetTag("Episodes").Tags("episode"):
            self.MapCareerDialog["Static"][tmp.GetContent()] = MakeSprite(tmp.GetStrAttr("image"), Layer_Static,
                { "x": tmp.GetIntAttr("x"), "y": tmp.GetIntAttr("y"), "hotspot": scraft.HotspotCenter })
        for tmp in globalvars.LevelProgress.GetTag("Levels").Tags("level"):
            self.MapCareerDialog["Buttons"][tmp.GetContent()] = PushButton("",
                self, Cmd_MapLevel + tmp.GetIntAttr("no"), PState_MapCareer,
                "level-pointers", [0, 1, 2, 3, 4], Layer_BtnText,
                tmp.GetIntAttr("x"), tmp.GetIntAttr("y"), 30, 30)
        for tmp in globalvars.LevelProgress.GetTag("Levels").Tags("outro"):
            self.MapCareerDialog["Buttons"][tmp.GetContent()] = PushButton("",
                self,
                Cmd_MapOutro + eval(globalvars.GameSettings.GetStrAttr("settings")).index(tmp.GetStrAttr("episode")),
                PState_MapCareer,
                "outro-pointers", [0, 1, 2, 3, 4], Layer_BtnText,
                tmp.GetIntAttr("x"), tmp.GetIntAttr("y"), 30, 30)
        
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
        if flag:
            globalvars.Musician.PlaySound("level.win")
        else:
            globalvars.Musician.PlaySound("level.lose")
            
        #��� � ����������� 
        tmpLevelName = globalvars.CurrentPlayer.GetLevel().GetContent()
        tmpLevelParams = globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpLevelName)
        if not flag:
            self.LevelCompleteDialog["Static"]["Back"].ChangeKlassTo("level-results.bg.bad")
            tmpFailed = eval(tmpLevelParams.GetStrAttr("failed"))
            tmpLayout = globalvars.LevelProgress.GetTag("Layouts").GetSubtag(tmpFailed["layout"])
            self.LevelCompleteDialog["Buttons"]["Comment"].SetParams({ "xy": eval(tmpLayout.GetStrAttr("textXY")),
                "area": eval(tmpLayout.GetStrAttr("textArea")), "klass": tmpLayout.GetStrAttr("textFont"),
                "cfilt-color": eval(tmpLayout.GetStrAttr("textColor")) })
            self.LevelCompleteDialog["Buttons"]["Comment"].SetText(globalvars.GameTexts.GetSubtag(tmpFailed["text"]).GetStrAttr("str"))
        else:
            if  params["expert"]:
                self.LevelCompleteDialog["Static"]["Back"].ChangeKlassTo("level-results.bg.expert")
            else:
                self.LevelCompleteDialog["Static"]["Back"].ChangeKlassTo("level-results.bg.good")
            tmpPassed = eval(tmpLevelParams.GetStrAttr("passed"))
            tmpLayout = globalvars.LevelProgress.GetTag("Layouts").GetSubtag(tmpPassed["layout"])
            self.LevelCompleteDialog["Buttons"]["Comment"].SetParams({ "xy": eval(tmpLayout.GetStrAttr("textXY")),
                "area": eval(tmpLayout.GetStrAttr("textArea")), "klass": tmpLayout.GetStrAttr("textFont"),
                "cfilt-color": eval(tmpLayout.GetStrAttr("textColor")) })
            self.LevelCompleteDialog["Buttons"]["Comment"].SetText(globalvars.GameTexts.GetSubtag(tmpPassed["text"]).GetStrAttr("str"))
            
        self.LevelCompleteDialog["Text"]["TextServed"].text = str(params["served"])
        self.LevelCompleteDialog["Text"]["TextLost"].text = str(params["lost"])
        self.LevelCompleteDialog["Text"]["TextEarned"].text = str(params["score"])
        
        #medals
        tmpBest = globalvars.BestResults.GetSubtag(globalvars.CurrentPlayer.GetLevel().GetContent())
        self.LevelCompleteDialog["Static"]["ExpertSign"].visible = params["expert"]
        self.LevelCompleteDialog["Static"]["BestSign"].visible = \
                (flag and params["score"]==tmpBest.GetIntAttr("hiscore") and params["score"]>0)
        #buttons
        if flag:
            self.LevelCompleteDialog["Buttons"]["Continue"].Show(True)
            self.LevelCompleteDialog["Buttons"]["Restart"].Show(False)
            self.LevelCompleteDialog["Buttons"]["No"].Show(False)
        else:
            self.LevelCompleteDialog["Buttons"]["Continue"].Show(False)
            self.LevelCompleteDialog["Buttons"]["Restart"].Show(True)
            self.LevelCompleteDialog["Buttons"]["No"].Show(True)
        
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
    #���������� �������� �������� ���������� �����
    #----------------------------
    def _ShowCookBookPage(self, no):
        #��������� � ������ ������������ �� ������ ������� ������:
        #�� ���������� �� ����������� �������� �����
        tmpAllSettings = eval(globalvars.GameSettings.GetStrAttr("settings"))
        while not globalvars.CurrentPlayer.GetLevelParams(tmpAllSettings[no]).GetBoolAttr("unlocked") and no>0:
            no -= 1
        tmpSetting = tmpAllSettings[no]
        self.CurrentCookbookPage = no
        
        #���������� �������� ��������
        self.CookbookDialog["Static"]["Back"].ChangeKlassTo(globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("background"))
        self.CookbookDialog["Static"]["Logo"].ChangeKlassTo(globalvars.CookbookInfo.GetSubtag(tmpSetting).GetStrAttr("logo"))
        
        #��������� �������: ��������� ��� ���, ����� ��� ������
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
        
        #������ ������������� ����
        #���� ����� ������� �� �������� ����
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
        #����� - ����� ������� ����� ����������� ������
        else:
            self.CookbookDialog["Buttons"]["CookbookClose"].SetState(ButtonState_Inert)
            self.CookbookDialog["Buttons"]["CookbookContinue"].Show(True)
            self.CookbookDialog["Buttons"]["CookbookPrev"].Show(False)
            self.CookbookDialog["Buttons"]["CookbookNext"].Show(False)

    #----------------------------
    #��������� � �������� �������� �������
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
        self.RulesDialog["Static"]["Back"].ChangeKlassTo("help-page"+str(no+1))
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
    #��������� ������ cancel � ok � ������� ����� �����:
    #���� ������ �� ������� � ������ ������� ����, ������ cancel ������ ���� ��������
    #����� ������ �� �������, ������ ok ������ ���� ��������
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
                self.HiscoresDialog["Text"]["Name_"+str(i)].text = ""
                self.HiscoresDialog["Text"]["Score_"+str(i)].text = ""
        if tmpTotalScores == 0:
            self.HiscoresDialog["Buttons"]["Reset"].SetState(ButtonState_Inert)
        else:
            self.HiscoresDialog["Buttons"]["Reset"].SetState(ButtonState_Up)
        
    #----------------------------
    # �������������� ���� �����
    # ������������ �������� � �������� ������
    #----------------------------
    def _UpdateMapWindow(self):
        #������ ������ �� �����, ������������ ������, �� �� ������ ������ ������� - ��� ����� �������� ���� ������
        tmpOutroKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("outro"))
        for level in tmpOutroKeys:
            #������ ������ �� ������� ������
            tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(level)
            if tmpPlayerResult.GetBoolAttr("expert"):
                self.MapCareerDialog["Buttons"][level].SetButtonKlass("outro-pointers-expert")
            else:
                self.MapCareerDialog["Buttons"][level].SetButtonKlass("outro-pointers")
            if tmpPlayerResult.GetBoolAttr("unlocked"):
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Up)
            else:
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Inert)
        
        tmpLevelKeys = map(lambda x: x.GetContent(), globalvars.LevelProgress.GetTag("Levels").Tags("level"))
        for level in tmpLevelKeys:
            #������ ������ �� ������� ������
            tmpPlayerResult = globalvars.CurrentPlayer.GetLevelParams(level)
            if tmpPlayerResult.GetBoolAttr("expert"):
                self.MapCareerDialog["Buttons"][level].SetButtonKlass("level-pointers-expert")
            else:
                self.MapCareerDialog["Buttons"][level].SetButtonKlass("level-pointers")
            if tmpPlayerResult.GetBoolAttr("unlocked"):
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Up)
            else:
                self.MapCareerDialog["Buttons"][level].SetState(ButtonState_Inert)
        
        #�������� �������� �� self.HilightedLevel
        
        #���� ������ ������� 
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
            self.MapCareerDialog["Text"]["LevelTitle"].text = \
                globalvars.LevelProgress.GetTag("Levels").GetSubtag(self.SelectedLevel).GetStrAttr("title")
        #���������
        elif self.SelectedLevel in tmpOutroKeys:
            self.MapCareerDialog["Buttons"]["ViewResults"].Show(True)
            self.MapCareerDialog["Buttons"]["Start"].Show(False)
            self.MapCareerDialog["Buttons"][self.SelectedLevel].SetState(ButtonState_Selected)
            self.MapCareerDialog["Text"]["BestResult"].text = self.SelectedLevel
            self.MapCareerDialog["Text"]["LevelTitle"].text = \
                globalvars.LevelProgress.GetTag("Levels").GetSubtag(self.SelectedLevel).GetStrAttr("title")
        else:
            self.MapCareerDialog["Buttons"]["ViewResults"].Show(False)
            self.MapCareerDialog["Buttons"]["Start"].Show(True)
            self.MapCareerDialog["Buttons"]["Start"].SetState(ButtonState_Inert)
            self.MapCareerDialog["Text"]["BestResult"].text = ""
        #���������� �������� �������� - ��������� ��� ��� ���
        for tmp in globalvars.LevelProgress.GetTag("Episodes").Tags("episode"):
            if globalvars.CurrentPlayer.GetLevelParams(tmp.GetContent()).GetBoolAttr("unlocked"):
                self.MapCareerDialog["Static"][tmp.GetContent()].frno = 0
            else:
                self.MapCareerDialog["Static"][tmp.GetContent()].frno = 1
        self.MapCareerDialog["Animations"]["JaneEyes"].SetState("Smile")
        self.MapCareerDialog["Animations"]["JaneEyes"].Freeze(False)
        
    #-------------------------------------------
    # �������� ������� ���� �������
    #-------------------------------------------
    def _UpdateComics(self):
        tmp = globalvars.CurrentPlayer.GetLevel()
        self.ComicScreen["Buttons"]["Back"].SetButtonKlass(tmp.GetStrAttr("image"))
        self.ComicScreen["Buttons"]["Next"].SetButtonKlass(tmp.GetStrAttr("button"))
        
    #-------------------------------------------
    # �������� ������� ����� ���������� �������
    #-------------------------------------------
    def _ShowEpisodeIntro(self):
        globalvars.Musician.PlaySound("episode.intro")
        tmpEpisode = globalvars.CurrentPlayer.GetLevel().GetStrAttr("episode")
        tmp = globalvars.ThemesInfo.GetSubtag(tmpEpisode)
        tmpCharacters = eval(globalvars.LevelProgress.GetTag("People").GetSubtag(tmpEpisode).GetStrAttr("people")).items()
        self.IntroScreen["Buttons"]["Back"].SetButtonKlass(tmp.GetStrAttr("background"))
        self.IntroScreen["Static"]["IntroPane"].ChangeKlassTo(tmp.GetStrAttr("introPane"))
        self.IntroScreen["Text"]["Title"].text = globalvars.CurrentPlayer.GetLevel().GetStrAttr("title")
        for i in range(self.MaxPeopleOnLevel):
            if i < len(tmpCharacters):
                self.IntroScreen["Static"]["Character"+str(i)].\
                    ChangeKlassTo(globalvars.CompetitorsInfo.GetSubtag(tmpCharacters[i][0]).GetStrAttr("src"))
                self.IntroScreen["Static"]["Character"+str(i)].x, self.IntroScreen["Static"]["Character"+str(i)].y = tmpCharacters[i][1]["xy"]
                self.IntroScreen["Static"]["Character"+str(i)].hotspot = scraft.HotspotCenterBottom
                self.IntroScreen["Text"]["Character"+str(i)].text = str(i+1)+". "+tmpCharacters[i][0]
            else:
                self.IntroScreen["Static"]["Character"+str(i)].ChangeKlassTo("$spritecraft$dummy$")
                self.IntroScreen["Text"]["Character"+str(i)].text = ""
        
    #-------------------------------------------
    # �������� �������� ����� ���������� �������
    #-------------------------------------------
    def _ShowEpisodeOutro(self):
        tmpLevel = globalvars.CurrentPlayer.GetLevel()
        tmpEpisode = tmpLevel.GetStrAttr("episode")
        tmp = globalvars.ThemesInfo.GetSubtag(tmpEpisode)
        tmpResults = globalvars.CurrentPlayer.GetScoresPlaceAndCondition()
        
        if tmpResults["pass"]:
            globalvars.Musician.PlaySound("episode.win")
        else:
            globalvars.Musician.PlaySound("episode.lose")
            
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
    # �������� ������ � ������� "���� ������", ��� ������ ������
    #-------------------------------------------
    def _UpdateLevelGoals(self):
        tmpLevelName = globalvars.CurrentPlayer.GetLevel().GetContent()
        tmpLevelParams = globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpLevelName)
        self.LevelGoalsDialog["Text"]["Title"].text = tmpLevelParams.GetStrAttr("title")
        self.LevelGoalsDialog["Text"]["TextLevel"].text = tmpLevelParams.GetStrAttr("name")
        self.LevelGoalsDialog["Text"]["TextGoal"].text = str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("moneyGoal"))
        self.LevelGoalsDialog["Text"]["TextExpert"].text = str(globalvars.LevelSettings.GetTag("LevelSettings").GetIntAttr("expertGoal"))
        
        tmpIntro = eval(tmpLevelParams.GetStrAttr("intro"))
        tmpLayout = globalvars.LevelProgress.GetTag("Layouts").GetSubtag(tmpIntro["layout"])
        self.LevelGoalsDialog["Text"]["IntroTitle"].ChangeKlassTo(tmpLayout.GetStrAttr("titleFont"))
        self.LevelGoalsDialog["Text"]["IntroTitle"].x, self.LevelGoalsDialog["Text"]["IntroTitle"].y = \
            eval(tmpLayout.GetStrAttr("titleXY"))
        self.LevelGoalsDialog["Text"]["IntroTitle"].cfilt.color = eval(tmpLayout.GetStrAttr("titleColor"))
        self.LevelGoalsDialog["Text"]["IntroTitle"].hotspot = scraft.HotspotCenter
        self.LevelGoalsDialog["Text"]["IntroTitle"].text = globalvars.GameTexts.GetSubtag(tmpIntro["title"]).GetStrAttr("str")
        self.LevelGoalsDialog["Buttons"]["IntroText"].SetParams({ "xy": eval(tmpLayout.GetStrAttr("textXY")),
            "area": eval(tmpLayout.GetStrAttr("textArea")), "klass": tmpLayout.GetStrAttr("textFont"),
            "cfilt-color": eval(tmpLayout.GetStrAttr("textColor")) })
        self.LevelGoalsDialog["Buttons"]["IntroText"].SetText(globalvars.GameTexts.GetSubtag(tmpIntro["text"]).GetStrAttr("str"))
        if tmpLayout.GetBoolAttr("hasPicture"):
            self.LevelGoalsDialog["Static"]["IntroPicture"].ChangeKlassTo(tmpIntro["picture"])
            if tmpIntro.has_key("frno"):
                self.LevelGoalsDialog["Static"]["IntroPicture"].frno = tmpIntro["frno"]
            else:
                self.LevelGoalsDialog["Static"]["IntroPicture"].frno = 0
            self.LevelGoalsDialog["Static"]["IntroPicture"].x, self.LevelGoalsDialog["Static"]["IntroPicture"].y = \
                eval(tmpLayout.GetStrAttr("pictureXY"))
            self.LevelGoalsDialog["Static"]["IntroPicture"].hotspot = eval(tmpLayout.GetStrAttr("hotspot"))
        else:
            self.LevelGoalsDialog["Static"]["IntroPicture"].ChangeKlassTo("$spritecraft$dummy$")
        
    #-------------------------------------------
    # �������� ������ � ������� - �������� ������ �� ������� ������
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
    # ������� ������ � ������� ��� ������-������� ���� - ��������� ���������� �����
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
    # ������� � ���������� ������� ��� ������
    # ������� ���������� ��� ������ ����� � ��� �������� �������
    #-------------------------------------------
    def NextCareerStage(self):
        try:
            self._ReleaseState(PState_Game)
            self._ReleaseState(PState_Comics)
            self._ReleaseState(PState_Intro)
            self._ReleaseState(PState_Outro)
            #�������� �� ������ ������� � ������� ��������� �����������
            tmpAllUnlocked = filter(lambda x: globalvars.CurrentPlayer.GetLevelParams(x.GetContent()).GetBoolAttr("unlocked"),
                                        globalvars.LevelProgress.GetTag("Levels").Tags())
            tmpLastUnlocked = tmpAllUnlocked[-1]
            tmpNoUnlockedLevels = len(filter(lambda x: x.GetName() == "level", tmpAllUnlocked))
            tmpNewUnlocked = globalvars.CurrentPlayer.NewUnlockedLevel() #str
                
            #���������� �������
            if tmpNewUnlocked != "" and \
                    globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewUnlocked).GetName() == "outro":
                globalvars.CurrentPlayer.PopNewUnlockedLevel()
                globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").GetSubtag(tmpNewUnlocked))
                self._SetState(PState_Outro)
            #���� ��������� ����������� - ������, �� �������� ������
            elif tmpLastUnlocked.GetName() == "comic":
                #���� ��� ��������� ������, � ��� ��� ������ - �������� ����� �����
                if not tmpLastUnlocked.Next() and \
                        globalvars.CurrentPlayer.GetLevelParams(tmpLastUnlocked.GetContent()).GetBoolAttr("seen"):
                    self._SetState(PState_MapCareer)
                else:
                    globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
                    self._SetState(PState_Comics)
            #������� �������� �������
            elif tmpLastUnlocked.GetName() == "intro":
                globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
                self._SetState(PState_Intro)
            #�����: ������� ���������� ����������� �������
            #���� ������ 1, �� ���������� �����
            elif tmpNoUnlockedLevels > 1:
                self._SetState(PState_MapCareer)
            #����� ��������� ������ �������
            else:
                globalvars.CurrentPlayer.SetLevel(tmpLastUnlocked)
                self._SetState(PState_StartLevel)
        except:
            oE.Log("Next stage fatal error")
            oE.Log(string.join(apply(traceback.format_exception, sys.exc_info())))
            sys.exit()
        
        
    #-------------------------------------------
    # ��������� ������ �� ������
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
                    globalvars.CurrentPlayer.SetLevel(globalvars.LevelProgress.GetTag("Levels").GetSubtag(self.SelectedLevel))
                    self._SetState(PState_Outro)
                elif cmd == Cmd_MapMainMenu:
                    self._ReleaseState(PState_MapCareer)
                else:
                    if cmd >= Cmd_MapOutro:
                        self.SelectedLevel = defs.GetTagWithAttribute(globalvars.LevelProgress.GetTag("Levels"),
                                "outro", "episode",
                                eval(globalvars.GameSettings.GetStrAttr("settings"))[cmd-Cmd_MapOutro]).GetContent()
                    else:
                        self.SelectedLevel = defs.GetTagWithAttribute(globalvars.LevelProgress.GetTag("Levels"),
                                            "level", "no", str(cmd-Cmd_MapLevel)).GetContent()
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
                        if globalvars.StateStack[-2] == PState_MainMenu:
                            globalvars.PlayerList.SelectPlayer(self.SelectedPlayer)
                        else:
                            self._DrawPlayersList()
                elif cmd == Cmd_EnterNameCancel:
                    pass
                self.EnterNameDialog["Text"]["Name"].text = ""
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
                if cmd == Cmd_LvCompleteNextLevel:
                    tmpSetting = globalvars.LevelSettings.GetTag("Layout").GetStrAttr("theme")
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
                    self._ReleaseState(PState_Game)
                
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
            #���������� �������� ������������ � ��������� - ���� �������� �����
            if globalvars.StateStack[-1] == PState_DevLogo:
                self.NextStateTime -= que.delta
                if self.NextStateTime <= 0:
                    self.SendCommand(Cmd_DevLogoClose)
            if globalvars.StateStack[-1] == PState_PubLogo:
                self.NextStateTime -= que.delta
                if self.NextStateTime <= 0:
                    self.SendCommand(Cmd_PubLogoClose)
                
            #����� � ����, ������� ����������� ������
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
                        elif oE.EvtKey() == scraft.Key_F8:
                            globalvars.Board.SendCommand(Cmd_DebugLoseLevel)
            
            #������������ ���� ����� ������ � ����������
            if globalvars.StateStack[-1] == PState_EnterName:
                if oE.EvtIsKeyDown():
                    self.EnterNameDialog["Text"]["NameErrors"].text = ""
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
        
    # ������ ���������� ������
    def JustRun(self):
        self._SetState(PState_StartLevel)
        
        
    def _SetState(self, state):
        if globalvars.StateStack == [] or globalvars.StateStack[-1] != state:
            globalvars.StateStack.append(state)
        if state in (PState_Game, PState_NextLevel, PState_StartLevel,
                     PState_GameOver, PState_InGameMenu):
            globalvars.Musician.SetState(MusicState_Game)
        #elif state == PState_InGameMenu:
        #    globalvars.Musician.SetState(MusicState_Pause)
        elif state == PState_MapCareer:
            globalvars.Musician.SetState(MusicState_Map)
        else:
            globalvars.Musician.SetState(MusicState_Menu)
            
        #����� ������ �������� ��� ������� �������
        if state in (PState_StartLevel, PState_NextLevel, PState_Players, PState_Options):
            self.GraySprite.visible = True
            self.GraySprite.layer = Layer_PopupGray
        elif state in (PState_EnterName, PState_YesNo, PState_YesNoCancel):
            self.GraySprite.visible = True
            self.GraySprite.layer = Layer_2ndPopupGray
        else:
            self.GraySprite.visible = False
            
        if state == PState_StartLevel:
            globalvars.Musician.PlaySound("level.start")
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
                self.MainMenuDialog["Text"]["WelcomeName"].visible = False
                self.MainMenuDialog["Buttons"]["Players"].Show(False)
                if len(globalvars.PlayerList.GetPlayerList()) <= 1:
                    self._SetState(PState_EnterName)
                else:
                    self._SetState(PState_Players)
            else:
                self.MainMenuDialog["Buttons"]["Players"].Show(True)
                self.MainMenuDialog["Text"]["WelcomeMessage"].visible = True
                self.MainMenuDialog["Text"]["WelcomeName"].visible = True
                self.MainMenuDialog["Text"]["WelcomeMessage"].text = Str_Menu_Welcome
                self.MainMenuDialog["Text"]["WelcomeName"].text = globalvars.GameConfig.GetStrAttr("Player")
            self.MainMenuDialog["Animations"]["JaneEyes"].SetState("Smile")
            self.MainMenuDialog["Animations"]["JaneEyes"].Freeze(False)
            self.MainMenuDialog["Animations"]["Vapor"].SetState("Play")
            self.MainMenuDialog["Animations"]["Vapor"].Freeze(False)
            
        elif state == PState_MapCareer:
            self._ReleaseState(PState_MainMenu)
            #��������� ������ �� �������: ���� ���������� ���������� �������,
            #���� ���������� ���������
            if globalvars.CurrentPlayer.NewUnlockedLevel() != "":
                globalvars.Musician.PlaySound("map.newlevel")
                self.HilightedLevel = self.SelectedLevel = globalvars.CurrentPlayer.NewUnlockedLevel()
                globalvars.CurrentPlayer.PopNewUnlockedLevel()
            if self.SelectedLevel == "":
                self.SelectedLevel = globalvars.CurrentPlayer.LastUnlockedLevel()
                self.HilightedLevel = ""
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
            self.EnterNameDialog["Text"]["Name"].text = ""
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
        
