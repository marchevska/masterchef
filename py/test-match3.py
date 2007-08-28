#!/usr/bin/env python
# -*- coding: cp1251 -*-

"""
Project: Master Chef
Тест match3 механики
"""

import scraft
from scraft import engine as oE
import globalvars
import defs
from constants import *
from configconst import *
from guielements import MakeSimpleSprite, MakeDummySprite, PushButton
from extra import *
import traceback, string

TokenRates = { "tomato": 5, "flour": 5, "avocado": 5,
              "meat": 5, "shrimp": 5, "salmon": 5,
              "rice": 0 }
MatchDeltasHor = ((-1, 0), (1, 0))
MatchDeltasVer = ((0, -1), (0, 1))
TmpMovingTime = 200
Const_MinimalGroup = 3

#---------------------
# класс игрового поля
#---------------------

class Storage(scraft.Dispatcher):
    def __init__(self, cols, rows, x, y):
        self.Crd_minX, self.Crd_minY = x, y
        self.Cols, self.Rows = cols, rows
        
        self.MatchMap = {}
        self.Chains = []
        self.Grid = {}
        self.Receptors = {}
        self.Cells = {}
        self.MovingTiles = {}
        
        for i in range(cols):
            for j in range(rows):
                    self.Receptors[i,j] = MakeDummySprite(self, Cmd_Receptor,
                            self._CellCoords((i,j))[0], self._CellCoords((i,j))[1],
                            Crd_deltaX, Crd_deltaY, Layer_Receptors)
                    self.Receptors[i,j].SetItem(Indexes["Col"], i)
                    self.Receptors[i,j].SetItem(Indexes["Row"], j)
                    self.Grid[i,j] = MakeSimpleSprite(u"$spritecraft$dummy$", Layer_Tokens,
                        self._CellCoordsLeft((i,j))[0], self._CellCoordsLeft((i,j))[1])
                    self.Cells[i,j] = Const_EmptyCell
        self.QueNo = oE.executor.Schedule(self)
                
        
    #--------------------------
    # Начальное заполнение поля
    #--------------------------
    def InitialFilling(self):
        for (i, j) in self.Cells.keys():
            self._PutRandomToken((i,j))
        
    def _PutRandomToken(self, cell):
        tmp = RandomKeyByRates(TokenRates)
        self.Cells[cell] = tmp
        self.Grid[cell].ChangeKlassTo(globalvars.CuisineInfo.GetTag("Ingredients").GetSubtag(tmp).GetStrAttr("src"))
        
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
        curKind = 0
        tmpChains = {}
        for direction in (MatchDeltasHor, MatchDeltasVer):
            self.MatchMap[direction] = {}
            for (i,j) in self.Cells.keys():
                if not (i,j) in self.MovingTiles.keys():
                    if not self.MatchMap[direction].has_key((i,j)):
                        self._Compare(i, j, self.Cells[(i,j)], curKind, direction)
                        curKind +=1
            tmpChains[direction] = map(lambda x: filter(lambda y: self.MatchMap[direction][y] == x, self.MatchMap[direction].keys()),
                            range(curKind))
        self.Chains = filter(lambda x: len(x)>=Const_MinimalGroup, tmpChains[MatchDeltasHor] + tmpChains[MatchDeltasVer])
                
    #--------------------------
    # Рекурсивно окрашивает линию клеток одного цвета в заданном направлении
    # (i,j) - координаты проверяемой клетки
    # color - цвет, с которым сравнивают клетку
    # kind - номер группы, по которому идет проверка
    #--------------------------
    def _Compare(self, i, j, color, kind, direction):
        if self.MatchMap[direction].has_key((i,j)) or self.MovingTiles.has_key((i,j)):
            return    
        if self.Cells.has_key((i,j)):
            if self._ColorMatch(self.Cells[i,j], color):
                    self.MatchMap[direction][i,j] = kind
                    for (dx, dy) in direction:
                        self._Compare(i+dx, j+dy, color, kind, direction)
                    
        
    def _ColorMatch(self, color1, color2):
        if color1 == color2:# and color1 >= 0:
            return True
        else:
            return False
        
    #--------------------------
    # основной цикл
    #--------------------------
    def _OnExecute(self, que) :
        try:
            #схлопывание
            for cell in self.MovingTiles.keys():
                self.MovingTiles[cell]["timer"] = max(self.MovingTiles[cell]["timer"] - que.delta, 0)
                self.Grid[cell].y = self._CellCoordsLeft(cell)[1] - \
                    int(self.MovingTiles[cell]["ySpeed"]*self.MovingTiles[cell]["timer"]/1000)
                if self.MovingTiles[cell]["timer"] == 0:
                    self.MovingTiles.pop(cell)
                
            #поиск совпадений
            self._GenerateMatchMap()
            if len(self.Chains)>0:
                for chain in self.Chains:
                    for cell in chain:
                        self._RemoveTokenFrom(cell)
                self._BeginCollapse()
            
        except:
            oE.Log(unicode(string.join(apply(traceback.format_exception, sys.exc_info()))))
        return scraft.CommandStateRepeat
        
    def _BeginCollapse(self):
        tmpBasicSpeed = int(1.0*Crd_deltaY*1000/TmpMovingTime)
        for i in range(self.Cols):
            for j in range(self.Rows-1, -1, -1):
                if self.Cells[i,j] != Const_EmptyCell:
                    tmpEmptyUnder = len(filter(lambda y: self.Cells[i,y] == Const_EmptyCell, range(j+1, self.Rows)))
                    if tmpEmptyUnder > 0:
                        self._SwapCells((i,j), (i,j+tmpEmptyUnder))
                        #self.MovingTiles[i,j+tmpEmptyUnder] = { "ySpeed": tmpBasicSpeed*tmpEmptyUnder, "timer": TmpMovingTime }
                        self.MovingTiles[i,j+tmpEmptyUnder] = { "ySpeed": tmpBasicSpeed, "timer": TmpMovingTime*tmpEmptyUnder }
            tmpEmptyTotal = len(filter(lambda y: self.Cells[i,y] == Const_EmptyCell, range(self.Rows)))
            if tmpEmptyTotal > 0:
                for j in range(tmpEmptyTotal):
                    self._PutRandomToken((i,j))
                    #self.MovingTiles[i,j] = { "ySpeed": tmpBasicSpeed*tmpEmptyTotal, "timer": TmpMovingTime }
                    self.MovingTiles[i,j] = { "ySpeed": tmpBasicSpeed, "timer": TmpMovingTime*tmpEmptyTotal }
        for cell in self.MovingTiles.keys():
            self.Grid[cell].y = self._CellCoordsLeft(cell)[1] - \
                int(self.MovingTiles[cell]["ySpeed"]*self.MovingTiles[cell]["timer"]/1000)
        
    #--------------------------
    # проверка использования тулзов;
    # если тулзы не используются, то использовать родительскую функцию
    #--------------------------
    def _OnMouseClick(self, sprite, x, y, button):
        if sprite.cookie == Cmd_Receptor:
            tmpPos = (sprite.GetItem(Indexes["Col"]), sprite.GetItem(Indexes["Row"]))
            if not tmpPos in self.MovingTiles.keys():
                self._RemoveTokenFrom(tmpPos)
                self._BeginCollapse()
        
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
        


oE.logging = True
oE.Init(scraft.DevDisableDrvInfo)
oE.vMode = Video_Mode
oE.background.color = 0x402020
oE.rscpath = unicode(sys.argv[0][0:sys.argv[0].rfind("\\")+1])
oE.SST = File_SST
oE.title = "Match 3 Test"
oE.nativeCursor = True
oE.showFps = False

defs.ReadCuisine()
defs.ReadResourceInfo()

globalvars.Cursor = Cursor()

Board = Storage(8, 8, 200, 100)
Board.InitialFilling()

while True:
    oE.NextEvent()
    if oE.EvtIsESC() or oE.EvtIsQuit() :
        break
    oE.DisplayEx(30) # 30 FPS


