# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Data Container based on dictionaries
#
# TODO:
# Make documentation

import numpy
import time

__all__ = ['DataContainer']


class DataContainer(object):
    '''
    Data container
    '''

    def __init__(self, **kwargs):
        self.info = ''
        self.file_id = ''
        self._data = {**kwargs}

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return self._data.__repr__()

    def keys(self):
        return self._data.keys()

    def save(self, file_name):
        '''
        Save a .npy file
        '''
        numpy.savez_compressed(file_name + self.file_id,
                               Info=self.info,
                               DateTime=time.asctime(time.localtime()),
                               **self._data)

    def savetxt(self, file_name, keys, **kwargs):
        '''
        save the data "keys" in a txt table
        TODO make better docummentation
        '''
        savedata = numpy.zeros((len(keys), len(self._data[keys[0]])))
        for i, key in enumerate(keys):
            savedata[i] = self._data[key]
        mykwargs = {}
        mykwargs['header'] = ( str(self.info) +
                             '\n Date: ' + time.asctime(time.localtime()) +
                             '\n' + ', '.join(keys) )
        mykwargs['fmt'] = '%0.6E'
        mykwargs.update(kwargs)
        numpy.savetxt(file_name, savedata.T, **mykwargs)

