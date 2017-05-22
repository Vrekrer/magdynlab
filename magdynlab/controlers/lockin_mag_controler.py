# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# LockIn controler for magnetometers
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['LockIn_Mag_Controler']


class LockIn_Mag_Controler(object):
    '''
    LockIn controler for magnetometers
    '''

    def __init__(self, LockIn_instrument):
        self.LockIn = LockIn_instrument
        self.emu_per_V = 1

    def __del__(self):
        pass

    def confDriver(self, OscFrec=200, OscAmp=0.2):
        self.LockIn.setOscilatorAmp(OscAmp)
        self.LockIn.setOscilatorFreq(OscFrec)

    def confInput(self, Sen=0.1, TC=0.1, AcGain='0'):
        self.LockIn.TC = TC
        self.LockIn.SEN = Sen
        self.LockIn.ConfigureInput(AcGain=AcGain)

    def ZeroPhase(self, TC=1.0, t_sleep=10):
        TCtemp = self.LockIn.TC
        self.LockIn.TC = 1
        time.sleep(t_sleep)
        ph = 0
        for i in range(10):
            time.sleep(t_sleep/10)
            ph += self.LockIn.Phase
        ph = ph / 10.0
        self.LockIn.setRefPhase(self.LockIn.getRefPhase() + ph)
        self.LockIn.TC = TCtemp
        time.sleep(t_sleep/4)

    def getRefPhase(self):
        return self.LockIn.getRefPhase()

    def getMagnetization(self,
                         n=20, iniDelay=1, measDelay=0,
                         stat=False, tol=0.05, maxIts=50):
        # TODO self.log('Measuring Magnetization ... ', EOL = '')
        vsIn = numpy.zeros(n)
        time.sleep(iniDelay)
        for i in range(n):
            time.sleep(measDelay)
            vsIn[i] = self.LockIn.X
        vIn = vsIn.mean()
        sigma = vsIn.std()
        maxSigma = numpy.abs(self.LockIn.SEN * tol)

        if stat:
            its = 0
            while (sigma > maxSigma) and (its < maxIts):
                its += 1
                err = (vsIn - vIn)**2
                vsIn = vsIn[err < sigma**2]
                while len(vsIn) < n:
                    time.sleep(measDelay)
                    vsIn = numpy.append(vsIn, self.LockIn.X)
                vIn = vsIn.mean()
                sigma = vsIn.std()
        return numpy.array([vIn, sigma]) * self.emu_per_V

    def getAmplitude(self,
                     n=20, iniDelay=1, measDelay=0):
        vsIn = numpy.zeros(n)
        time.sleep(iniDelay)
        for i in range(n):
            time.sleep(measDelay)
            vsIn[i] = self.LockIn.Magnitude
        vIn = vsIn.mean()
        return vIn
