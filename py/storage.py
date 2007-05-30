#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Storage classes
"""

import scraft
from scraft import engine as oE
import globalvars
from customer import Customer
from constants import *
from configconst import *
from guielements import MakeSimpleSprite, MakeDummySprite, MakeSprite, PushButton
from extra import *
import traceback, string
from random import choice, shuffle, random
import time

#--------------------------------------------
# Storage - базовый класс контейнера токенов
#--------------------------------------------

class Storage(scraft.Dispatcher):
    def __init__(self, cols, rows, x, y, klass):
        self.Crd_minX, self.Crd_minY = x, y
        self.Cols, self.Rows = cols, rows
        
        self.Action = Const_HighlightPick
        self.Base = MakeSprite("$spritecraft$dummy$", Layer_Receptors, {"x": x, "y": y })
        self.HighlightedCells = []
        self.Highlight = oE.NewTileMap_(cols+1, rows+1, Crd_deltaX, Layer_HighlightMarkers)
        self.Highlight.AddTilesFrom("cell-highlight")
        self.Highlight.AddTilesFrom("cell-action")
        self.Highlight.AddTilesFrom("cell-use")
        self.Highlight.x = x - Crd_deltaX/2
        self.Highlight.y = y - Crd_deltaY/2
        self.SelectedCells = []
        self.Selection = oE.NewTileMap_(cols+1, rows+1, Crd_deltaX, Layer_SelectMarkers)
        self.Selection.AddTilesFrom("cell-select")
        self.Selection.x = x - Crd_deltaX/2
        self.Selection.y = y - Crd_deltaY/2
        
        self.Background = {}
        self.Grid = {}
        self.Receptors = {}
        self.Cells = {}
        
        for i in range(-1, cols+1):
            for j in range(-1, rows+1):
                #выбираем номер кадра из класса
                if i == -1:
                    if j == -1:
                        tmpFrno = 0
                    elif j == rows:
                        tmpFrno = 6
                    else:
                        tmpFrno = 3
                elif i == cols:
                    if j == -1:
                        tmpFrno = 2
                    elif j == rows:
                        tmpFrno = 8
                    else:
                        tmpFrno = 5
                else:
                    if j == -1:
                        tmpFrno = 1
                    elif j == rows:
                        tmpFrno = 7
                    else:
                        tmpFrno = 4
                self.Background[i,j] = MakeSimpleSprite(klass, Layer_StorageFrame, self._AbsCellCoords((i,j))[0], self._AbsCellCoords((i,j))[1], scraft.HotspotCenter, tmpFrno)
                
                #4 - кадр из середины поял (не рамка), то есть его надо заполнить
                if tmpFrno == 4:
                    self.Receptors[i,j] = MakeDummySprite(self, Cmd_Receptor,
                            self._CellCoords((i,j))[0], self._CellCoords((i,j))[1],
                            Crd_deltaX, Crd_deltaY, Layer_Receptors)
                    self.Receptors[i,j].SetItem(Indexes["Col"], i)
                    self.Receptors[i,j].SetItem(Indexes["Row"], j)
                    self.Receptors[i,j].parent = self.Base
                    self.Grid[i,j] = MakeSimpleSprite(u"$spritecraft$dummy$", Layer_Tokens,
                        self._CellCoordsLeft((i,j))[0], self._CellCoordsLeft((i,j))[1])
                    self.Grid[i,j].parent = self.Base
                    self.Cells[i,j] = Const_EmptyCell
                
    def Clear(self):
        self.Highlight.Clear()
        self.Selection.Clear()
        for spr in self.Background.values() + self.Grid.values() + \
            self.Receptors.values():
            spr.Dispose()
        self.HighlightedCells = []
        self.SelectedCells = []
        self.Background = {}
        self.Grid = {}
        self.Receptors = {}
        self.Cells = {}
        
    def Freeze(self, flag):
        if flag:
            self.Highlight.Clear()
            self.Selection.Clear()
            self.HighlightedCells = []
            self.SelectedCells = []
        
    def _ReHighlight(self):
        #пересчитать подсветку токенов
        tmpPos = self._CellByCoords((oE.mouseX, oE.mouseY))
        if tmpPos in self.Cells.keys():
            if self.Cells[tmpPos] != Const_EmptyCell and tmpPos[1]<self.Rows:
                self._HighlightCells(tmpPos, True)
            else:
                self._HighlightCells(tmpPos, False)
        else:
            self._HighlightCells(tmpPos, False)
        
    def _OnMouseClick(self, sprite, x, y, button):
        if globalvars.StateStack[-1] == PState_Game:
            if button == 2:
                globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
            #elif globalvars.Board.GameCursorState in (GameCursorState_Default, GameCursorState_Tokens):
            else:
                if sprite.cookie == Cmd_Receptor:
                    #tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    tmpPos = self._CellByCoords((sprite.scrX, sprite.scrY))
                    if self.Cells[tmpPos] != Const_EmptyCell and len(self.HighlightedCells)>0:
                        globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
                        #токены - подобрать на мышь
                        self.PickTokens()
                        globalvars.Board.SendCommand(Cmd_PickFromStorage,
                            {"where": self, "type": self.Cells[tmpPos], "no": len(self.HighlightedCells)})        
                    else:
                        if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tokens:
                            #put tokens from mouse
                            globalvars.Board.SendCommand(Cmd_ClickStorage, {"where": self, "pos": tmpPos})        
    
    #--------------------------
    # Подсвечивает группу клеток одного типа под курсором
    #--------------------------
    def _HighlightCells(self, pos, flag):
        if flag:
            tmpFrames = { 0: 0, 1: 1, 2: 3, 3: 2, 4: 15, 5:10, 6: 32, 7:6,
                8: 19, 9: 31, 10: 14, 11: 8, 12: 22, 13: 16, 14: 18, 15: 12 }
            for i in range(self.Cols+1):
                for j in range(self.Rows+1):
                    #проверяем 4 соседние ячейки
                    tmp = ((i-1,j-1) in self.HighlightedCells)*8 + ((i,j-1) in self.HighlightedCells)*4 + \
                        ((i-1,j) in self.HighlightedCells)*2 + ((i,j) in self.HighlightedCells)*1
                    self.Highlight.SetTile(i,j,tmpFrames[tmp]+self.Action)
        else:
            self.Highlight.Clear()
            self.HighlightedCells = []
        
    #--------------------------
    # Собирает группу токенов на курсор
    #--------------------------
    def PickTokens(self):
        self.SelectedCells = list(self.HighlightedCells)
        self._DrawSelection()
        
    def _DrawSelection(self):
        tmpFrames = { 0: 0, 1: 1, 2: 3, 3: 2, 4: 15, 5:10, 6: 32, 7:6,
            8: 19, 9: 31, 10: 14, 11: 8, 12: 22, 13: 16, 14: 18, 15: 12 }
        for i in range(self.Cols+1):
            for j in range(self.Rows+1):
                #проверяем 4 соседние ячейки
                tmp = ((i-1,j-1) in self.SelectedCells)*8 + ((i,j-1) in self.SelectedCells)*4 + \
                    ((i-1,j) in self.SelectedCells)*2 + ((i,j) in self.SelectedCells)*1
                self.Selection.SetTile(i,j,tmpFrames[tmp])
        
    #--------------------------
    # Сбрасывает группу токенов с курсора - при удалении или сбросе
    #--------------------------
    def DropTokens(self):
        self.Selection.Clear()
        self.SelectedCells = []
        
    #--------------------------
    # Удаление токена из заданной клетки
    #--------------------------
    def _RemoveTokenFrom(self, cell):
        self.Cells[cell] = Const_EmptyCell
        self.Grid[cell].ChangeKlassTo(u"$spritecraft$dummy$")
        
    def _AbsCellCoords(self, cell):
        return (self.Crd_minX + cell[0]*Crd_deltaX + Crd_deltaX/2, 
                self.Crd_minY + cell[1]*Crd_deltaY + Crd_deltaY/2)
        
    def _CellCoords(self, cell):
        return (cell[0]*Crd_deltaX + Crd_deltaX/2, 
                cell[1]*Crd_deltaY + Crd_deltaY/2)
        
    def _CellCoordsLeft(self, cell):
        return (cell[0]*Crd_deltaX, 
                cell[1]*Crd_deltaY)
        
    def _CellByCoords(self, crd):
        return (int((crd[0]-self.Base.x)/Crd_deltaX),
                int((crd[1]-self.Base.y)/Crd_deltaY))
        
        
#--------------------------------------------
#--------------------------------------------
# Store - временное хранилище токенов
# Токены сортируются группами одинаковых
#--------------------------------------------
#--------------------------------------------
class Store(Storage):
    def __init__(self, cols, rows, x, y, theme):
        Storage.__init__(self, cols, rows, x, y, theme.GetStrAttr("storage"))
        
        self.Capacity = cols*rows
        self.NoTokens = 0
        self.TokensHeld = map(lambda x: { "item": x, "no": 0 },
            map(lambda x: x.GetStrAttr("type"), globalvars.LevelSettings.GetTag("IngredientRates").Tags("Ingredient")))

    #--------------
    # проверка наличия no свободных клеток
    #--------------
    def HasFreeSlots(self, no):
        if self.Capacity - self.NoTokens >= no:
            return True
        else:
            return False
        
    #--------------
    # добавить "no" токенов типа "type" - без проверки
    #--------------
    def AddTokens(self, type, no, pos):
        try:
            filter(lambda x: x["item"] == type, self.TokensHeld)[0]["no"] += no
            self.NoTokens += no
        except:
            pass
        self.Draw()
        
    #--------------
    # отрисовка
    #--------------
    def Draw(self):
        tmpTokens = reduce(lambda a,b: a+b, map(lambda x: [x["item"]]*x["no"], self.TokensHeld))
        for i in range(self.Cols):
            for j in range(self.Rows):
                tmp = j*self.Cols+i - (self.Capacity - self.NoTokens)  
                if tmp >= 0:
                    self.Cells[i,j] = tmpTokens[tmp]
                    self.Grid[i,j].ChangeKlassTo(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(self.Cells[i,j]).GetStrAttr("src"))
                else:
                    self._RemoveTokenFrom((i,j))
        self._ReHighlight()            
        
    #--------------------------
    # Удаление выделенных токенов с поля
    #--------------------------
    def RemoveTokens(self):
        tmpType = self.Cells[self.SelectedCells[0]]
        #тот самый токен, который удаляют
        tmp = filter(lambda x: x["item"] == tmpType, self.TokensHeld)[0]
        self.NoTokens -= tmp["no"]
        tmp["no"] = 0
        for tmpCell in self.SelectedCells:
            self._RemoveTokenFrom(tmpCell)
        self.Draw()
        
    #--------------------------
    # Подсвечивает группу клеток одного типа под курсором
    #--------------------------
    def _HighlightCells(self, pos, flag):
        if flag:
            self.HighlightedCells = filter(lambda x: self.Cells[x] == self.Cells[pos], self.Cells.keys())
            Storage._HighlightCells(self, pos, True)
        else:
            Storage._HighlightCells(self, (0,0), False)
        
    #--------------------------
    # при движении курсора над полем подсвечивает группы клеток
    #--------------------------
    def _OnMouseOver(self, sprite, flag):
        try:
            if globalvars.StateStack[-1] == PState_Game:
                if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] in (GameCursorState_Default, GameCursorState_Tokens):
                    if sprite.cookie == Cmd_Receptor:
                        #tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                        tmpPos = self._CellByCoords((sprite.scrX, sprite.scrY))
                        if self.Cells.has_key(tmpPos) and self.Cells[tmpPos] != Const_EmptyCell:
                            self._HighlightCells(tmpPos, flag)
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            
        
        
#--------------------------------------------
#--------------------------------------------
# SingularStore - временное хранилище токенов
# Токены можно класть и брать только по одному!
#--------------------------------------------
#--------------------------------------------
class SingularStore(Storage):
    def __init__(self, cols, rows, x, y, theme):
        Storage.__init__(self, cols, rows, x, y, theme.GetStrAttr("storage"))
        
        self.Capacity = cols*rows
        self.NoTokens = 0
        
    #--------------
    # проверка наличия no свободных клеток
    #--------------
    def HasFreeSlots(self, no):
        if self.Capacity - self.NoTokens >= no:
            return True
        else:
            return False
        
    #--------------
    # добавить "no" токенов типа "type" - без проверки
    #--------------
    def AddTokens(self, type, no, pos):
        try:
            self.Cells[pos] = type
            self.Grid[pos].ChangeKlassTo(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(type).GetStrAttr("src"))
            self.NoTokens += no
        except:
            pass
        self.Draw()
        
    #--------------
    # отрисовка
    #--------------
    def Draw(self):
        self._ReHighlight()            
        
    #--------------------------
    # Удаление выделенных токенов с поля
    #--------------------------
    def RemoveTokens(self):
        self.NoTokens -= 1
        self._RemoveTokenFrom(self.SelectedCells[0])
        self.Draw()
        
    #--------------------------
    # Подсвечивает группу клеток одного типа под курсором
    #--------------------------
    def _HighlightCells(self, pos, flag):
        if flag:
            self.HighlightedCells = [pos]
            Storage._HighlightCells(self, pos, True)
        else:
            Storage._HighlightCells(self, (0,0), False)
        
    #--------------------------
    # при движении курсора над полем подсвечивает группы клеток
    #--------------------------
    def _OnMouseOver(self, sprite, flag):
        try:
            if globalvars.StateStack[-1] == PState_Game:
                if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] in (GameCursorState_Default, GameCursorState_Tokens):
                    if sprite.cookie == Cmd_Receptor:
                        #tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                        tmpPos = self._CellByCoords((sprite.scrX, sprite.scrY))
                        if self.Cells.has_key(tmpPos) and self.Cells[tmpPos] != Const_EmptyCell:
                            self._HighlightCells(tmpPos, flag)
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        
        
#--------------------------------------------
#--------------------------------------------
# Field - игровое поле
#--------------------------------------------
#--------------------------------------------
class Field(Storage):
    def __init__(self, cols, rows, x, y, theme):
        Storage.__init__(self, cols, rows, x, y, theme.GetStrAttr("field"))
        self.Collapsing = False
        self.MatchMap = {}
        self.FallingBlocks = {}
        self.SetState(FieldState_None)
        self.QueNo = oE.executor.Schedule(self)
        
    #--------------------------
    # Начальное заполнение поля
    #--------------------------
    def InitialFilling(self):
        for i in range(self.Cols):
            for j in range(self.Rows):
                self._PutRandomToken((i,j))
        
    #--------------------------
    # Поместить произвольный токен в заданную клетку
    #--------------------------
    def _PutRandomToken(self, cell):
        #считаем рекомендованные частоты
        tmpLevelIngredRates = dict(map(lambda x: (x.GetStrAttr("type"), x.GetIntAttr("rate")),
                       globalvars.LevelSettings.GetTag("IngredientRates").Tags("Ingredient")))
        tmpBoardNeeded = dict(globalvars.BlackBoard.Inspect(BBTag_Ingredients))
        tmpRecommendedRates = dict(tmpLevelIngredRates)
        for ing in tmpRecommendedRates.keys():
            tmpRecommendedRates[ing] *= globalvars.GameSettings.GetIntAttr("levelRatesMultiplier")
            if tmpBoardNeeded.has_key(ing):
                tmpRecommendedRates[ing] += tmpBoardNeeded[ing]*globalvars.GameSettings.GetIntAttr("boardNeededMultiplier")
        tmpRecommendedSum = reduce(lambda a,b: a+b, tmpRecommendedRates.values(),0)
        
        #считаем реальные частоты
        tmpRealRates = dict(map(lambda x: (x, len(filter(lambda y: self.Cells[y] == x, self.Cells.keys()))),
                           tmpLevelIngredRates.keys()))
        tmpRealSum = reduce(lambda a,b: a+b, tmpRealRates.values(),0)
        
        #делаем коррекцию, когда реальная частота появления ингредиента превышают рекомендованную
        for ing in tmpRecommendedRates.keys():
            if tmpRealRates[ing]*tmpRecommendedSum > tmpRecommendedRates[ing]*tmpRealSum and \
                    tmpRealSum > globalvars.GameSettings.GetIntAttr("minCorrectionAmount") and tmpRecommendedRates[ing] > 0:
                tmpExceedDelta = 1.0*(tmpRealRates[ing]*tmpRecommendedSum)/(tmpRecommendedRates[ing]*tmpRealSum) - 1.0
                tmpRecommendedRates[ing] = int(1.0*tmpRecommendedRates[ing]*\
                    math.exp(-tmpExceedDelta**2*globalvars.GameSettings.GetFltAttr("expMultiplier")))
        
        tmp = RandomKeyByRates(tmpRecommendedRates)
        self.Cells[cell] = tmp
        self.Grid[cell].ChangeKlassTo(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(tmp).GetStrAttr("src"))
        
    #--------------------------
    # Удаление токенов с поля
    #--------------------------
    def RemoveTokens(self):
        for tmpCell in self.SelectedCells:
            self._RemoveTokenFrom(tmpCell)
        
    def _RemoveTokenFrom(self, cell, explode = True, removeUpper = False):
        if explode:
            p = oE.NewParticles("p"+str(cell), "heart", 0)
            p.dispatcher = self
            p.SetEmissionQuantity(5)
            p.SetEmissionPeriod(33)
            p.count = 20
            p.SetEmitterCf(scraft.EmCfIncAngle, 1, 3)
            p.SetEmitterCf(scraft.EmCfInitDirect, -3.14, 3.14)
            p.SetEmitterCf(scraft.EmCfInitSpeed, 30, 40)
            p.SetEmitterCf(scraft.EmCfIncTrans, 150, 150)
            p.lifeTime = 200
            p.cycled = False
            p.x = self._AbsCellCoords(cell)[0]
            p.y = self._AbsCellCoords(cell)[1]
            p.StartEmission()
        Storage._RemoveTokenFrom(self, cell)
        if removeUpper:
            for j in range(cell[1],0,-1):
                self._SwapCells((cell[0], j), (cell[0], j-1))
        
    def _OnLifetimeOut(self, p) :
        p.Dispose()
        
    #--------------------------
    # Перестановка содержимого двух ячеек
    #--------------------------
    def _SwapCells(self, cell1, cell2):
        tmp = self.Cells[cell1]
        self.Cells[cell1] = self.Cells[cell2]
        self.Cells[cell2] = tmp
        tmp = self.Grid[cell1]
        self.Grid[cell1] = self.Grid[cell2]
        self.Grid[cell2] = tmp
        self.Grid[cell1].x, self.Grid[cell1].y = self._CellCoordsLeft(cell1)
        self.Grid[cell2].x, self.Grid[cell2].y = self._CellCoordsLeft(cell2)
        
    #--------------------------
    # Окрашивает клетки игрового поля по группам одного цвета
    #--------------------------
    def _GenerateMatchMap(self):
        self.MatchMap = {}
        #заглушка для коллапсоида - предотвращает клики по нижнему ряду
        for i in range(self.Cols):
            self.MatchMap[i, self.Rows] = -1
            
        curKind = 0
        #найти и выделить все бонусы - пометить как отдельные бонусы
        for cell in filter(lambda x: self.Cells[x] in map(lambda z: z.GetContent(),
                filter(lambda y: y.GetStrAttr("type") == "bonus", globalvars.CuisineInfo.GetTag("Ingredients").Tags())),
                self.Cells.keys()):
            self.MatchMap[cell] = curKind
            curKind +=1
            
        #все остальное - разметить групами
        tmpAllKeys = filter(lambda x: x[1]<self.Rows, self.Cells.keys())
        for (i,j) in tmpAllKeys:
                if not self.MatchMap.has_key((i,j)):
                    self._Compare(i, j, self.Cells[(i,j)], curKind)
                    curKind +=1
        tmpChains = map(lambda x: filter(lambda y: self.MatchMap[y] == x, self.MatchMap.keys()),
                        range(curKind))
        
        #слишком маленькие группы или пустые клетки - не в счет
        for (i,j) in tmpAllKeys:
            if not self.MatchMap.has_key((i,j)) or self.Cells[i,j] == Const_EmptyCell \
                or len(tmpChains[self.MatchMap[i,j]]) < globalvars.GameSettings.GetIntAttr("tokensGroupMin"):
                self.MatchMap[i,j] = -1
                
    #--------------------------
    # Рекурсивно окрашивает группу клеток одного цвета на игровом поле
    # (i,j) - координаты проверяемой клетки
    # color - цвет, с которым сравнивают клетку
    # kind - номер группы, по которому идет проверка
    #--------------------------
    def _Compare(self, i, j, color, kind):
        if self.MatchMap.has_key((i,j)):
            return    
        if self.Cells.has_key((i,j)):
            if self._ColorMatch(self.Cells[i,j], color):
                    self.MatchMap[i,j] = kind
                    for (dx, dy) in MatchDeltas:
                        self._Compare(i+dx, j+dy, color, kind)
                    
        
    def _ColorMatch(self, color1, color2):
        if color1 == color2:# and color1 >= 0:
            return True
        else:
            return False
        
        
    #--------------------------
    # Подсвечивает группу клеток одного типа под курсором
    #--------------------------
    def _HighlightCells(self, pos, flag):
        if flag:
            tmpAllBonuses = map(lambda z: z.GetContent(),
                filter(lambda y: y.GetStrAttr("type") == "bonus", globalvars.CuisineInfo.GetTag("Ingredients").Tags()))
            
            #сначала проверяем токен под курсором (бонус или обычный токен)
            #если под курсором бонус - проверяем, его надо брать или им действовать на месте
            if self.Cells[pos] in tmpAllBonuses:
                #удаление ряда - посветить горизонталь
                if self.Cells[pos] == 'bonus.removerow':
                    self.HighlightedCells = filter(lambda x: x[1] == pos[1] \
                        and self.Cells[x] != Const_EmptyCell and x[1]<self.Rows, self.Cells.keys())
                    self.Action = Const_HighlightUse
                #бомба - подсветить круг
                elif self.Cells[pos] == 'bonus.bomb':
                    self.HighlightedCells = filter(lambda x: (x[0]-pos[0])*(x[0]-pos[0])+(x[1]-pos[1])*(x[1]-pos[1]) <= \
                        globalvars.GameSettings.GetIntAttr("bombRadiusSquared") \
                        and self.Cells[x] != Const_EmptyCell and x[1]<self.Rows, self.Cells.keys())
                    self.Action = Const_HighlightUse
                #иначе - шафл или скроллбэк
                elif self.Cells[pos] in ('bonus.shuffle', 'bonus.scrollback', 'bonus.hearts'):
                    self.HighlightedCells = [pos]
                    self.Action = Const_HighlightUse
                else:
                    self.HighlightedCells = [pos]
                    self.Action = Const_HighlightPick
            #если под курсором обычный токен - проверяем, что на курсоре
            else:
                #если на курсоре бонус, который действует на токены - подсвечиваем активную область
                if globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool \
                        and globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] in ('bonus.spoon', 'bonus.magicwand'):
                    #ложка - подсветить все клетки поля того же типа
                    if globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] == 'bonus.spoon':
                        self.HighlightedCells = filter(lambda x: self.Cells[x] == self.Cells[pos] and x[1] < self.Rows, self.Cells.keys())
                        self.Action = Const_HighlightAct
                    #волшебная палочка - подсветить круг - и проверить, что мы не размножаем бонусы!
                    elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] == 'bonus.magicwand':
                        if globalvars.GameSettings.GetBoolAttr("allowBonusConvertion"):
                            tmpNonConvertable = [Const_EmptyCell]
                        else:
                            tmpNonConvertable = tmpAllBonuses + [Const_EmptyCell]
                        self.HighlightedCells = filter(lambda x: (x[0]-pos[0])*(x[0]-pos[0])+(x[1]-pos[1])*(x[1]-pos[1]) <= \
                            globalvars.GameSettings.GetIntAttr("magicWandRadiusSquared") \
                            and not self.Cells[x] in tmpNonConvertable \
                            and x[1]<self.Rows, self.Cells.keys())
                        self.Action = Const_HighlightAct
                #если на курсоре бонус, который не действует на токены,
                #или же токены, или вообще ничего нет -
                #то предполагается обмен - подсвечиваем подбираемую группу токенов
                else:
                    self.HighlightedCells = filter(lambda x: self.MatchMap[x] == self.MatchMap[pos], self.MatchMap.keys())
                    self.Action = Const_HighlightPick
                    
            Storage._HighlightCells(self, pos, True)
        else:
            Storage._HighlightCells(self, (0,0), False)
                
    #--------------------------
    # основной цикл
    #--------------------------
    def _OnExecute(self, que) :
        try:
            if self.State == FieldState_StartLevel:
                #красивое падение блоков в начале уровня, по заданной программе
                #выполнить движение токенов; когда оно закончено -
                globalvars.Board.SendCommand(Cmd_MovementFinished)
                self.SetState(FieldState_Input)
                
            elif self.State == FieldState_Input:
                pass
                
            #схлопывание блоков после удаления, по заданной программе
            elif self.State == FieldState_Collapse:
                self.FallingTime = max(self.FallingTime - que.delta, 0)
                for cell in self.FallingBlocks.keys():
                    self.Grid[cell].y = self._CellCoordsLeft(cell)[1] - \
                        int(self.FallingBlocks[cell]*self.FallingTime/1000)
                if self.FallingTime <= 0:
                    self.SetState(FieldState_Input)
                
            #перемешивание блоков
            elif self.State == FieldState_Shuffle:
                self.ShuffleTime = max(self.ShuffleTime - que.delta, 0)
                
                for cell in self.ShufflingBlocks.keys():
                    self.Grid[cell].x = self._CellCoordsLeft(cell)[0] - \
                        int(self.ShufflingBlocks[cell][0]*self.ShuffleTime/1000)
                    self.Grid[cell].y = self._CellCoordsLeft(cell)[1] - \
                        int(self.ShufflingBlocks[cell][1]*self.ShuffleTime/1000)
                #перемещение блоков
                
                if self.ShuffleTime <= 0:
                    self.SetState(FieldState_Input)
                
            #превращение блоков волшебной палочкой 
            elif self.State == FieldState_MagicWandConverting:
                self.ConvertionTime = max(self.ConvertionTime - que.delta, 0)
                
                #превращение блоков
                
                if self.ConvertionTime <= 0:
                    self.SetState(FieldState_Input)
                
            elif self.State == FieldState_EndLevel:
                #красивое падение блоков в конце уровня, по заданной программе
                self.SetState(FieldState_None)
            
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        return scraft.CommandStateRepeat
        
    #--------------------------
    # задает состояние игры
    #--------------------------
    def SetState(self, state, parameter = None):
        self.State = state
        if state == FieldState_None:
            pass
            
        #начало уровня; задать способ появления блоков на поле
        elif state == FieldState_StartLevel:
            pass
                        
        #основной цикл - ожидание ввода игрока
        elif state == FieldState_Input:
            self._GenerateMatchMap()
            self._ReHighlight()
            
        #схлопывание столбцов поля после удаления блоков
        elif state == FieldState_Collapse:
            self.FallingBlocks = {}
            self.FallingTime = int(globalvars.GameSettings.GetFltAttr("tokensFallingTime")*1000)    
            tmpBasicSpeed = int(1.0*Crd_deltaY/globalvars.GameSettings.GetFltAttr("tokensFallingTime"))
            for i in range(self.Cols):
                for j in range(self.Rows-1, -1, -1):
                    if self.Cells[i,j] != Const_EmptyCell:
                        tmpEmptyUnder = len(filter(lambda y: self.Cells[i,y] == Const_EmptyCell, range(j+1, self.Rows)))
                        if tmpEmptyUnder > 0:
                            self._SwapCells((i,j), (i,j+tmpEmptyUnder))
                            self.FallingBlocks[i,j+tmpEmptyUnder] = tmpBasicSpeed*tmpEmptyUnder
                if not self.Collapsing:
                    tmpEmptyTotal = len(filter(lambda y: self.Cells[i,y] == Const_EmptyCell, range(self.Rows)))
                    if tmpEmptyTotal > 0:
                        for j in range(tmpEmptyTotal):
                            self._PutRandomToken((i,j))
                            self.FallingBlocks[i,j] = tmpBasicSpeed*tmpEmptyTotal
            for cell in self.FallingBlocks.keys():
                self.Grid[cell].y = self._CellCoords(cell)[1] - \
                    int(self.FallingBlocks[cell]*self.FallingTime/1000)
            self._GenerateMatchMap()
                
        #перемешивание токенов на поле
        elif state == FieldState_Shuffle:
            globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
            self.ShuffleTime = int(globalvars.GameSettings.GetFltAttr("shuffleTime")*1000)
            self.ShufflingBlocks = {}
            tmpBasicSpeedX = int(1.0*Crd_deltaX/globalvars.GameSettings.GetFltAttr("shuffleTime"))
            tmpBasicSpeedY = int(1.0*Crd_deltaY/globalvars.GameSettings.GetFltAttr("shuffleTime"))
            tmpOldKeys = filter(lambda x: self.Cells[x]!=Const_EmptyCell and x[1]<self.Rows, self.Cells.keys())
            tmpNewKeys = list(tmpOldKeys)
            shuffle(tmpNewKeys)
            tmpValues = map(lambda x: self.Cells[x], tmpOldKeys)
            for i in range(len(tmpOldKeys)):
                self.Cells[tmpNewKeys[i]] = tmpValues[i]
                self.Grid[tmpNewKeys[i]].ChangeKlassTo(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(self.Cells[tmpNewKeys[i]]).GetStrAttr("src"))
                self.Grid[tmpNewKeys[i]].x, self.Grid[tmpNewKeys[i]].y = self._CellCoordsLeft(tmpOldKeys[i])
                self.ShufflingBlocks[tmpNewKeys[i]] = ((tmpNewKeys[i][0]-tmpOldKeys[i][0])*tmpBasicSpeedX,
                    (tmpNewKeys[i][1]-tmpOldKeys[i][1])*tmpBasicSpeedY)
            
        #превращение волшебной палочкой
        elif state == FieldState_MagicWandConverting:
            self.ConvertionTime = globalvars.GameSettings.GetFltAttr("magicWandConvertingTime")
            
            #программа для превращения!
            
            for cell in self.ConvertedCells:
                self.Cells[cell] = parameter
                self.Grid[cell].ChangeKlassTo(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(self.Cells[cell]).GetStrAttr("src"))
                
        #конец уровня; задать способ удаления блоков с поля
        elif state == FieldState_EndLevel:
            pass
        
    #--------------------------
    # при движении курсора над полем подсвечивает группы клеток
    #--------------------------
    def _OnMouseOver(self, sprite, flag):
        try:
            if globalvars.StateStack[-1] == PState_Game:
            #if self.State == FieldState_Input:
                if sprite.cookie == Cmd_Receptor:
                    tmpPos = self._CellByCoords((sprite.scrX, sprite.scrY))
                    #tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    if self.Cells.has_key(tmpPos) and self.Cells[tmpPos] != Const_EmptyCell:
                        self._HighlightCells(tmpPos, flag)
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
                    
        
    #--------------------------
    # проверка использования тулзов;
    # если тулзы не используются, то использовать родительскую функцию
    #--------------------------
    def _OnMouseClick(self, sprite, x, y, button):
        if globalvars.StateStack[-1] == PState_Game:
        #if self.State == FieldState_Input:
            try:
                #tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                tmpPos = self._CellByCoords((x, y))
                if not self.Cells.has_key(tmpPos):
                    return
                tmpAllBonuses = map(lambda z: z.GetContent(),
                    filter(lambda y: y.GetStrAttr("type") == "bonus", globalvars.CuisineInfo.GetTag("Ingredients").Tags()))
                
                #проверяем использование бонуса на поле
                if button == 1 and self.Action == Const_HighlightUse:
                    globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
                    #дествия на месте
                    #шафл - перемешать поле
                    if self.Cells[tmpPos] == 'bonus.shuffle':
                            self._RemoveTokenFrom(tmpPos, False, True)
                            self.SetState(FieldState_Shuffle, tmpPos)
                        
                    #бомба - взрыв
                    elif self.Cells[tmpPos] == 'bonus.bomb':
                        for tmpCell in self.HighlightedCells:
                            self._RemoveTokenFrom(tmpCell, True)
                        self._HighlightCells((0,0), False)
                        self.SetState(FieldState_Collapse)
                        
                    #удаление строки
                    elif self.Cells[tmpPos] == 'bonus.removerow':
                        for tmpCell in self.HighlightedCells:
                            self._RemoveTokenFrom(tmpCell, True)
                        self._HighlightCells((0,0), False)
                        self.SetState(FieldState_Collapse)
                    
                    #обратная прокрутка
                    elif self.Cells[tmpPos] == 'bonus.scrollback' and self.Collapsing:
                        self._HighlightCells((0,0), False)
                        self._RemoveTokenFrom(tmpPos, False, True)
                        self.SetDropperState(DropperState_ScrollBack)
                    
                    #сердечки - подарок всем покупателям
                    elif self.Cells[tmpPos] == 'bonus.hearts':
                        self._HighlightCells((0,0), False)
                        self._RemoveTokenFrom(tmpPos, False, True)
                        globalvars.Board.SendCommand(Cmd_UtilizePowerUp, 'bonus.hearts')
                            
                #проверяем использование бонуса с курсора
                elif button == 1 and self.Action == Const_HighlightAct:
                    #ложка - удалить подсвеченные токены
                    if globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] == 'bonus.spoon':
                        if len(self.HighlightedCells) >0:
                            self._RemoveTokenFrom(self.SelectedCells[0], False, True)
                            globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
                            for tmpCell in self.HighlightedCells:
                                self._RemoveTokenFrom(tmpCell)
                            self._HighlightCells((0,0), False)
                            self.SetState(FieldState_Collapse)
                        
                    #волшебная палочка - превращение токенов
                    elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["tooltype"] == 'bonus.magicwand':
                        if len(self.HighlightedCells) >0:
                            self.ConvertedCells = list(self.HighlightedCells)
                            self.SetState(FieldState_MagicWandConverting, self.Cells[tmpPos])
                            self._RemoveTokenFrom(self.SelectedCells[0], False, True)
                            globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
                            
                elif button == 1 and self.Action == Const_HighlightPick and self.Cells[tmpPos] in tmpAllBonuses:
                    globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
                    self.PickTokens()
                    globalvars.Board.SendCommand(Cmd_PickPowerUp, { "type":self.Cells[tmpPos], "where": self })
                        
                else:
                    Storage._OnMouseClick(self, sprite, x, y, button)
            except:
                oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
            
    def SendCommand(self, cmd, parameter=None):
        if cmd == Cmd_StopDropper:
            pass
        
    def Freeze(self, flag):
        if flag:
            oE.executor.GetQueue(self.QueNo).Suspend()
            Storage.Freeze(self, flag)
        else:
            oE.executor.GetQueue(self.QueNo).Resume()
            
    def Clear(self):
        oE.executor.DismissQueue(self.QueNo)
        Storage.Clear(self)
        
#--------------------------------------------
#--------------------------------------------
# Collapsoid - поле типа игры Collapse
# В нижний ряд выбрасываются новые токены 
#--------------------------------------------
#--------------------------------------------
class Collapsoid(Field):
    def __init__(self, cols, rows, initialrows, delay, dropin, shiftspeed, x, y, theme):
        Storage.__init__(self, cols, rows+1, x, y, theme.GetStrAttr("collapsoid"))
        self.Rows -= 1
        #кнопка для быстрого сколлинга на строку
        self.ScrollButton = PushButton("FastShift", self, Cmd_CollapsoidFashShift, PState_Game,
                                       "$spritecraft$dummy$", [0, 0, 0], Layer_CollapsoidScrollButton,
                                       self._AbsCellCoords((1.0*(cols-1)/2, rows))[0], self._AbsCellCoords((1.0*(cols-1)/2, rows))[1],
                                       Crd_deltaX*cols, Crd_deltaY + 10,
                                       "L"+(cols-2)*"M"+"R", [theme.GetStrAttr("collapsoidDropper"),
                                       theme.GetStrAttr("collapsoidDropperRoll"), theme.GetStrAttr("collapsoidDropperDown")])
        self.MatchMap = {}
        self.FallingBlocks = {}
        self.Collapsing = True
        self.InitialRows = initialrows
        self.Delay = delay
        self.DropIn = dropin
        self.ShiftSpeed = shiftspeed
        self.SetState(FieldState_None)
        self.SetDropperState(DropperState_None)
        self.QueNo = oE.executor.Schedule(self)
        
    #--------------------------
    # Начальное заполнение поля
    #--------------------------
    def InitialFilling(self):
        for i in range(self.Cols):
            for j in range(self.Rows - self.InitialRows, self.Rows):
                self._PutRandomToken((i,j))
        
    #--------------------------
    # Управляет общим состоянием поля
    #--------------------------
    def SetState(self, state, parameter = None):
        if state == FieldState_StartLevel:
            self.SetDropperState(DropperState_Drop)
        elif state == FieldState_EndLevel:
            self.SetDropperState(DropperState_None)
        Field.SetState(self, state, parameter)
        
    #--------------------------
    # Управляет состянием дроппера (выбросом элементов)
    #--------------------------
    def SetDropperState(self, state):
        self.DropperState = state
        if state == DropperState_None:
            pass
            
        elif state == DropperState_Drop:
            self.Dropped = 0
            self.NextDropTime = self.Delay
            
        elif state == DropperState_Burn:
            for cell in self.BurningTokens:
                self._RemoveTokenFrom(cell)
            self.BurningTime = int(1000*globalvars.GameSettings.GetFltAttr("burnCollapsoidTime"))
            
        elif state == DropperState_Move:
            #начало движения: сдвиг базы вниз и
            #подъем всех токенов на 1 строку вверх
            if filter(lambda i: self.Cells[i,self.Rows] != Const_EmptyCell, range(self.Cols)) != []:
                self.Base.y = self.Crd_minY + Crd_deltaY
                self.Highlight.y = self.Crd_minY + Crd_deltaY/2
                self.Selection.y = self.Crd_minY + Crd_deltaY/2
                self.SelectedCells = map(lambda x: (x[0], x[1]-1), self.SelectedCells)
                self._DrawSelection()
                for i in range(self.Cols):
                    self.Receptors[i,0].Dispose()
                for i in range(self.Cols):
                    for j in range(self.Rows):
                        self._SwapCells((i,j), (i,j+1))
                        self.Receptors[i,j] = self.Receptors[i,j+1]
                        self.Receptors[i,j].y = self._CellCoords((i,j))[1]
                for i in range(self.Cols):
                    self.Receptors[i, self.Rows] =  MakeDummySprite(self, Cmd_Receptor,
                            self._CellCoords((i,self.Rows))[0], self._CellCoords((i,self.Rows))[1],
                            Crd_deltaX, Crd_deltaY, Layer_Receptors)
                    self.Receptors[i,self.Rows].SetItem(Indexes["Col"], i)
                    self.Receptors[i,self.Rows].SetItem(Indexes["Row"], self.Rows)
                    self.Receptors[i,self.Rows].parent = self.Base
                self._GenerateMatchMap()
                self._ReHighlight()
                self.DestCrd = 0
                self.Speed = -self.ShiftSpeed
                self.MovingTime = int(1.0*1000*Crd_deltaY/self.ShiftSpeed)
            
        elif state == DropperState_ScrollBack:
            #обратный сдвиг: сжигаем лишние токены, делаем быстрый сдвиг
            noRows = globalvars.GameSettings.GetIntAttr("scrollBackRows")
            self.Base.y = self.Crd_minY - noRows*Crd_deltaY
            self.Highlight.y = self.Crd_minY - Crd_deltaY/2 - noRows*Crd_deltaY
            self.Selection.y = self.Crd_minY - Crd_deltaY/2 - noRows*Crd_deltaY
            self.SelectedCells = filter(lambda y: y[0]<self.Rows, map(lambda x: (x[0], x[1]+noRows), self.SelectedCells))
            self._DrawSelection()
            
            #удалить и сдвинуть
            for tmpCell in filter(lambda (i,j): j >= self.Rows-noRows, self.Cells.keys()):
                if self.Cells[tmpCell] != Const_EmptyCell:
                    self._RemoveTokenFrom(tmpCell, True)
                    if self.FallingBlocks.has_key(tmpCell):
                        self.FallingBlocks.pop(tmpCell)
            for i in range(self.Cols):
                for j in range(self.Rows-1-noRows, -1, -1):
                    self._SwapCells((i,j), (i,j+noRows))
            self._GenerateMatchMap()
            self._ReHighlight()
            
            self.DestCrd = 0
            self.MovingTime = int(1.0*1000*globalvars.GameSettings.GetFltAttr("scrollBackTime"))
            self.Speed = int(noRows*Crd_deltaY/globalvars.GameSettings.GetFltAttr("scrollBackTime"))
            
        
    #--------------------------
    # Основной цикл: сдвиг поля и выброс новых токенов
    #--------------------------
    def _OnExecute(self, que):
        try:
            if self.DropperState == DropperState_Drop:
                self.NextDropTime -= que.delta
                if self.NextDropTime < 0:
                    if self.Dropped < self.Cols:
                        self.Dropped += 1
                        self._PutRandomToken((self.Dropped-1, self.Rows))
                        self.NextDropTime += self.DropIn
                    else:
                        #проверка на переполнение
                        if filter(lambda i: self.Cells[i,0] != Const_EmptyCell, range(self.Cols)) != []:
                            globalvars.Board.SendCommand(Cmd_CollapsoidFull, self)
                        else:
                            self.SetDropperState(DropperState_Move)
                
            elif self.DropperState == DropperState_Burn:
                self.BurningTime -= que.delta
                if self.BurningTime <= 0:
                    self.SetDropperState(DropperState_Move)
                
            elif self.DropperState == DropperState_Move:
                self.MovingTime = max(0, self.MovingTime - que.delta)
                tmpCrd = self.DestCrd - 1.0*self.MovingTime*self.Speed/1000
                self.Base.y = self.Crd_minY + tmpCrd
                self.Highlight.y = self.Crd_minY - Crd_deltaY/2 + tmpCrd
                self.Selection.y = self.Crd_minY - Crd_deltaY/2 + tmpCrd
                if self.MovingTime <= 0:
                    self._FinishMotion()
                    
            elif self.DropperState == DropperState_ScrollBack:
                self.MovingTime = max(0, self.MovingTime - que.delta)
                tmpCrd = self.DestCrd - 1.0*self.MovingTime*self.Speed/1000
                self.Base.y = self.Crd_minY + tmpCrd
                self.Highlight.y = self.Crd_minY - Crd_deltaY/2 + tmpCrd
                self.Selection.y = self.Crd_minY - Crd_deltaY/2 + tmpCrd
                if self.MovingTime <= 0:
                    self._FinishMotion()
                    
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        
        Field._OnExecute(self, que)
        return scraft.CommandStateRepeat
            
    #--------------------------
    # Быстрый сдвиг поля
    #--------------------------
    def _FastShift(self):
        if self.DropperState == DropperState_Drop:
            #завершить выброс новых токенов
            while self.Dropped < self.Cols:
                self.Dropped += 1
                self._PutRandomToken((self.Dropped-1, self.Rows))
        if filter(lambda i: self.Cells[i,0] != Const_EmptyCell, range(self.Cols)) != []:
            if self.DropperState != DropperState_Move:
                globalvars.Board.SendCommand(Cmd_CollapsoidFull, self)
            #уже происходит движение и поле переполнено - ничего не делать
            else:
                return
        else:
            if self.DropperState != DropperState_Move:
                self.SetDropperState(DropperState_Move)
            self._FinishMotion()
            
        
    #--------------------------
    # Завершение сдвига поля
    #--------------------------
    def _FinishMotion(self):
        self.Base.y = self.Crd_minY
        self.Highlight.y = self.Crd_minY - Crd_deltaY/2
        self.Selection.y = self.Crd_minY - Crd_deltaY/2
        self.SetDropperState(DropperState_Drop)
        
    #--------------------------
    # Сжигание верхних токенов
    #--------------------------
    def GetBurnCrd(self):
        self.BurningTokens = filter(lambda x: self.Cells[x]!=Const_EmptyCell and \
            x[1]<globalvars.GameSettings.GetIntAttr("burnCollapsoidRows"), self.Cells.keys())
        return map(lambda x: self._AbsCellCoords(x), self.BurningTokens)
        
    #--------------------------
    # передавать только клики по непустым клеткам или правые клики
    #--------------------------
    def _OnMouseClick(self, sprite, x, y, button):
        if globalvars.StateStack[-1] == PState_Game:
            if (button == 1 and globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] == GameCursorState_Tool) \
                    or button == 2:
                Field._OnMouseClick(self, sprite, x, y, button)
            elif globalvars.BlackBoard.Inspect(BBTag_Cursor)["state"] in (GameCursorState_Default, GameCursorState_Tokens):
                if sprite.cookie == Cmd_Receptor:
                    tmpPos = self._CellByCoords((sprite.scrX, sprite.scrY))
                    #tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    if self.MatchMap[tmpPos] != -1:
                        Field._OnMouseClick(self, sprite, x, y, button)
                    else:
                        #self._FastShift()
                        pass
                            
                            
    def SendCommand(self, cmd, parameter=None):
        if cmd == Cmd_CollapsoidFashShift:
            if self.DropperState in (DropperState_Drop, DropperState_Move):
                self._FastShift()
            
        elif cmd == Cmd_CollapsoidBurn:
            self.SetDropperState(DropperState_Burn)
            
        elif cmd == Cmd_StopDropper:
            if self.DropperState == DropperState_Move:
                self._FastShift()
            self.SetDropperState(DropperState_None)
        
    def Clear(self):
        self.ScrollButton.Kill()
        Field.Clear(self)
        
#--------------------------------------------
#--------------------------------------------
# TrashCan - мусорка
#--------------------------------------------
#--------------------------------------------
class TrashCan(scraft.Dispatcher):
    def __init__(self, capacity, x, y, theme):
        self.Capacity = capacity
        self.Dummy = MakeDummySprite(self, Cmd_TrashCan, x, y, 60, 60, Layer_Storage)
        self.TrashCanSprite = MakeSimpleSprite(unicode(theme.GetStrAttr("trashcan")), Layer_Storage, x, y)
        self.Indicator = BarIndicator(x-25, y-5, 50, 10,
                    theme.GetStrAttr("trashcanBarFull"), theme.GetStrAttr("trashcanBarEmpty"), Layer_Storage-1)
        self.Empty()
        #oE.executor.Schedule(self)
        
    def Show(self, flag):
        self.Dummy.visible = flag
        self.TrashCanSprite.visible = flag
        self.Indicator.Show(flag)
        
    def Discard(self, no):
        self.Contains += no
        if self.Contains >= self.Capacity:
            self.Active = False
        self.Indicator.SetValue(min(1.0*self.Contains/self.Capacity, 1))
        
    def Empty(self):
        self.Contains = 0
        self.Active = True
        self.Indicator.SetValue(0)
        
    def _OnMouseClick(self, sprite, button, x, y):
        if sprite.cookie == Cmd_TrashCan and self.Active:
            globalvars.Board.SendCommand(Cmd_TrashCan, self)
        
    def Kill(self):
        self.Dummy.Dispose()
        self.TrashCanSprite.Dispose()
        self.Indicator.Kill()
        
        
