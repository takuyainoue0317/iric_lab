
'''
Add comment
'''
import numpy as np
import h5py
from cls_grid2d import Grid2d

class Geographic2d(Grid2d):
    
    def __init__(self, f_cgns):
        super().__init__(f_cgns)

        with h5py.File(f_cgns, mode='r') as f:
            
            # node values
            dir_name = 'iRIC/iRICZone/GridConditions'
            zz = f[dir_name + '/Elevation/Value/ data'][()]
            self.zz = zz.reshape([self.nj, self.ni])

            #cell values
            fm = f[dir_name + '/Fix_movable/Value/ data'][()]
            self.fm = fm.reshape([self.nj-1, self.ni-1])
            
            obst = f[dir_name + '/Obstacle/Value/ data'][()]
            self.obst = obst.reshape([self.nj-1, self.ni-1])

            sn = f[dir_name + '/roughness_cell/Value/ data'][()]
            self.sn = sn.reshape([self.nj-1, self.ni-1])

            vege_d = f[dir_name + '/vege_density/Value/ data'][()]
            self.vege_d = vege_d.reshape([self.nj-1, self.ni-1])

            vege_h = f[dir_name + '/vege_height/Value/ data'][()]
            self.vege_h = vege_h.reshape([self.nj-1, self.ni-1])

            mix = f[dir_name + '/mix_cell/Value/ data'][()]
            self.mix = mix.reshape([self.nj-1, self.ni-1])

