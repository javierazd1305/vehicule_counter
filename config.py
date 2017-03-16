import cv2
import numpy as np
import threading
import paho.mqtt.publish as publisher
import json
from read import *


class IterRegistry(type):
    def __iter__(cls):
        return iter(cls.registry)

class Vehicules:
    next_id = 0
    __metaclass__ = IterRegistry
    registry = []
    def __init__(self,area,tipo,x,y):
        self.ident = Vehicules.next_id
        self.x = x
        self.y = y
        self.entrada = area
        self.salida = None
        self.tipo = tipo
        self.registry.append(self)
        Vehicules.next_id += 1
        
    def update(self,x,y):
        self.x = x
        self.y = y

    def __del__(self):
        class_name = self.__class__.__name__

    @classmethod
    def getAll(cls):
        suma = 0
        for i in Vehicules:
            suma +=1
        return suma
    @classmethod
    def members(cls):
        for i in Vehicules:
            print i.x, i.y, i.entrada, i.salida
    @classmethod
    def comparison_state(cls,x,y):
        for i in Vehicules:
            if i.x == x and i.y == y:
                return True
        else:
            return False
    @classmethod
    def comparison_move(cls,radius,x,y):
        for i in Vehicules:
            if ((i.x-x)**2) + ((i.y - y)**2) < (radius ** 2):
                return True
        else:
            return False

    @classmethod
    def update_minimo_1(cls,radius,x,y):
        diff = 0
        minimo = 1000
        nuevo_x = None
        nuevo_y = None
        for i in Vehicules:
            if ((i.x-x)**2) + ((i.y - y)**2) < (radius ** 2):
                diff = ((i.x-x)**2) + ((i.y - y)**2)
                if diff < minimo:
                    minimo = diff
                    nuevo_x = i.x
                    nuevo_y = i.y
        for j in Vehicules:
            if j.x == nuevo_x and j.y == nuevo_y:
                j.update(x,y)      
  

    @classmethod
    def asignar_salida_cercano(cls,radius,salida,x,y):
        #print x,y, Vehicules.members()
        diff = 0
        minimo = 1000000
        count = 0
        count_minimo= 1000
        nuevo_x = None
        nuevo_y = None
        salida_out = ""
        entrada_out = ""
        tipo_out = ""
        if len(Vehicules.registry) > 0:
            for i in Vehicules:
                if ((i.x-x)**2) + ((i.y - y)**2) < (radius ** 2):
                    diff = ((i.x-x)**2) + ((i.y - y)**2)
                    if diff < minimo:
                        minimo = diff
                        nuevo_x = i.x
                        nuevo_y = i.y
                        count_minimo = count
                count +=1
            for j in Vehicules:
                if j.x == nuevo_x and j.y == nuevo_y:
                    j.salida = salida
                    #print j.entrada, j.salida, j.tipo
                    entrada_out = j.entrada
                    salida_out = j.salida
                    tipo_out = j.tipo
                    Vehicules.registry.pop(count_minimo)
                    return entrada_out, salida_out, tipo_out
                
#increment counter
def add_count(lista,entrada,salida,tamano):
    for todo in lista:
        if entrada == todo[0] and salida == todo[1]:
            todo[2][tamano]+=1
            
#create new vehicule          
def crear_nuevo(area,entrada,tam_min,tam_max,cx,cy):
    if area <= tam_min:
        Vehicules(entrada,'moto',cx,cy)
    if area > tam_min and area <= tam_max:
        Vehicules(entrada,'auto',cx,cy)
    if area > tam_max:
        Vehicules(entrada,'camion',cx,cy)

#variable counters
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True)
lista = []
inList, outList, inDraw, outDraw, entradas = extract_point()
salidas = entradas
msgs=[]
for e in entradas:
    for s in salidas:
        lista.append([e,s,{'moto':0,'auto':0,'camion':0}])

#Mqqt 
def send_message():
    threading.Timer(5.0, send_message).start()
    for i in lista:
        data = {
                'id':1,
                'entrada':i[0],
                'salida': i[1],
                'counter': i[2]["moto"]+i[2]["auto"]+i[2]["camion"],
                'moto': i[2]["moto"],
                'auto': i[2]["auto"],
                'camion': i[2]["camion"]
                }
        msgs.append({"topic":"counter","payload":json.dumps(data)})
    publisher.multiple(msgs,hostname="127.0.0.1" , port=1883, keepalive=5)
    for todo in lista:
        todo[2]["auto"] = 0
        todo[2]["moto"] = 0
        todo[2]["camion"] = 0

#mouse callback  
def obtener_punto(event,x,y,flags,param):
    if event ==4:
        print x,y
        #print Vehicules.members()

#draw the areas
def draw(image):
    for i in inDraw:   
        cv2.polylines(image, np.int32([i[2]]), 1,(0,255,0))
    for i in outDraw:
        cv2.polylines(image, np.int32([i[2]]), 1,(0,0,255))

        
