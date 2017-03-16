#!/usr/bin/env python
#-*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import ast
import numpy as np
from shapely.geometry.polygon import Polygon

def extract_point():
    tree = ET.parse('point.xml')
    root = tree.getroot()
    lista = []
    polys = []
    inList = []
    outList = []
    draw=[]
    inDraw = []
    outDraw = []

    for area in root.iter('poly'):
        for tipo in area:
            lista.append([area.attrib['name'], tipo.attrib['type'], ast.literal_eval(tipo[0].attrib['coords'])])
            draw.append([area.attrib['name'], tipo.attrib['type'], ast.literal_eval(tipo[0].attrib['coords'])])

    for poly in root.findall('poly'):
        polys.append(poly.attrib['name'])

    for i in lista:
        if i[1] == 'in':
            inList.append(i)
        else:
            outList.append(i)

    for i in draw:
        if i[1] == 'in':
            inDraw.append(i)
        else:
            outDraw.append(i)
            
    for i in inList:
        i[2] = Polygon(i[2])
    for i in outList:
        i[2] = Polygon(i[2])

    for i in inDraw:
        i[2] = np.array(i[2])
    for i in outDraw:
        i[2] = np.array(i[2])
    
    return inList, outList, inDraw, outDraw,polys
extract_point()
