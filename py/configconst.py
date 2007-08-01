#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Project: Master Chef
Список констант для конфигурации игры
"""

import scraft

#размер поля
FieldMinX = 0
FieldMinY = 0
FieldMaxX = 800
FieldMaxY = 600
Crd_deltaX = Crd_deltaY = 40
Video_Mode = scraft.VMODE_800x600x32
Window_Title = "Master Chef"
DEF_Header = "MasterChef"

#имена файлов
File_GameConfig = "data/game.def"
File_Hiscores = "data/scores.def"
File_BestResults = "data/best.def"
File_PlayersConfig = "data/players.def"

File_PlayersConfigSafe = "safe/players.def"
File_DummyProfile = "safe/dummy.def"
File_GameConfigSafe = "safe/game.def"
File_BestResultsSafe = "safe/best.def"

File_SST = "masterchef.sst"

File_Cuisine = "def/cuisine.def"
File_Recipes = "def/recipes.def"
File_GameSettings = "def/gamesettings.def"
File_ResourceInfo = "def/resource.def"
File_Animations = "def/animations.def"
File_LevelProgress = "def/levelprogress.def"
File_GameTexts = "def/text.def"

#сигнатура
Str_SignatureBegin = "signature{\n  value("
Str_SignatureEnd = ")\n}\n"

# стартовые параметры игрока
NewGame_Score = 0
NewLevel_Score = 0

RunMode_Test = 0
RunMode_Play = 1

