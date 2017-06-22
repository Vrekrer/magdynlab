# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Data 3D
#
# TODO:
# Make documentation

import numpy

__all__ = ['Data3D']


class Data3D(object):
    '''
    Data container for Z(x,y) data type.
    where Z is a real or complex number
    Z.shape = ( len(y), len(x))
    
    Each column of the array corresponds to a given x value
    Z[:,nx] = Z(y) values with x = x[nx]
    
    Each row of the array corresponds to a given y value
    Z[ny] = Z(y) values with y = y[ny]
    
    Saved files keeps the same column row structure
    '''

    def __init__(self):
        self.header = None
        self.fmt = 'npy'
        self.reset()

    def reset(self):
        self.x = numpy.atleast_1d(0) * numpy.NaN
        self.y = numpy.atleast_1d(0) * numpy.NaN
        self.dataArray = numpy.atleast_2d(0) * numpy.NaN
        self.Z = self.dataArray
        self._Ny = -1
        self._Nx = -1

    def initialize(self, xs, ys, dtype=float):
        '''
        Sets the dataArray to the shape of the list xs and ys
        and stores the xs and ys lists
        '''
        self.x = numpy.atleast_1d(xs)
        self.y = numpy.atleast_1d(ys)
        self.dataArray = numpy.zeros((len(self.y), len(self.x)), dtype=dtype)
        self.Z = self.dataArray
        self._Ny = -1
        self._Nx = -1

    def addRow(self, DataR):
        self._Ny = self._Ny + 1
        self.dataArray[self._Ny] = DataR

    def addColumn(self, DataC):
        self._Nx = self._Nx + 1
        self.dataArray[:,self._Nx] = DataC

    # TODO implement saves
