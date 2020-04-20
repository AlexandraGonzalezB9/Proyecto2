# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 12:56:57 2018

@author: SALASDRAI
"""
import numpy as np
import scipy.signal as signal

class Biosenal(object):
    def __init__(self,data=None):
        if not data==None:
            self.asignarDatos(data)
        else:
            self.__data=np.asarray([])
            self.__canales=0
            self.__puntos=0
    def asignarDatos(self,data):
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        #prevengo errores logicos
        if x_min>=x_max:
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[:,x_min:x_max]
#%%
    #necesito una escala?
#    def escalar_senal(self,x_min,x_max,escala):
#        print("marcador1")
#        if datos=="":
#            print("marcador2")
#            if x_min>=x_max:
#                return None
#            #el slicing no genera copia de los datos sino que devuelve un segmento de los originales, para no modificar el original se debe hacer una copia
#            copia_data=self.data[:,x_min:x_max].copy()
#            x_min2=int(x_min*escala)
#            x_max2=int(x_max*escala)
#            copia_data2=copia_data[:,x_min2:x_max2]
#%%
    def escalar_senal(self,x_min,x_max,escala):
        copia_datos=self.__data[:,x_min:x_max].copy()
        return copia_datos*escala
    
    def calcularWavelet(self, canal):
        
        senal = self.__data[canal, :];
        
        #%%analisis usando wavelet continuo
        import pywt #1.1.1

        #%%
        sampling_period =  1/1000
        Frequency_Band = [4, 30] # Banda de frecuencia a analizar

        # Métodos de obtener las escalas para el Complex Morlet Wavelet  
        # Método 1:
        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1, 250)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 
        
        N = senal.shape[0]
        
        #%%
        # Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
        time_epoch = sampling_period*N

        # Analizar una epoca de un montaje (con las escalas del método 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet

        [coef, freqs] = pywt.cwt(senal, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = (np.abs(coef)) ** 2
        
        return time, freqs, power
    
    def calcular_welch(self,canal,wch):
        fs = 1/1000
        senal = self.__data[canal, :];
        if wch == "No se sobreponen":
            f, Pxx = signal.welch(senal,fs,'hamming', 512, 256, 512, scaling='density')

        elif wch == "Se sobreponen al 50%":
            f, Pxx = signal.welch(senal,fs,'hamming', 512*0.5, 256*0.5, 512*0.5, scaling='density')

        elif wch == "Se sobreponen el doble":
            f, Pxx = signal.welch(senal,fs,'hamming', 1024, 512, 1024, scaling='density')
            
        return f, Pxx

    