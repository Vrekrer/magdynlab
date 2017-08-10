# coding=utf-8

# Author: Diego Gonzalez Chavez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# magdynlab
# Base class for all instruments
#
# TODO:
# Make documentation

import visa
import datetime
import os
import numpy

__all__ = ['InstrumentBase']


class InstrumentBase(object):
    '''
    Base class for all instrument classes in magdynlab
    '''

    def __init__(self, ResourceName, logFile='MagDynLab_Log'):
        if os.name == 'nt':
            rm = visa.ResourceManager()
        else:
            rm = visa.ResourceManager('@py')
        self.VI = rm.open_resource(ResourceName)
        self._IDN = self.VI.resource_name
        if logFile is None:
            self._logFile = logFile
        else:
            if not os.path.isfile(logFile):
                with open(logFile, 'w') as log:
                    log.write('MagDynLab Instruments LogFile\n')
            self._logFile = os.path.abspath(logFile)
        self._logWrite('OPEN_')

    def __del__(self):
        self._logWrite('CLOSE')
        self.VI.close()

    def __str__(self):
        return "%s : %s" % ('magdynlab.instrument', self._IDN)

    def _logWrite(self, action, value=''):
        if self._logFile is not None:
            with open(self._logFile, 'a') as log:
                timestamp = datetime.datetime.utcnow()
                log.write('%s %s %s : %s \n' %
                          (timestamp, self._IDN, action, repr(value)))
    _log = _logWrite

    def write(self, command):
        self._logWrite('write', command)
        self.VI.write(command)

    def read(self):
        self._logWrite('read ')
        returnR = self.VI.read()
        self._logWrite('resp ', returnR)
        return returnR

    def query(self, command):
        self._logWrite('query', command)
        returnQ = self.VI.query(command)
        self._logWrite('resp ', returnQ)
        return returnQ

    def query_type(self, command, type_caster):
        returnQ = self.query(command)
        return type_caster(returnQ)

    def query_int(self, command):
        return self.query_type(command, int)

    def query_float(self, command):
        return self.query_type(command, float)

    def query_values(self, command):
        read_term = self.VI.read_termination
        self.VI.read_termination = None
        data = numpy.array(self.VI.query_binary_values(command, datatype='d'))
        self.VI.read_termination = read_term
        return data


class InstrumentChild(object):
    '''
    Base class for instrument subclasses in magdynlab
    '''

    def __init__(self, parent):
        self.parent = parent
        self._logWrite = parent._logWrite
        self._log = parent._log
        self.write = parent.write
        self.query = parent.query
        self.query_type = parent.query_type
        self.query_int = parent.query_int
        self.query_float = parent.query_float
        self.query_values = parent.query_values
        self._IDN = parent._IDN + ' %s' % self.__class__.__name__

    def __del__(self):
        del self.parent
        del self._logWrite
        del self._log
        del self.write
        del self.query
        del self.query_type
        del self.query_int
        del self.query_float
        del self.query_values

    def __str__(self):
        return "%s : %s" % ('magdynlab.instrument', self._IDN)
