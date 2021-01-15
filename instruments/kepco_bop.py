# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Bipolar Power Supplies
# KEPCO : BOP 20-20M
# KEPCO : BOP 20-20ML
# KEPCO : BOP 50-20MG
# (Should work with other BOP 400W/1000W models)
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['KEPCO_BOP']


class KEPCO_BOP(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=6, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'KEPCO BOP'
        self.VI.write_termination = None
        self.VI.read_termination = self.VI.LF
        self.write('*CLS')
        self.write('*RST')
        self.write('OUTPUT ON')

    def __del__(self):
        self.write('VOLT 0')
        super().__del__()

    def SetRange(self, r):
        '''
        Change operating range for output current or voltage

        Usage :
            SetRange('Full' / '1/4' / 'AUTO')
        '''
        validCodes = ['Full', '1/4', 'AUTO']
        if r in validCodes:
            rangeStr = ['1', '4', 'AUTO'][validCodes == r]
            mode = ['VOLT', 'CURR'][self.query_int('FUNC:MODE?')]
            self.write('%s:RANG:%s' % (mode, rangeStr))
        else:
            self._log('ERR ', 'Range error code')

    def Output(self, out):
        '''
        Enable or disable power supply output

        Usage :
            Output('ON'/'OFF')
        '''
        if out in ['ON', 'OFF']:
            self.write('OUTPUT ' + out)
        else:
            self._log('ERR ', 'Output error code')

    def CurrentMode(self):
        ''' Changes to constant current operation mode '''
        self.write('FUNC:MODE CURR')

    def VoltageMode(self):
        ''' Changes to constant voltage operation mode '''
        self.write('FUNC:MODE VOLT')

    @property
    def OperationMode(self):
        ''' Returns actual operation mode '''
        modes = ['Constant Voltage', 'Constant Current']
        return modes[self.query_int('FUNC:MODE?')]

    def VoltageOut(self, vOut):
        '''
        Sets the Output/Protection Voltage

        Usage :
            VoltageOut(voltage)
        '''
        self.write('VOLT %0.4f' % vOut)

    @property
    def voltage(self):
        '''
        On Voltage mode:
            Sets output voltage or return programed voltage
        On Current mode:
            Sets or return protection voltage
        '''
        return self.query_float('VOLT?')

    @voltage.setter
    def voltage(self, vOut):
        self.VoltageOut(vOut)

    def CurrentOut(self, cOut):
        '''
        Sets the Output/Protection Current

        Usage :
            CurrentOut(current)
        '''
        self.write('CURR %0.4f' % cOut)

    @property
    def current(self):
        '''
        On Voltage mode:
            Sets or return protection current
        On Current mode:
            Sets output current or return programed current
        '''
        return self.query_float('CURR?')

    @current.setter
    def current(self, cOut):
        self.CurrentOut(cOut)

    def BEEP(self):
        '''BEEP'''
        self.write('SYST:BEEP')

    @property
    def MeasuredVoltage(self):
        '''Measured Voltage Value'''
        return self.query_float('MEAS:VOLT?')

    @property
    def MeasuredCurrent(self):
        '''Measured Current Value'''
        return self.query_float('MEAS:CURR?')
