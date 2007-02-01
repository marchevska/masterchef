#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Уровни и эпизоды игры
"""

NoEpisodes = 2
Episodes =  [ 
              #название эпизода; количество уровней;
              #классы для фона и слоев: 
              #закрытых и открытых тайлов,
              #мостика и пустых тайлов
              #анимация ловушки и игрока в ловушке
              #список препятствий
              
              ###################
              # эпизод 1 - храм #
              ###################
              
              { "Name": "Temple",
                "NoLevels": 3,
                "Background": u"episode1-bg",
                "ClosedCells": u"episode1-closed",
                "OpenCells": u"episode1-open" ,
                "BridgeCells": u"tiles-safe",
                #"EmptyCells": u"episode1-empty",
                "TrapCells": u"episode1-trap",
                "TrapAnimation": [
                    { "frno": 1, "delay": 400 },
                    { "frno": 2, "delay": 200 },
                    { "frno": 3, "delay": 100 },
                    { "frno": 4, "delay": 100 },
                    { "frno": 0, "delay": 800 }
                ],
                "PlayerTrapped": u"episode1-trap-player",
                "PlayerTrappedAnimation": [
                    { "frno": 0, "delay": 400 },
                    { "frno": 1, "delay": 200 },
                    { "frno": 2, "delay": 100 },
                    { "frno": 3, "delay": 100 },
                    { "frno": 4, "delay": 400 },
                    { "frno": 5, "delay": 400 }
                ],
                "MapSize": (14,11), "MapOrigin": (1,3),
                "CompleteImage": u"episode1-complete",
                "CompleteText": u"Congratulations! You have passed the first dungeon",
                "TotalTiles": 64,
                "Tileset":  [ { "klass": u"e1-bars-topleft",     "base":  0, "no": 16 },
                              { "klass": u"e1-bars-topright",    "base": 16, "no": 16 },
                              { "klass": u"e1-bars-bottomleft",  "base": 32, "no": 16 },
                              { "klass": u"e1-bars-bottomright", "base": 48, "no": 16 },
                              { "klass": u"episode1-empty", "base": 64, "no": 25 }
                            ] },
                #"Tileset":    { 1: u"e1-bar01",  2: u"e1-bar02",  3: u"e1-bar03",  4: u"e1-bar04",
                #                5: u"e1-bar05",  6: u"e1-bar06",  7: u"e1-bar07",  8: u"e1-bar08", 
                #                9: u"e1-bar09", 10: u"e1-bar10", 11: u"e1-bar11", 12: u"e1-bar12" } },
                
              #######################
              # эпизод 2 - гробница #
              #######################
              
              { "Name": "Tomb",
                "NoLevels": 2,
                "Background": u"episode1-bg",
                "ClosedCells": u"episode1-closed",
                "OpenCells": u"episode1-open" ,
                "BridgeCells": u"tiles-safe",
                #"EmptyCells": u"episode1-empty",
                "TrapCells": u"episode1-trap",
                "TrapAnimation": [
                    { "frno": 1, "delay": 400 },
                    { "frno": 2, "delay": 200 },
                    { "frno": 3, "delay": 100 },
                    { "frno": 4, "delay": 100 },
                    { "frno": 0, "delay": 800 }
                ],
                "PlayerTrapped": u"episode1-trap-player",
                "PlayerTrappedAnimation": [
                    { "frno": 0, "delay": 400 },
                    { "frno": 1, "delay": 200 },
                    { "frno": 2, "delay": 100 },
                    { "frno": 3, "delay": 100 },
                    { "frno": 4, "delay": 400 },
                    { "frno": 5, "delay": 400 }
                ],
                "MapSize": (14,11), "MapOrigin": (1,3),
                "CompleteImage": u"episode1-complete",
                "CompleteText": u"Congratulations! You have passed the second dungeon",
                "TotalTiles": 64,
                "Tileset":  [ { "klass": u"e1-bars-topleft",     "base":  0, "no": 16 },
                              { "klass": u"e1-bars-topright",    "base": 16, "no": 16 },
                              { "klass": u"e1-bars-bottomleft",  "base": 32, "no": 16 },
                              { "klass": u"e1-bars-bottomright", "base": 48, "no": 16 },
                              { "klass": u"episode1-empty", "base": 64, "no": 25 }
                            ] },
                #"Tileset":    { 1: u"e1-bar01",  2: u"e1-bar02",  3: u"e1-bar03",  4: u"e1-bar04",
                #                5: u"e1-bar05",  6: u"e1-bar06",  7: u"e1-bar07",  8: u"e1-bar08", 
                #                9: u"e1-bar09", 10: u"e1-bar10", 11: u"e1-bar11", 12: u"e1-bar12" } },
    ]
Levels = [
      #название уровня; 
      #номер эпизода и номер уровня в эпизоде;
      #координаты маркера уровня на карте;
      #время на прохождение в миллис,
      #имя файла уровня
      #уровни с номером 0 - чекпойнты
      { "Name": u"1-1",
        "Episode": 0,
        "NoInEpisode": 0,
        "XYonMap": (250,150),
        "GridSize": (16,17),
        "MinXY": (160,45),
        "StartPos": (8,15),
        "Traps": 5,
        "PassTime": 50000,
        "BonusRates": [ 10, 10, 3, 2, 25 ],
        "Filename": "levels/level1-01.def"
        },
      { "Name": u"1-2",
        "Episode": 0,
        "NoInEpisode": 1,
        "XYonMap": (300,160),
        "GridSize": (16,17),
        "MinXY": (160,45),
        "StartPos": (8,15),
        "Traps": 7,
        "PassTime": 70000,
        "BonusRates": [ 10, 10, 3, 2, 25 ],
        "Filename": "levels/level1-02.def"
        },
      { "Name": u"1-3",
        "Episode": 0,
        "NoInEpisode": 2,
        "XYonMap": (340,180),
        "GridSize": (16,17),
        "MinXY": (160,45),
        "StartPos": (8,15),
        "Traps": 10,
        "PassTime": 80000,
        "BonusRates": [ 10, 10, 3, 2, 25 ],
        "Filename": "levels/level1-03.def"
        },
      { "Name": u"2-1",
        "Episode": 1,
        "NoInEpisode": 0,
        "XYonMap": (370,190),
        "GridSize": (16,17),
        "MinXY": (160,45),
        "StartPos": (8,15),
        "Traps": 12,
        "PassTime": 90000,
        "BonusRates": [ 10, 10, 3, 2, 25 ],
        "Filename": "levels/level2-01.def"
        },
      { "Name": u"2-2",
        "Episode": 1,
        "NoInEpisode": 1,
        "XYonMap": (400,210),
        "GridSize": (16,17),
        "MinXY": (160,45),
        "StartPos": (8,15),
        "Traps": 15,
        "PassTime": 100000,
        "BonusRates": [ 10, 10, 3, 2, 25 ],
        "Filename": "levels/level2-02.def"
        }
    ]

