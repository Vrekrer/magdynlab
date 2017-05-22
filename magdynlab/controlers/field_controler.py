# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Magnetic Field controler
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['FieldControler']


class FieldControler(object):
    '''
    Magnetic field controler
    
    to be used with a Kepco BOP power source driving coreless coils
    '''

    def __init__(self, Kepco_instrument):
        self.Kepco = Kepco_instrument

        self.HperOut = 16.952  # Oe por I de la salida (aprox)
        self.MaxHRate = 30.0  # Rate H maximo en Oe/s
        self.InToH = 16.952  # Oe por valor de entrada medidos (Oe/A)

        self.Kepco.CurrentMode()
        self.Kepco.voltage = 20.0
        self.Kepco.SetRange('Full')

    def __del__(self):
        pass

    def ResetKepco(self):
        self.Kepco.current = 0
        self.Kepco.CurrentMode()
        self.Kepco.voltage = 20.0
        self.Kepco.SetRange('Full')

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
        vIn = self.Kepco.current
        if Unit == 'Oe':
            return self.InToH * vIn
        elif Unit == 'A/m':
            return self.InToH * vIn * 1.0E3 / (4 * numpy.pi)

    def setField(self, Fld, Alg='Fast'):
        '''Set magnetic field'''
        # TODO self.log('Setting field : %.1f Oe ... ' % Fld, EOL = '')
        InstTime = 0.01  # Tiempo (en s) aprox en establecer y leer el GPIB

        targetIn = Fld / self.InToH
        actualIn = self.Kepco.current
        vInErr = numpy.abs(targetIn - actualIn)

        dVOut = (targetIn - actualIn)  # valor que debe variar la salida
        # Rampa variando dVolt

        vRate = self.MaxHRate / self.InToH  # Taza de variacion en Vin/s
        vIni = self.Kepco.current

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
            self.Kepco.current = v
            time.sleep(dt)
        # time.sleep(0.5)
        # TODO self.log('Done.', [125,125,125])

    def TurnOff(self):
        # TODO self.log('Turning field off ... ', EOL = '')
        vIni = self.Kepco.current
        vPoints = numpy.linspace(vIni, 0, 100)
        dt = numpy.abs(vIni) * self.HperOut / (self.MaxHRate * 100.0)

        for v in vPoints:
            self.Kepco.current = v
            time.sleep(dt)
        # self.log('Done.', [125,125,125])

    def BEEP(self, t_sleep=0.1):
        self.Kepco.BEEP()
        time.sleep(t_sleep)
