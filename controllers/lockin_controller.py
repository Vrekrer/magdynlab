# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# General LockIn controller
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['LockIn_Controller']


class LockIn_Controller(object):
    '''
    General LockIn controller
    '''

    def __init__(self, LockIn_instrument):
        self.LockIn = LockIn_instrument
        self.emu_per_V = 1

    def __del__(self):
        pass

    def ZeroPhase(self, TC=1.0, t_sleep=10):
        TCtemp = self.LockIn.TC
        self.LockIn.TC = TC
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

    def getAmplitude(self,
                         n=20, iniDelay=1, measDelay=0,
                         stat=False, tol=0.05, maxIts=5):
        # TODO self.log('Measuring ... ', EOL = '')
        vsIn = numpy.zeros(n)
        time.sleep(iniDelay)
        for i in range(n):
            time.sleep(measDelay)
            vsIn[i] = self.LockIn.Magnitude
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
        return numpy.array([vIn, sigma])
