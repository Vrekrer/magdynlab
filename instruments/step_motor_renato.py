# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# Step Motor Arduino Based Hardware build by Renato for
# the PL experiment at LABSEM PUC-RIO
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['StepMotor_Renato']


class StepMotor_Renato(_InstrumentBase):
    def __init__(self, port='3',
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'ASRL%s::INSTR' % port
        super().__init__(ResourceName, logFile)
        self._IDN = 'StepMotor Renato'
        self.VI.write_termination = self.VI.CR + self.VI.LF
        self.VI.read_termination = self.VI.CR + self.VI.LF
        self.locked = False

    def Move(self, n_steps):
        '''
        Moves the motor by the especified number of steps
        Positive numbers move the step motor clockwise,
        while negative numbers move it anti-clockwise
        '''
        if not self.locked:
            self.Lock()

        if n_steps > 0:
            self.VI.write('passo_horario%d' % abs(n_steps))
        elif n_steps < 0:
            self.VI.write('passo_antihorario%d' % abs(n_steps))

    def Lock(self):
        '''
        Energizes the motor coils thus locks the motor motion.
        '''
        self.locked = True
        self.VI.write('lock')

    def Release(self):
        '''
        De-energizes the motor coils thus releases the motion lock.
        '''
        self.VI.query('free')
        self.locked = False
