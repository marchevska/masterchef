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
        self.HighlightSprites = []
        self.SelectedCells = []
        self.SelectedSprites = []
        
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
        for tmp in self.HighlightSprites+self.SelectedSprites:
            tmp.Dispose()
        for spr in self.Background.values() + self.Grid.values() + \
            self.Receptors.values():
            spr.Dispose()
        self.HighlightedCells = []
        self.HighlightSprites = []
        self.SelectedCells = []
        self.SelectedSprites = []
        self.Background = {}
        self.Grid = {}
        self.Receptors = {}
        self.Cells = {}
        
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
                        globalvars.Board.SendCommand(Cmd_ClickStorage, self)        
    
    #--------------------------
    # Подсвечивает группу клеток одного типа под курсором
    #--------------------------
    def _HighlightCells(self, pos, flag):
        if flag:
            self.HighlightSprites = []
            for tmpCell in self.HighlightedCells:
                self.HighlightSprites.append(MakeSimpleSprite(u"cell-marker",
                    Layer_Markers+1, self._CellCoords(tmpCell)[0], self._CellCoords(tmpCell)[1]))
        else:
            for spr in self.HighlightSprites:
                spr.Dispose()
            self.HighlightedCells = []
            self.HighlightSprites = []
        
    #--------------------------
    # Собирает группу токенов на курсор
    #--------------------------
    def PickTokens(self):
        self.SelectedCells = list(self.HighlightedCells)
        self.SelectedSprites = []
        for tmpCell in self.SelectedCells:
            self.SelectedSprites.append(MakeSimpleSprite(u"select-marker",
                Layer_Markers, self._CellCoords(tmpCell)[0], self._CellCoords(tmpCell)[1]))
        
    #--------------------------
    # Сбрасывает группу токенов с курсора - при удалении или сбросе
    #--------------------------
    def DropTokens(self):
        for spr in self.SelectedSprites:
            spr.Dispose()
        self.SelectedSprites = []
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
#--------------------------------------------
#--------------------------------------------
class Store(Storage):
    def __init__(self, cols, rows, x, y, theme):
        Storage.__init__(self, cols, rows, x, y, theme["storage"])
        
        self.Capacity = cols*rows
        self.NoTokens = 0
        self.TokensHeld = map(lambda x: { "item": x, "no": 0 }, globalvars.LevelInfo["IngredientRates"].keys())

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
    def AddTokens(self, type, no):
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
        if globalvars.Board.GameCursorState in (GameCursorState_Default, GameCursorState_Tokens):
            if sprite.cookie == Cmd_Receptor:
                tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                if self.Cells[tmpPos] != Const_EmptyCell:
                    self._HighlightCells(tmpPos, flag)
        
        
#--------------------------------------------
#--------------------------------------------
# Field - игровое поле
#--------------------------------------------
#--------------------------------------------
class Field(Storage):
    def __init__(self, cols, rows, x, y, theme):
        Storage.__init__(self, cols, rows, x, y, theme["field"])
        self.SetState(FieldState_None)
        oE.executor.Schedule(self)
        
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
        tmp = RandomKeyByRates(globalvars.LevelInfo["IngredientRates"])
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
        for (i,j) in self.Cells.keys():
                if not self.MatchMap.has_key((i,j)):
                    self._Compare(i, j, self.Cells[(i,j)], curKind)
                    curKind +=1
        tmpChains = map(lambda x: filter(lambda y: self.MatchMap[y] == x, self.MatchMap.keys()),
                        range(curKind))
        for (i,j) in self.Cells.keys():
            if len(tmpChains[self.MatchMap[i,j]]) < Const_MinimalGroup:
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
                    self.HighlightedCells = filter(lambda x: (x[0]-pos[0])*(x[0]-pos[0])+(x[1]-pos[1])*(x[1]-pos[1]) <= globalvars.GameSettings["magicwandradiussquared"], self.Cells.keys())
                    
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
            self.FallingTime = int(globalvars.GameSettings["tokensfallingtime"]*1000)    
            tmpBasicSpeed = int(1.0*Crd_deltaY/globalvars.GameSettings["tokensfallingtime"])
            for i in range(self.Cols):
                for j in range(self.Rows-1, -1, -1):
                    if self.Cells[i,j] != Const_EmptyCell:
                        tmpEmptyUnder = len(filter(lambda y: self.Cells[i,y] == Const_EmptyCell, range(j+1, self.Rows)))
                        if tmpEmptyUnder > 0:
                            self._SwapCells((i,j), (i,j+tmpEmptyUnder))
                            self.FallingBlocks[i,j+tmpEmptyUnder] = tmpBasicSpeed*tmpEmptyUnder
                tmpEmptyTotal = len(filter(lambda y: self.Cells[i,y] == Const_EmptyCell, range(self.Rows)))
                if tmpEmptyTotal > 0:
                    for j in range(tmpEmptyTotal):
                        self._PutRandomToken((i,j))
                        self.FallingBlocks[i,j] = tmpBasicSpeed*tmpEmptyTotal
            for cell in self.FallingBlocks.keys():
                self.Grid[cell].y = self._CellCoords(cell)[1] - \
                    int(self.FallingBlocks[cell]*self.FallingTime/1000)
                
        #перемешивание токенов на поле
        elif state == FieldState_Shuffle:
            globalvars.Board.SendCommand(Cmd_DropWhatYouCarry)
            self.ShuffleTime = int(globalvars.GameSettings["shuffletime"]*1000)
            
            self.ShufflingBlocks = {}
            tmpBasicSpeedX = int(1.0*Crd_deltaX/globalvars.GameSettings["shuffletime"])
            tmpBasicSpeedY = int(1.0*Crd_deltaY/globalvars.GameSettings["shuffletime"])
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
            self.ConvertionTime = globalvars.GameSettings["magicwandconvertingtime"]
            
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
        if self.State == FieldState_Input:
            if sprite.cookie == Cmd_Receptor:
                tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
                if self.Cells[tmpPos] != Const_EmptyCell:
                    self._HighlightCells(tmpPos, flag)
        
    #--------------------------
    # проверка использования тулзов;
    # если тулзы не используются, то использовать родительскую функцию
    #--------------------------
    def _OnMouseClick(self, sprite, x, y, button):
        if self.State == FieldState_Input:
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
            
            
        
#--------------------------------------------
#--------------------------------------------
# TrashCan - мусорка
#--------------------------------------------
#--------------------------------------------
class TrashCan(scraft.Dispatcher):
    def __init__(self, capacity, x, y, theme):
        self.Capacity = capacity
        self.Dummy = MakeDummySprite(self, Cmd_TrashCan, x, y, 60, 60, Layer_Storage)
        self.TrashCanSprite = MakeSimpleSprite(unicode(theme["trashcan"]), Layer_Storage, x, y)
        self.Indicator = BarIndicator(x-25, y-5, 50, 10,
                    unicode(theme["trashcanBarFull"]), unicode(theme["trashcanBarEmpty"]), Layer_Storage-1)
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
        
