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

__all__ = ['FieldControlerDriven']


class FieldControlerDriven(object):
    '''
    Magnetic field controler

    to be used with a Kepco BOP power source and
    a multimiter measuring a hall probe
    '''

    def __init__(self, Kepco_instrument, Voltmeter_instrument):
        self.Kepco = Kepco_instrument
        self.VoltMeter = Voltmeter_instrument

        self.MaxHRate = 30.0  # Rate H maximo en Oe/s
        self.HperOut = 30.0   # Oe por I de la salida (max)
        self.InToH = 10000    # Oe por valor de entrada medidos (Oe/V)

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

    def getField(self, delay=0.5, Res='Fast', Unit='Oe'):
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
        time.sleep(delay)
        vIn = self.VoltMeter.voltage

        if Unit == 'Oe':
            return self.InToH * vIn
        elif Unit == 'A/m':
            return self.InToH * vIn * 1.0E3 / (4 * numpy.pi)

    def setField(self, Fld, Tol=0.5, FldStep=1.0):
        '''Set magnetic field'''
        # TODO self.log('Setting field : %.1f Oe ... ' % Fld, EOL = '')
        sng = numpy.sign(Fld - self.getField())

        t0 = time.time()
        self.getField(delay=0)
        self.Kepco.current = self.Kepco.current
        LoopTime = time.time() - t0

        while (sng * (Fld - self.getField(delay=0)) > 15):
            self.Kepco.current = self.Kepco.current + sng * 2.0*FldStep/self.HperOut
            time.sleep(numpy.max([FldStep/self.MaxHRate - LoopTime, 0]))

        t0 = time.time()
        self.getField(delay=0.2)
        self.Kepco.current = self.Kepco.current
        LoopTime = time.time() - t0

        while (sng * (Fld - self.getField(delay=0.2)) > Tol):
            self.Kepco.current = self.Kepco.current + sng * FldStep/self.HperOut
            time.sleep(numpy.max([FldStep/self.MaxHRate - LoopTime, 0]))

        # self.log('Done.', [125,125,125])

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
