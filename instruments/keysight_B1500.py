# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Semiconductor Device Analyzer
# KEYSIGHT : B1500A
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase
import time
import numpy

__all__ = ['KEYSIGHT_B1500A']


class KEYSIGHT_B1500A(_InstrumentBase):
    def __init__(self,
                 IP='192.168.13.7',
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'TCPIP0::%s::5025::SOCKET' % IP
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEYSIGHT B1500A'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.VI.timeout = 5000

        self.write('RES:FORM:ESC ON')
        self.write('RES:FORM TEXT')

    def OpenWorkspace(self, workspace):
        if self.query('WORK:STAT?') == 'OPEN':
            self.write('WORK:CLOSE')
            while self.VI.query('WORK:STAT?') == 'OPEN':
                time.sleep(0.1)
        self.write(':WORK:OPEN "%s"' % workspace)
        while self.query('WORK:STAT?') == 'CLOS':
            time.sleep(0.1)
        self.query('WORK:STAT?')

    def _RUN(self):
        while 'No error' not in self.query('SYST:ERR?'):
            time.sleep(0.1)
        self.write('RUN')
        done = False
        while not(done):
            if self.query('*OPC?') == '1':
                done = True
            else:
                time.sleep(0.1)

    def _getResult(self, delete=False):
        rawData = self.query('RES:FETCH?')
        if delete:
            self.write('RES:REC:LAT')
        rawList = rawData.split('\\r\\n')
        data = rawList.pop(0)
        while 'AutoAnalysis.Marker.Data.StartCondition' not in data:
            data = rawList.pop(0)
        self.headers = numpy.array(rawList.pop(0).split(','))
        raw_result = numpy.array([numpy.fromstring(line, sep=',')
                                   for line in rawList])
        result = {}
        for i, key in enumerate(self.headers):
            result[key] = raw_result[:, i]
        return result

    def getResultDictionary(self, new=False, delete=False):
        if new:
            self._RUN()
        return self._getResult(delete)
