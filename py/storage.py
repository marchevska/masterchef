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
from guielements import MakeSimpleSprite, MakeDummySprite, PushButton
from extra import *
import traceback, string
from random import choice, shuffle

#--------------------------------------------
# Storage - базовый класс контейнера токенов
#--------------------------------------------

class Storage(scraft.Dispatcher):
    def __init__(self, cols, rows, x, y, klass):
        self.Crd_minX, self.Crd_minY = x, y
        self.Cols, self.Rows = cols, rows
        
        self.HighlightedCells = []
        self.Highlight = oE.NewTileMap_(cols+1, rows+1, Crd_deltaX, Layer_Markers+1)
        self.Highlight.AddTilesFrom("cell-highlight")
        self.Highlight.x = x - Crd_deltaX/2
        self.Highlight.y = y - Crd_deltaY/2
        self.SelectedCells = []
        self.Selection = oE.NewTileMap_(cols+1, rows+1, Crd_deltaX, Layer_Markers)
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
                self.Background[i,j] = MakeSimpleSprite(klass, Layer_Storage, self._CellCoords((i,j))[0], self._CellCoords((i,j))[1], scraft.HotspotCenter, tmpFrno)
                
                #4 - кадр из середины поял (не рамка), то есть его надо заполнить
                if tmpFrno == 4:
                    self.Receptors[i,j] = MakeDummySprite(self, Cmd_Receptor,
                            self._CellCoords((i,j))[0], self._CellCoords((i,j))[1],
                            Crd_deltaX, Crd_deltaY, Layer_Receptors)
                    self.Receptors[i,j].SetItem(Indexes["Col"], i)
                    self.Receptors[i,j].SetItem(Indexes["Row"], j)
                    self.Grid[i,j] = MakeSimpleSprite(u"$spritecraft$dummy$", Layer_Tokens,
                        self._CellCoordsLeft((i,j))[0], self._CellCoordsLeft((i,j))[1])
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
            if self.Cells[tmpPos] != Const_EmptyCell:
                self._HighlightCells(tmpPos, True)
            else:
                self._HighlightCells(tmpPos, False)
        else:
            self._HighlightCells(tmpPos, False)
        
    def _OnMouseClick(self, sprite, x, y, button):
        if globalvars.StateStack[-1] == PState_Game:
            if button == 2:
                globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
            elif globalvars.Board.GameCursorState in (GameCursorState_Default, GameCursorState_Tokens):
                if sprite.cookie == Cmd_Receptor:
                    tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    if self.Cells[tmpPos] != Const_EmptyCell and len(self.HighlightedCells)>0:
                        #pick tokens    
                            globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
                            self.PickTokens()
                            globalvars.Board.SendCommand(Cmd_PickFromStorage,
                                {"where": self, "type": self.Cells[tmpPos], "no": len(self.HighlightedCells)})        
                    else:
                        if globalvars.Board.GameCursorState == GameCursorState_Tokens:
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
                    self.Highlight.SetTile(i,j,tmpFrames[tmp])
        else:
            self.Highlight.Clear()
            self.HighlightedCells = []
        
    #--------------------------
    # Собирает группу токенов на курсор
    #--------------------------
    def PickTokens(self):
        self.SelectedCells = list(self.HighlightedCells)
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
        
    def _CellCoords(self, cell):
        return (self.Crd_minX + cell[0]*Crd_deltaX + Crd_deltaX/2, 
                self.Crd_minY + cell[1]*Crd_deltaY + Crd_deltaY/2)
        
    def _CellCoordsLeft(self, cell):
        return (self.Crd_minX + cell[0]*Crd_deltaX, 
                self.Crd_minY + cell[1]*Crd_deltaY)
        
    def _CellByCoords(self, crd):
        return (int((crd[0] - self.Crd_minX)/Crd_deltaX),
                int((crd[1] - self.Crd_minY)/Crd_deltaY))
        
        
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
                    self.Grid[i,j].ChangeKlassTo(globalvars.CuisineInfo["Ingredients"][self.Cells[i,j]]["src"])
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
                if globalvars.Board.GameCursorState in (GameCursorState_Default, GameCursorState_Tokens):
                    if sprite.cookie == Cmd_Receptor:
                        tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                        if self.Cells[tmpPos] != Const_EmptyCell:
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
            self.Grid[pos].ChangeKlassTo(globalvars.CuisineInfo["Ingredients"][type]["src"])
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
                if globalvars.Board.GameCursorState in (GameCursorState_Default, GameCursorState_Tokens):
                    if sprite.cookie == Cmd_Receptor:
                        tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                        if self.Cells[tmpPos] != Const_EmptyCell:
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
        tmp = RandomKeyByRates(dict(map(lambda x: (x.GetStrAttr("type"), x.GetIntAttr("rate")),
                       globalvars.LevelSettings.GetTag("IngredientRates").Tags("Ingredient"))))
        self.Cells[cell] = tmp
        self.Grid[cell].ChangeKlassTo(globalvars.CuisineInfo["Ingredients"][tmp]["src"])
        
    #--------------------------
    # Удаление токенов с поля
    #--------------------------
    def RemoveTokens(self):
        for tmpCell in self.SelectedCells:
            self._RemoveTokenFrom(tmpCell)
        
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
        curKind = 0
        tmpAllKeys = filter(lambda x: x[1]<self.Rows, self.Cells.keys())
        for (i,j) in tmpAllKeys:
                if not self.MatchMap.has_key((i,j)):
                    self._Compare(i, j, self.Cells[(i,j)], curKind)
                    curKind +=1
        tmpChains = map(lambda x: filter(lambda y: self.MatchMap[y] == x, self.MatchMap.keys()),
                        range(curKind))
        for (i,j) in tmpAllKeys:
            if len(tmpChains[self.MatchMap[i,j]]) < globalvars.GameSettings.GetIntAttr("tokensGroupMin"):
                self.MatchMap[i,j] = -1
        #заглушка для коллапсоида
        for i in range(self.Cols):
            self.MatchMap[i, self.Rows] = -1
                
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
            if globalvars.Board.GameCursorState in (GameCursorState_Default, GameCursorState_Tokens):
                if self.MatchMap[pos] != -1:
                    self.HighlightedCells = filter(lambda x: self.MatchMap[x] == self.MatchMap[pos], self.MatchMap.keys())
                    
            elif globalvars.Board.GameCursorState == GameCursorState_Tool:
                #ложка - подсветить все клетки поля того же типа
                if globalvars.Board.PickedTool == 'Spoon':
                    self.HighlightedCells = filter(lambda x: self.Cells[x] == self.Cells[pos], self.Cells.keys())
                    
                #крест (нож+вилка) - посветить вертикаль и горизонталь
                elif globalvars.Board.PickedTool == 'Cross':
                    self.HighlightedCells = filter(lambda x: x[0] == pos[0] or x[1] == pos[1], self.Cells.keys())
                    
                #волшебная палочка - подсветить круг
                elif globalvars.Board.PickedTool == 'Magicwand':
                    self.HighlightedCells = filter(lambda x: (x[0]-pos[0])*(x[0]-pos[0])+(x[1]-pos[1])*(x[1]-pos[1]) <= \
                        globalvars.GameSettings.GetIntAttr("magicWandRadiusSquared"), self.Cells.keys())
                    
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
            sprite = oE.FindSpriteAtMouse(Layer_Receptors, Layer_Receptors)
            if sprite:
                if sprite.cookie == Cmd_Receptor:
                    tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    if self.Cells[tmpPos] != Const_EmptyCell:
                        self._HighlightCells(tmpPos, flag)
            
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
            tmpOldKeys = self.Cells.keys()
            tmpNewKeys = list(tmpOldKeys)
            shuffle(tmpNewKeys)
            tmpValues = self.Cells.values()
            self.Cells = dict(zip(tmpNewKeys, tmpValues))
            for i in range(len(tmpOldKeys)):
                self.Grid[tmpNewKeys[i]].ChangeKlassTo(globalvars.CuisineInfo["Ingredients"][self.Cells[tmpNewKeys[i]]]["src"])
                self.Grid[tmpNewKeys[i]].x, self.Grid[tmpNewKeys[i]].y = self._CellCoordsLeft(tmpOldKeys[i])
                self.ShufflingBlocks[tmpNewKeys[i]] = ((tmpNewKeys[i][0]-tmpOldKeys[i][0])*tmpBasicSpeedX,
                    (tmpNewKeys[i][1]-tmpOldKeys[i][1])*tmpBasicSpeedY)
            
        #превращение волшебной палочкой
        elif state == FieldState_MagicWandConverting:
            self.ConvertionTime = globalvars.GameSettings.GetFltAttr("magicWandConvertingTime")
            
            #программа для превращения!
            
            for cell in self.ConvertedCells:
                self.Cells[cell] = self.Cells[parameter]
                self.Grid[cell].ChangeKlassTo(globalvars.CuisineInfo["Ingredients"][self.Cells[cell]]["src"])
                
        #конец уровня; задать способ удаления блоков с поля
        elif state == FieldState_EndLevel:
            pass
        
    #--------------------------
    # при движении курсора над полем подсвечивает группы клеток
    #--------------------------
    def _OnMouseOver(self, sprite, flag):
        try:
            if globalvars.StateStack[-1] == PState_Game:
            #if not oE.executor.GetQueue(self.QueNo).IsSuspended():
            #if self.State == FieldState_Input:
                if sprite.cookie == Cmd_Receptor:
                    tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    if self.Cells[tmpPos] != Const_EmptyCell:
                        self._HighlightCells(tmpPos, flag)
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
                    
        
    #--------------------------
    # проверка использования тулзов;
    # если тулзы не используются, то использовать родительскую функцию
    #--------------------------
    def _OnMouseClick(self, sprite, x, y, button):
        if globalvars.StateStack[-1] == PState_Game:
        #if not oE.executor.GetQueue(self.QueNo).IsSuspended():
        #if self.State == FieldState_Input:
            if button == 1 and globalvars.Board.GameCursorState == GameCursorState_Tool:
                #ложка или крест - удалить подсвеченные токены
                if globalvars.Board.PickedTool in ('Cross', 'Spoon'):
                    globalvars.Board.UseTool()
                    for tmpCell in self.HighlightedCells:
                        self._RemoveTokenFrom(tmpCell)
                    self.SetState(FieldState_Collapse)
                #волшебная палочка - превращение токенов
                elif globalvars.Board.PickedTool == 'Magicwand':
                    globalvars.Board.UseTool()
                    tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                    self.ConvertedCells = list(self.HighlightedCells)
                    self.SetState(FieldState_MagicWandConverting, tmpPos)
            else:
                Storage._OnMouseClick(self, sprite, x, y, button)
            
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
    def __init__(self, cols, rows, initialrows, x, y, theme):
        Field.__init__(self, cols, rows+1, x, y, theme)
        self.Collapsing = True
        self.StartRow = 0
        self.Rows -= 1
        self.InitialRows = initialrows
        self.SetDropperState(DropperState_None)
        
    #--------------------------
    # Начальное заполнение поля
    #--------------------------
    def InitialFilling(self):
        for i in range(self.Cols):
            for j in range(self.Rows - self.InitialRows, self.Rows):
                self._PutRandomToken((i,j))
        
    def SetState(self, state, parameter = None):
        if state == FieldState_StartLevel:
            self.SetDropperState(DropperState_Drop)
        elif state == FieldState_EndLevel:
            self.SetDropperState(DropperState_None)
        Field.SetState(self, state, parameter)
        
    def SetDropperState(self, state):
        self.DropperState = state
        if state == DropperState_None:
            pass
            
        elif state == DropperState_Drop:
            self.Dropped = 0
            self.NextDropTime = 200
            
        elif state == DropperState_Move:
            self.MovingTime = 1000
            self.DestCrd = -40
            self.Speed = -40
        
    def _OnExecute(self, que):
        try:
            if self.DropperState == DropperState_Drop:
                self.NextDropTime -= que.delta
                if self.NextDropTime < 0:
                    if self.Dropped < self.Cols:
                        self.Dropped += 1
                        self._PutRandomToken((self.Dropped-1, self.Rows))
                        self.NextDropTime += 200
                    else:
                        self.SetDropperState(DropperState_Move)
                
            elif self.DropperState == DropperState_Move:
                self.MovingTime = max(0, self.MovingTime - que.delta)
                tmpCrd = self.DestCrd - 1.0*self.MovingTime*self.Speed/1000
                oE.SetLayerY(Layer_Tokens, tmpCrd)
                oE.SetLayerY(Layer_Receptors, tmpCrd)
                if self.MovingTime <= 0:
                    oE.SetLayerY(Layer_Tokens, 0)
                    oE.SetLayerY(Layer_Receptors, 0)
                    for i in range(self.Cols):
                        for j in range(self.Rows):
                            self._SwapCells((i,j), (i,j+1))
                    self._GenerateMatchMap()
                    self.SetDropperState(DropperState_Drop)
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        
        Field._OnExecute(self, que)
        return scraft.CommandStateRepeat

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
        
        
