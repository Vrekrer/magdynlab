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

__all__ = ['FieldController_SM']


class FieldController_SM(object):
    '''
    Magnetic field controller
    
    to be used with a KEITHLEY 2400 source meter driving coreless coils
    '''

    def __init__(self, SourceMeter_Instruments):
        self.SM = SourceMeter_Instruments

        self.HperOut = 16.952  # Oe por I de la salida (aprox)
        self.MaxHRate = 30.0  # Rate H maximo en Oe/s
        self.InToH = 16.952  # Oe por valor de entrada medidos (Oe/A)

        self.SM.sense_mode = '4-Wires'
        self.SM.output = 'OFF'
        self.SM.source_function = 'Current'
        self.SM.source_value = 0
        self.SM.sense_function = 'Voltage'
        self.SourceCurrentLimit = 2

    def __del__(self):
        pass

    def getField(self, Res='Fast', Unit='Oe'):
        '''
        Returns the measured magnetic field.
        Usage :
            getField()
            getField(Res , Unit)

        Resolution codes:
            'Fast' (Default) : Return the value of 1 measurement.
            'High' : Return the mean of 10 measurements.
        Units:
            'Oe' : Field in Oe (default)
            'A/m' : Field in A/m
        '''
        vIn = self.SM.source_value
        if Unit == 'Oe':
            return self.InToH * vIn
        elif Unit == 'A/m':
            return self.InToH * vIn * 1.0E3 / (4 * numpy.pi)

    def setField(self, Fld, Alg='Fast'):
        self.SM.output = 'ON'
        '''Set magnetic field'''
        # TODO self.log('Setting field : %.1f Oe ... ' % Fld, EOL = '')
        InstTime = 0.01  # Tiempo (en s) aprox en establecer y leer el GPIB

        targetIn = Fld / self.InToH
        actualIn = self.SM.source_value
        vInErr = numpy.abs(targetIn - actualIn)

        dVOut = (targetIn - actualIn)  # valor que debe variar la salida
        # Rampa variando dVolt

        vRate = self.MaxHRate / self.InToH  # Taza de variacion en Vin/s
        vIni = self.SM.source_value

        vFin = vIni + dVOut
        nPoints = 400
        tRamp = vInErr / vRate  # Tiempo que deberia tomar la rampa
        if tRamp - InstTime * nPoints > 0:
            # Delay entre los puntos de la rampa
            dt = (tRamp - InstTime) / nPoints
        else:
            dt = 0
            nPoints = numpy.round(tRamp / InstTime) + 5
        vPoints = numpy.linspace(vIni, vFin, nPoints)
        self.vPoints = vPoints
        for v in vPoints:
            self.SM.source_value = v
            time.sleep(dt)
        # time.sleep(0.5)
        # TODO self.log('Done.', [125,125,125])

    def TurnOff(self):
        # TODO self.log('Turning field off ... ', EOL = '')
        vIni = self.SM.source_value
        vPoints = numpy.linspace(vIni, 0, 100)
        dt = numpy.abs(vIni) * self.HperOut / (self.MaxHRate * 100.0)

        for v in vPoints:
            self.SM.source_value = v
            time.sleep(dt)
        # self.log('Done.', [125,125,125])
        
        self.SM.output = 'OFF'

    def BEEP(self, t_sleep=0.1):
        self.SM.BEEP()
        time.sleep(t_sleep)
