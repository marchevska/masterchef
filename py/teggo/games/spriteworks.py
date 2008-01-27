#!/usr/bin/env python
# -*- coding: cp1251 -*-

import scraft
from scraft import engine as oE

# Создает спрайт по словарю параметров
# klass и layer - обязательные параметры
def MakeSprite(newKlass, newLayer, param = {}):
    tmpSpr = oE.NewSprite_(newKlass, newLayer)
    if param.has_key("x") and param.has_key("y"):
        tmpSpr.x = param["x"]
        tmpSpr.y = param["y"]
    elif param.has_key("xy"):
        tmpSpr.x, tmpSpr.y = param["xy"]
    if param.has_key("xSize"):
        tmpSpr.xSize = param["xSize"]
    if param.has_key("ySize"):
        tmpSpr.ySize = param["ySize"]
    if param.has_key("text"):
        tmpSpr.text = param["text"]
    if param.has_key("frno"):
        tmpSpr.frno = param["frno"]
    if param.has_key("hotspot"):
        tmpSpr.hotspot = param["hotspot"]
    if param.has_key("sublayer"):
        tmpSpr.sublayer = param["sublayer"]
    if param.has_key("cfilt-color"):
        tmpSpr.cfilt.color = param["cfilt-color"]
    if param.has_key("cookie"):
        tmpSpr.cookie = param["cookie"]
    if param.has_key("dispatcher"):
        tmpSpr.dispatcher = param["dispatcher"]
    if param.has_key("parent"):
        tmpSpr.parent = param["parent"]
    if param.has_key("transparency"):
        tmpSpr.transparency = param["transparency"]
    if param.has_key("scale"):
        tmpSpr.xScale, tmpSpr.yScale = param["scale"], param["scale"]
    if param.has_key("xyScale"):
        tmpSpr.xScale, tmpSpr.yScale = param["xyScale"][0], param["xyScale"][1]
    if param.has_key("xScale"):
        tmpSpr.xScale = param["xScale"]
    if param.has_key("yScale"):
        tmpSpr.xScale = param["yScale"]
    return tmpSpr
