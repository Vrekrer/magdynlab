# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Data 2D
#
# TODO:
# Make documentation

import numpy

__all__ = ['Data2D']


class Data2D(object):
    '''Data container for tabular data
        By default only two columns are used
        these can be accesed using X and Y properties
    '''

    def __init__(self):
        self.reset()
        self.header = None
        self.fmt = 'txt'
        self.str_fmt = '%.6E'
        self.reset()

    def reset(self, n=2):
        self.dat = numpy.array([numpy.zeros((n)) * numpy.NaN])

    def addPoint(self, *values):
        pt = numpy.array(list(values))
        if not numpy.any(numpy.isfinite(self.dat)):
            self.dat[0] = pt
        else:
            self.dat = numpy.append(self.dat, [pt], axis=0)

    def save(self, fileName):
        if self.header is None:
            numpy.savetxt(fileName, self.dat, fmt=self.str_fmt)
        else:
            numpy.savetxt(fileName, self.dat,
                          fmt=self.str_fmt, header=self.header)
        # TODO implement npy saves

    def load(self, fileName):
        if self.header is None:
            sr = 0
        else:
            sr = self.header.count('\n') + 1
        self.dat = numpy.loadtxt(fileName, skiprows=sr)
        # TODO implement npy loads

    @property
    def X(self):
        return self.dat[:, 0]

    @property
    def Y(self):
        return self.dat[:, 1]
