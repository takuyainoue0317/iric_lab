
'''
Add comment
'''
import numpy as np
import h5py

class Grid2d:

    def __init__(self, f_cgns):

        with h5py.File(f_cgns, mode='r') as f:
                
            dir_name = 'iRIC/iRICZone/GridCoordinates'
            self.xx = f[dir_name + '/CoordinateX/ data'][()]
            self.yy = f[dir_name + '/CoordinateY/ data'][()]

        self.ni = self.xx.shape[1]
        self.nj = self.xx.shape[0]