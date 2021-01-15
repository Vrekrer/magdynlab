# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Magnetic Field controller
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['FieldControllerPUC']


class FieldControllerPUC(object):

#    Controlador de Campo Magnetico

    def __init__(self, E3648A_instrument):
        self.PowerSupply = E3648A_instrument

        self.HperOut = 2.89 #Oe por I de la salida (aprox)
        self.MaxHRate = 20.0 #Rate H maximo en Oe/s
        self.InToH = 2.89 #Oe por valor de entrada medidos (Oe/A)
        self._sign = +1

        self.PowerSupply.output = 2
        self.PowerSupply.range = 'P20V'
        self.PowerSupply.voltage = 0.0
        self.PowerSupply.output = 1

    def __del__(self):
        self.PowerSupply.outStatus = 'OFF'

    @property
    def _polarity(self):
        return self._sign

    @_polarity.setter
    def _polarity(self, value):
        if value >= 0:
            self.PowerSupply.output = 2
            self.PowerSupply.voltage = 0.0
            self.PowerSupply.output = 1
            self._sign = 1
        else:
            self.PowerSupply.output = 2
            self.PowerSupply.voltage = 9.0
            self.PowerSupply.output = 1
            self._sign = -1

    def getField(self, Unit = 'Oe'):
#        Returns the measured magnetic field in Oe.
#        Usage :
#            getField()
#            getField(Res , Unit)
#            
#        Units:
#            'Oe' : Field in Oe
#            'A/m' : Field in A/m
        self.PowerSupply.output = 1
        vIn = self.PowerSupply.current * self._sign
        
        if Unit == 'Oe':
            return self.InToH * vIn
        elif Unit == 'A/m':
            return self.InToH * vIn * 1.0E3 / (4 * numpy.pi) 


    def setField(self, Fld, Alg = 'Fast'):
       
       # Set Magnetic Field
        self.PowerSupply.output = 1
        self.PowerSupply.outStatus = 'ON' 
        InstTime = 0.01 #Tiempo (en s) aprox en establecer y leer el GPIB 

        if numpy.sign(Fld+1E-16) != self._sign :
            self.TurnOff()
            self._polarity = Fld
            time.sleep(0.1)
            self.PowerSupply.outStatus = 'ON'
        Fld = numpy.abs(Fld)
            
        targetIn = Fld / self.InToH     
        actualIn = self.PowerSupply.current
        vInErr = numpy.abs(targetIn - actualIn)


        dVOut = (targetIn - actualIn)  #valor que debe variar la salida
        #Rampa variando dVolt

        vRate = self.MaxHRate / self.InToH #Taza de variacion en Vin/s
        vIni = self.PowerSupply.current

        vFin = vIni + dVOut
        nPoints = 100
        tRamp = vInErr / vRate #Tiempo que deberia tomar la rampa
        if tRamp - InstTime * nPoints > 0:
            dt = (tRamp - InstTime) / nPoints #Delay entre los puntos de la rampa
        else:
            dt = 0
            nPoints = numpy.round(tRamp / InstTime) + 5
        vPoints = numpy.linspace(vIni, vFin, nPoints)
        for v in vPoints:
            self.PowerSupply.current = v
            time.sleep(dt)
        time.sleep(0.5)
    
    def TurnOff(self):
        vIni = self.PowerSupply.current
        vPoints = numpy.linspace(vIni, 0, 50)
        dt = numpy.abs(vIni) * self.HperOut  / (self.MaxHRate * 100.0)

        for v in vPoints:
            self.PowerSupply.current = v
            time.sleep(dt)
        self.PowerSupply.output = 1
        self.PowerSupply.outStatus = 'OFF'

    def BEEP(self):
        self.PowerSupply.BEEP()
        time.sleep(0.05)
 
