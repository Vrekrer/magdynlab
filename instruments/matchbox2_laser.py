# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls:
# MatchBox2 Lasers
#
# TODO:
# Make documentation


from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['MatchBox2_Laser']


class MatchBox2_Laser(_InstrumentBase):
    def __init__(self, port='4',
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'ASRL%s::INSTR' % port
        super().__init__(ResourceName, logFile, baud_rate=115200)
        self._IDN = 'MatchBox2 Laser'
        self.VI.write_termination = None
        self.VI.read_termination = self.VI.CR + self.VI.LF

    def getInfo(self):
        '''
        Get all the laser info
        '''
        info = '##Info##\n' + self.VI.query('r i')
        info += '\n' + self.VI.read()
        info += '\n' + self.VI.read()
        info += '\n' + 'Operating time: %s' % self.VI.read()
        info += '\n' + 'Switched on times: %s' % self.VI.read()
        return info

    def getSettings(self):
        '''
        Get all the laser settings
        '''
        settings = self.VI.query('r s').split(' ')[1:]
        settings_info = '''##Settings##
        Target temp 1: %0.1f °C
        Target temp 2: %0.1f °C
        Setted DAC value: %s
        Output power: %s mW
        Laser Diode Current: %s mA
        Max Laser Diode Current: %s mA
        %s
        Access level: %s
        Target temp body? %0.1f °C''' % (float(settings[0])/100,
                                         float(settings[1])/100,
                                         settings[3],
                                         settings[4],
                                         settings[2],
                                         settings[5],
                                         settings[6],
                                         settings[7],
                                         float(settings[8])/100)
        return settings_info

    def getReadings(self):
        '''
        Get all the laser readings
        '''
        readings = self.VI.query('r r').split(' ')[1:]
        readings_info = '''##Readings##
        Actual Temp 1: %s °C  (%s of set)
        Actual Temp 2: %s °C  (%s of set)
        Actual Temp Body: %s °C  (%s of set)
        Laser Current: %s
        Laser Voltage: %s
        Laser status: %s
        Other value: %s''' % (readings[0], readings[4],
                              readings[1], readings[5],
                              readings[2], readings[7],
                              readings[3],
                              readings[8],
                              readings[6],
                              readings[9])
        return readings_info

    def setPower(self, value):
        self.VI.query('c 4 %0.2f' % value)
        self.VI.read()

    def turnOn(self):
        self.VI.query('e 1')

    def turnOff(self):
        self.VI.query('e 0')
