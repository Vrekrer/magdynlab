# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Resistance Controller
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['ResistanceController']


class ResistanceController(object):

#    Controllador de SourceMeter para medidas de resistencia

    def __init__(self, source_meter):
        self.SM = source_meter
        self.SM.sense_mode = '4-Wire'
        self.Mode('Current')
        
    def Mode(self, mode):
        if mode == 'Voltage':
            self.SM.source_function = 'Voltage'
            self.SM.sense_function = 'Current'
            self.SM.source_value = 1E-3
        elif mode == 'Current':
            self.SM.source_function = 'Current'
            self.SM.sense_function = 'Voltage'
            self.SM.source_value = 50E-6
            
            
    def getResistance(self, n = 5, iniDelay = 0.1, measDelay = 0.01):
        vsIn = numpy.zeros(n)
        out = self.SM.output
        self.SM.output = 'ON'

        time.sleep(iniDelay)
        sv = self.SM.source_value
        svs = numpy.linspace(-sv, sv, n)
        
        for i in range(n):
            time.sleep(measDelay)
            self.SM.source_value = svs[i]
            vsIn[i] = self.SM.sense_value
        self.SM.output = out
        X = numpy.polyfit(svs, vsIn, 1)[0]
        if 'VOLT' in self.SM.sense_function:
            return 1/X
        else:
            return X
