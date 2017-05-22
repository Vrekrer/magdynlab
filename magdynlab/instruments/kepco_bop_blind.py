# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Special class for controling BOP with no query commands
# Useful for not fully functional instruments
#
# TODO:
# Make documentation

from .kepco_bop import KEPCO_BOP as _base_KEPCO

__all__ = ['KEPCO_BOP_blind']


class KEPCO_BOP_blind(_base_KEPCO):
    def __init__(self,
                 GPIB_Address=6, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        super().__init__(GPIB_Address, GPIB_Device, ResourceName, logFile)
        self._IDN = 'KEPCO BOP BLIND'
        self._voltage = 0
        self._current = 0
        self._mode = 0

    def SetRange(self, r):
        '''Do Nothing'''
        pass

    def CurrentMode(self):
        ''' Changes to constant current operation mode '''
        self._mode = 1
        self.write('FUNC:MODE CURR')

    def VoltageMode(self):
        ''' Changes to constant voltage operation mode '''
        self._mode = 0
        self.write('FUNC:MODE VOLT')

    @property
    def OperationMode(self):
        ''' Returns actual operation mode '''
        modes = ['Constant Voltage', 'Constant Current']
        return modes[self._mode]

    def VoltageOut(self, vOut):
        '''
        Sets the Output/Protection Voltage

        Usage :
            VoltageOut(voltage)
        '''
        self._voltage = vOut
        self.write('VOLT %0.4f' % vOut)

    @property
    def voltage(self):
        '''
        On Voltage mode:
            Sets output voltage or return programed voltage
        On Current mode:
            Sets or return protection voltage
        '''
        return self._voltage

    @voltage.setter
    def voltage(self, vOut):
        self.VoltageOut(vOut)

    def CurrentOut(self, cOut):
        '''
        Sets the Output/Protection Current

        Usage :
            CurrentOut(current)
        '''
        self._current = cOut
        self.write('CURR %0.4f' % cOut)

    @property
    def current(self):
        '''
        On Voltage mode:
            Sets or return protection current
        On Current mode:
            Sets output current or return programed current
        '''
        return self._current

    @current.setter
    def current(self, cOut):
        self.CurrentOut(cOut)

    @property
    def MeasuredVoltage(self):
        '''Fake Measured Voltage Value'''
        return self._voltage

    @property
    def MeasuredCurrent(self):
        '''Fake Measured Current Value'''
        return self._current
