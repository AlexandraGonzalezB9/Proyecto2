#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 10:37:41 2018

@author: alexander
"""
from Modelo import Biosenal
from interfaz import InterfazGrafico
import sys
from PyQt5.QtWidgets import QApplication
class Principal(object):
    def __init__(self):        
        self.__app=QApplication(sys.argv)
        self.__mi_vista=InterfazGrafico()
        self.__mi_biosenal=Biosenal()
        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)
        self.__mi_vista.asignar_Controlador(self.__mi_controlador)
    def main(self):
        self.__mi_vista.show()
        sys.exit(self.__app.exec_())
    
class Coordinador(object):
    def __init__(self,vista,biosenal):
        self.__mi_vista=vista
        self.__mi_biosenal=biosenal
    def recibirDatosSenal(self,data):
        self.__mi_biosenal.asignarDatos(data)
    def devolverDatosSenal(self,x_min,x_max):
        return self.__mi_biosenal.devolver_segmento(x_min,x_max)
    def escalarSenal(self,x_min,x_max,escala):
        return self.__mi_biosenal.escalar_senal(x_min,x_max,escala)
    def calcularWavelet(self, canal):
        return self.__mi_biosenal.calcularWavelet(canal)
    def calcular_welch(self,canal,wch):
        return self.__mi_biosenal.calcular_welch(canal,wch)
    
    
p=Principal()
p.main()