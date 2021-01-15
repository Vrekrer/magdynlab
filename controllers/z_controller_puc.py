# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Magneto Impedance Controller for PUC
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['ZControler_PUC']


class ZControler_PUC(object):

    def __init__(self, LockIn_instrument):
        self.LockIn = LockIn_instrument
    
    def setFreq(self, freq):
        return self.LockIn.setOscilatorFreq(freq)
        
    def getFXY(self, n = 5, iniDelay = 0.1, measDelay = 0):
        vsIn = numpy.zeros((n,2))
        time.sleep(iniDelay)
        for i in range(n):
            time.sleep(measDelay)
            vsIn[i] = [self.LockIn.X, self.LockIn.Y]
        vIn = vsIn.mean(axis=0)
        freq = self.LockIn.Freq
        return numpy.array([freq, vIn[0], vIn[1]])
