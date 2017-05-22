# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Signal Generator
# Stanford Research Systems : DS335
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['SRS_DS335']


class SRS_DS335(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=15, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'SRS_SR830'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self._unit = 'VP'  # Volts peak to peak

    @property
    def amplitude(self):
        '''
        Sets or return the output voltage amplitude.

        Use the "unit" property to set the units used (Vpp or Vrms).
        '''
        amp_str = self.querry('AMPL?')
        self._unit = amp_str[-2:]
        return float(amp_str[:4])

    @amplitude.setter
    def amplitude(self, vAmp):
        self.write('AMPL %0.2f%s' % (vAmp, self._unit))

    @property
    def unit(self):
        '''
        Sets or return the voltage units (Vpp or Vrms).

        Changing the unit corrects the output voltage value
        to keep it at the same phisical value.
        '''
        self.amplitude  # read unit from hardware
        return {'VP': 'Vpp', 'VR': 'Vrms'}[self._unit]

    @unit.setter
    def unit(self, vUnit):
        newUnit = {'Vpp': 'VP', 'Vrms': 'VR'}.get(vUnit, 'VP')
        amp = self.amplitude  # read amplitude and unit from hardware
        oldUnit = self._unit
        self._unit = newUnit
        unitChange_str = '%sto%s' % (oldUnit, newUnit)
        unitChange_factors = {'VPtoVR': 0.5**0.5, 'VRtoVP': 2**0.5}
        if unitChange_str in unitChange_factors:
            self.amplitude = amp * unitChange_factors[unitChange_str]

    @property
    def frequency(self):
        '''Sets or return the output frequency in Hz'''
        return self.query_float('FREQ?')

    @frequency.setter
    def frequency(self, vFreq):
        self.write('FREQ %0.6f' % vFreq)

    @property
    def offset(self):
        '''Sets or return the output offset in volts'''
        return self.query_float('OFFS?')

    @offset.setter
    def offset(self, vOffset):
        self.write('OFFS %0.2f' % vOffset)

    @property
    def loadImpedance(self):
        '''
        Sets or return the output source impedance mode
        "HighZ" or "50 Ohm"
        '''
        val = self.query('TERM?')
        return {'1': 'HighZ', '0': '50 Ohm'}[val]

    @loadImpedance.setter
    def loadImpedance(self, vTerm):
        term_str = {'HighZ': '1', '50 Ohm': '0'}.get(vTerm, '1')
        self.write('TERM %s' % term_str)

    @property
    def syncOutput(self):
        '''
        Return the sync output state or sets it to "ON" or "OFF"
        '''
        val = self.query('SYNC?')
        return {'1': 'ON', '0': 'OFF'}[val]

    @syncOutput.setter
    def syncOutput(self, vSync):
        sync_str = {'ON': '1', 'OFF': '0'}.get(vSync, '1')
        self.write('SYNC %s' % sync_str)

    @property
    def function(self):
        val = self.query('FUNC?')
        return {'0': 'Sine', '1': 'Square', '2': 'Triange',
                '3': 'Ramp', '4': 'Noise'}[val]

    @function.setter
    def function(self, vFunct):
        '''
        Sets or return the output function
        "Sine", "Square", "Triange", "Ramp" or "Noise"
        '''
        funct_str = {'Sine': '0', 'Square': '1', 'Triange': '2',
                     'Ramp': '3', 'Noise': '4'}.get(vFunct, '0')
        self.write('FUNC %s' % funct_str)

    def Display(self, show_funct='Amp'):
        '''
        Changes de hardware dysplay to show:
        "Amplitude" ('Amp'), "Frequency" (Freq) or "Offset" ('Offs')
        '''
        dps_str = {'Amplitude': '2', 'Frequency': '1', 'Offset': '3',
                   'Amp': '2', 'Freq': '1', 'Offs': '3'}.get(show_funct, '2')
        self.write('KEYS %s' % dps_str)
