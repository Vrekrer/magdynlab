# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Gaussmeter
# LakeShore 475
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['LakeShore_475']


class LakeShore_475(_InstrumentBase):
    def __init__(self,
                 GPIB_Address=12, GPIB_Device=0,
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' % (GPIB_Device, GPIB_Address)
        super().__init__(ResourceName, logFile)
        self._IDN = 'LakeShore 475'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF
        self.write('*CLS')
        self.write('*RST')

    @property
    def field(self):
        '''Field Value'''
        return self.query_float('RDGFIELD?')
