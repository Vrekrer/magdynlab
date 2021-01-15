# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# This class controls the:
# SCPI Arduino controled step motor driver
#
# TODO:
# Make documentation

from .instruments_base import InstrumentBase as _InstrumentBase

__all__ = ['VrekrerStepMotor']


class VrekrerStepMotor(_InstrumentBase):
    def __init__(self, port='0',
                 ResourceName=None, logFile=None):
        if ResourceName is None:
            ResourceName = 'ASRL%s::INSTR' % port
        super().__init__(ResourceName, logFile)
        self._IDN = 'Vrekrer Step Motor'
        self.VI.write_termination = self.VI.LF
        self.VI.read_termination = self.VI.LF

    @property
    def ID(self):
        '''ID'''
        return self.query('*IDN?')

    @property
    def state(self):
        '''Motor state'''
        motor_state = self.VI.query('MCON:STAT?')
        return {'ON':'Energized / Motor locked', 
                'OFF':'Not energized/ Motor released'}[motor_state]

    @property
    def locked(self):
        motor_state = self.VI.query('MCON:STAT?')
        return {'ON':True, 'OFF':False}[motor_state]

    @property
    def released(self):
        return not self.locked

    def Lock(self):
        '''
        Energizes the motor coils thus locks the motor motion.
        '''
        self.VI.write('MCON:STAT ON')

    def Release(self):
        '''
        De-energizes the motor coils thus releases the motion lock.
        '''
        self.VI.write('MCON:STAT OFF')

    @property
    def step_frequency(self):
        '''Step frequency in steps/second'''
        step_half_period = self.query_float('MCON:SHPE?') * 1E-6
        speed = 1/(step_half_period*2)
        return speed

    @step_frequency.setter
    def step_frequency(self, speed):
        step_half_period = int(0.5E6/speed)
        self.write('MCON:SHPE %d' % step_half_period)

    def Move(self, n_steps):
        '''
        Moves the motor by the especified number of steps
        Positive numbers move the step motor clockwise,
        while negative numbers move it anti-clockwise
        '''
        if not self.locked:
            self.Lock()
        self.VI.write('MOVE %d' % n_steps)

    @property
    def is_moving(self):
        move_state = self.VI.query('MOVE:STAT?')
        return {'Moving':True, 'Idle':False}[move_state]

