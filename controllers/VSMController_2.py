import time
import numpy
from ..Instruments import EG_G_7265
#from ..Instruments import SRS_SR830
from ..UserInterfaces.Loggers import NullLogger

class VSMController2(object):

    #Controlador y sensor del VSM
    
    def __init__(self, Logger =  None):
        self.LockIn = EG_G_7265(RemoteOnly = False)
        #self.LockIn = SRS_SR830(GPIB_Address = 22, RemoteOnly = False)
        self.LockIn.InputMode('0')
        self.LockIn.VoltageInputMode('1')
        self.LockIn.FilterSlope('3')
        self.LockIn.setRefPhase(85.0)
        self.confDriver()
        self.confInput()
        self.emu_per_V = 1
        #self.emu_per_V = 3.2867
        #self.emu_per_V = 1
                
        if Logger == None:
            self._logger =  NullLogger()
        else:
            self._logger = Logger
        self.log = self._logger.log
        
        
    def confDriver(self, OscFrec = 200, OscAmp = 0.2):
        self.LockIn.setOscilatorAmp(OscAmp)
        self.LockIn.setOscilatorFreq(OscFrec)
    def confInput(self, Sen = 0.1, TC = 0.1, AcGain = '0'):
        self.LockIn.TC = TC
        self.LockIn.SEN = Sen
        self.LockIn.ConfigureInput(AcGain = AcGain)
        
    def ZeroPhase(self):
        TCtemp = self.LockIn.TC
        self.LockIn.TC = 1
        time.sleep(15)
        ph = 0
        for i in range(10):
            time.sleep(1)
            ph = self.LockIn.Phase + ph
        ph = ph / 10.0
        self.LockIn.setRefPhase(self.LockIn.getRefPhase() + ph)
        self.LockIn.TC = TCtemp
        time.sleep(3)
        
    def getRefPhase(self):
        return self.LockIn.getRefPhase()
        
    def getMagnetization(self, n = 20, iniDelay = 1, measDelay = 0, stat = False, tol = 0.05, maxIts = 50):
        self.log('Measuring Magnetization ... ', EOL = '')
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
                its = its + 1 
                err = (vsIn - vIn)**2
                vsIn = vsIn[err < sigma**2]
                while len(vsIn) < n:
                    time.sleep(measDelay)
                    vsIn = numpy.append(vsIn, self.LockIn.X)
                vIn = vsIn.mean()
                sigma = vsIn.std()
        self.log('Done.', [125,125,125])
        self.log('M = %.3E     | ' % (vIn * self.emu_per_V), [100,100,100], EOL = '')
        self.log('s = %.3E ' % (sigma * self.emu_per_V), [190,190,190])
        return numpy.array([vIn, sigma])* self.emu_per_V
        
    def getAmplitude(self, n = 20, iniDelay = 1, measDelay = 0):
        vsIn = numpy.zeros(n)
        time.sleep(iniDelay)
        for i in range(n):
            time.sleep(measDelay)
            vsIn[i] = self.LockIn.Magnitude
        vIn = vsIn.mean()
        return vIn
