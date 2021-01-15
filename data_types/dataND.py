# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Data 3D
#
# TODO:
# Make documentation

import numpy

__all__ = ['DataND']


class DataND(object):
    '''
    Data container for Z(x) data type.
    where Z an array 
    '''

    def __init__(self):
        self.header = None
        self.fmt = 'npy'

    def initialize(self, x, shape, dtype=float):
        '''
        '''
        self.x = numpy.atleast_1d(x)
        self.dataArray = numpy.zeros([len(self.x), *shape], dtype=dtype)
        self._N = -1

    def addData(self, Data, i='Last'):
        if i == 'Last':
            self._N = self._N + 1
            i = self._N
        self.dataArray[i] = Data

    # TODO implement saves
