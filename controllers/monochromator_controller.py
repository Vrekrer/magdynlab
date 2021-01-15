# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Monotchromator controller
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['MonochromatorController']


class MonochromatorController(object):
    '''
    Monotchromator controller
    
    to be used with a step motor based harwdare
    '''

    def __init__(self, Motor_Driver):
        self.Driver = Motor_Driver

        self.Step_per_nm = 1250  # Number of steps per nm
        self.Time_per_step = 0.015E-3 # Seconds per steps

        # max and min wave lengths (used for step-motor stops)
        self.MAX_WAVE_LENGTH = 2000;
        self.MIN_WAVE_LENGTH = 0;
        self._current_WL = None;

    def __del__(self):
        self.Driver.Release()

    def setRefPosition(self, wave_length_value):
        self._current_WL = wave_length_value;
        self.Driver.Lock()

    @property
    def wave_length(self):
        '''
        Sets or return the working wave length (in nm)
        '''
        if self._current_WL is None:
            return 'No Reference'
        else:
            return self._current_WL

    @wave_length.setter
    def wave_length(self, wave_length_value):
        if self._current_WL is None:
            print('No reference position')
            return

        if wave_length_value < self.MIN_WAVE_LENGTH:
            wave_length_value = self.MIN_WAVE_LENGTH
        if wave_length_value > self.MAX_WAVE_LENGTH:
            wave_length_value = self.MAX_WAVE_LENGTH

        steps = (wave_length_value - self._current_WL) * self.Step_per_nm
        self.Driver.Move(steps)
        self._current_WL = wave_length_value
        time.sleep(abs(steps) * self.Time_per_step)
