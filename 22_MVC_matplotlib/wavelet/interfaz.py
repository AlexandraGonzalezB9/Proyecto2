#%%ñibrerias
import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
from numpy import arange, sin, pi
#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import scipy.io as sio
import numpy as np
from Modelo import Biosenal
import matplotlib.pyplot as plt;
from IPython import get_ipython

#from csv import reader as reader_csv

# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)
        
        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)
        
    #este metodo me grafica al senal senoidal que yo veo al principio, mas no senales
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s)
    #hay que crear un metodo para graficar lo que quiera
    def graficar_gatos(self,datos):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        ##self.axes.plot(datos)
        #y lo graficamos
        ##print("datos")
        ##print(datos)
        #voy a graficar en un mismo plano varias senales que no quecden superpuestas cuando uso plot me pone las graficas en un mismo grafico
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c,:]+c*10)
        self.axes.set_xlabel("muestras")
        self.axes.set_ylabel("voltaje (uV)")
        #self.axes.set
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()
        
    def graficar_espectro(self,time, freqs, power):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        self.axes.contourf(time,
                 freqs[(freqs >= 4) & (freqs <= 40)],
                 power[(freqs >= 4) & (freqs <= 40),:],
                 20, # Especificar 20 divisiones en las escalas de color 
                 extend='both')
        #y lo graficamos
        print("datos")
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()
        
        
    def graficar_canal(self,datos,canal):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #y lo graficamos
        #voy a graficar en un mismo plano varias senales que no quecden superpuestas cuando uso plot me pone las graficas en un mismo grafico
        self.axes.plot(datos[canal,:])
        self.axes.set_xlabel("muestras")
        self.axes.set_ylabel("voltaje (uV)")
        #self.axes.set
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()
        
    def graficar_welch(self,f,Pxx):
        self.axes.clear()
        self.axes.plot(f[(f >= 0.000004) & (f <= 0.004)],Pxx[(f >= 0.000004) & (f <= 0.004)])
        self.axes.figure.canvas.draw()

        
#%%
        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    #condtructor
    def __init__(self):
        #siempre va
        super(InterfazGrafico,self).__init__()
        #se carga el diseno
        loadUi ('anadir_grafico.ui',self)
        #se llama la rutina donde configuramos la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite añadir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        #se añade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        #se añade el campo de graficos
        layout.addWidget(self.__sc)
        
        #se organizan las señales 
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_adelante.clicked.connect(self.adelante_senal)
        self.boton_atras.clicked.connect(self.atrasar_senal)
        self.boton_w.clicked.connect(self.w_senal)
        self.boton_disminuir.clicked.connect(self.disminuir_senal) 
        self.tiempoinicial.editingFinished.connect(self.tiempo_inicial)
        self.tiempofinal.editingFinished.connect(self.tiempo_final)
        self.welch_2.currentIndexChanged.connect(self.metodo_welch)

        #hay botones que no deberian estar habilitados si no he cargado la senal
        
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_w.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.canales.setEnabled(False)
        
        #Activar boton de seleccionar canal a visualizar
        self.canales.valueChanged.connect(self.canales_senal)
        self.canales.editingFinished.connect(self.canales_senal)
        
        #cuando cargue la senal debo volver a habilitarlos
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador
    
        
    def adelante_senal(self):
        self.__x_min=self.__x_min+2000
        self.__x_max=self.__x_max+2000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def atrasar_senal(self):
        #que se salga de la rutina si no puede atrazar
        if self.__x_min<2000:
            return
        self.__x_min=self.__x_min-2000
        self.__x_max=self.__x_max-2000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def w_senal(self):
        #canal = int(self.canales.value())
        
        #en realidad solo necesito limites cuando tengo que extraerlos, pero si los 
        #extraigo por fuera mi funcion de grafico puede leer los valores
        tiempo, freq, power = self.__coordinador.calcularWavelet(int(self.canales.value()))
        self.__sc.graficar_espectro(tiempo, freq)
    
    def disminuir_senal(self):
        self.__sc.graficar_gatos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,0.5))
        
   
    def canales_senal(self):
        canal = int(self.canales.value())
        self.__sc.graficar_canal(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max),canal)
    def tiempo_inicial(self):
        self.__x_min=int(self.tiempoinicial.text())
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def tiempo_final(self):
        self.__x_max=int(self.tiempofinal.text())
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
        
    def metodo_welch(self):
        wch = self.welch_2.currentText()
        f, Pxx = self.__coordinador.calcular_welch(int(self.canales.value()),wch)
        self.__sc.graficar_welch(f, Pxx)
        
        
    def cargar_senal(self):
        #se abre el cuadro de dialogo para cargar
        #* son archivos .mat
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Todos los archivos (*);;Archivos mat (*.mat)*")
        if archivo_cargado != "":
            print(archivo_cargado)
            #la senal carga exitosamente entonces habilito los botones
            data = sio.loadmat(archivo_cargado)
            data = data["data"]
            #volver continuos los datos
            sensores,puntos,ensayos=data.shape
            senal_continua=np.reshape(data,(sensores,puntos*ensayos),order="F")
            self.__coordinador.recibirDatosSenal(senal_continua)
            self.__x_min = int(self.tiempoinicial.text())
            self.__x_max = int(self.tiempofinal.text())
          

            #graficar utilizando el controlador
            self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
            ##self.boton_guardar.setEnabled(True)
            self.canales.setEnabled(True)
            self.numero_canales.setEnabled(True)
            self.boton_adelante.setEnabled(True)
            self.boton_atras.setEnabled(True)
            ##self.boton_wavelet.setEnable(True)
            self.boton_w.setEnabled(True)
            self.boton_disminuir.setEnabled(True)
            
            sen = str(sensores)
            self.numero_canales.setText(sen)
            
            
            self.canales.setMaximum(sensores-1)
            self.canales.setMinimum(0)
            
        elif archivo_cargado != "" and archivo_cargado.endswith(".txt"):
            
            data = open (archivo_cargado,"r")
            print(archivo_cargado)
            lines = reader_csv(data);
            row_number = 0;
            header =  '';
            channels = 11;
            header_size = 6;

            data = [];

            for row in lines: 
                if row_number < header_size:
                    header = header + row[0] + '\n';
                    row_number = row_number + 1;
                    print(row);
                else :
                    temp = [];
                    counter = 0;
                    for column in row:
                        if counter == 0:
                            counter = counter + 1;
                            continue
                        elif counter == channels + 1:
                            break;
                        else:
                            temp.append(float(column));
                        counter = counter + 1;
                    data.append(temp);
            biosignal = np.asarray(data, order = 'C');
            biosignal = np.transpose(biosignal);
              #la senal carga exitosamente entonces habilito los botones
            
            
            #volver continuos los datos
            sensores,puntos=biosignal.shape
            senal_continua=np.reshape(biosignal,(sensores,puntos),order="F")
            self.__coordinador.recibirDatosSenal(senal_continua)
            self.__x_min = int(self.tiempoinicial.text())
            self.__x_max = int(self.tiempofinal.text())             
                    
            #graficar utilizando el controlador
            self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
            ##self.boton_guardar.setEnabled(True)
            self.canales.setEnabled(True)
            self.numero_canales.setEnabled(True)
            self.boton_adelante.setEnabled(True)
            self.boton_atras.setEnabled(True)
            ##self.boton_wavelet.setEnable(True)
            self.boton_w.setEnabled(True)
            self.boton_disminuir.setEnabled(True)
            
            sen = str(sensores)
            self.numero_canales.setText(sen)
            
            
            self.canales.setMaximum(sensores-1)
            self.canales.setMinimum(0)
            

#app=QApplication(sys.argv)
#mi_ventana = InterfazGrafico()
#sys.exit(app.exec_()) 
#               
        
        
        
        
        
        
        
