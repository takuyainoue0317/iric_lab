'''
Add comment
'''
import numpy as np
import h5py
from cls_geographic2d import Geographic2d

class Flow2d(Geographic2d):
    
    def __init__(self, f_cgns):
        super().__init__(f_cgns)

        #set dir name
        iterator_name = 'iRIC/BaseIterativeData/'
        solusion_name = 'iRIC/iRICZone/'

        #delete past results
        with h5py.File(f_cgns, mode='a') as f:

            # delete calculation result
            for item in f[solusion_name]:
                if 'Solution' in item:
                    sname = solusion_name + item
                    f.__delitem__(sname)
            
            
            #delete iterator directory
            if iterator_name in f:
                f.__delitem__(iterator_name)
            

        #counter default
        self.output_counter = 1

        #time series list
        self.time_list = []

        #dir list
        self.node_dir_list = []
        self.cell_dir_list = []

    def result_output_for_cgns(self, f_cgns, time):
        print('result_output')

        self.time_list.append(time)

        it_dir = 'iRIC/BaseIterativeData/'
        itp_dir = 'iRIC/iRICZone/ZoneIterativeData/'
        node = 'FlowSolution'
        cell = 'FlowCellSolution'
        node_dir = 'iRIC/iRICZone/FlowSolution' + str(self.output_counter)
        cell_dir = 'iRIC/iRICZone/FlowCellSolution' + str(self.output_counter)
        
        self.node_dir_list.append(node_dir)
        self.cell_dir_list.append(cell_dir)

        with h5py.File(f_cgns, mode='a') as f:
            
            #iterator value
            # # delete
            # if it_dir in f:
            #     f.__delitem__(it_dir)

            # # create iterator group
            # grp = f.create_group(it_dir)
            # dset = grp.create_dataset(' data', data=[len(self.time_list)])
            
            # grp = grp.create_group('TimeValues')
            # dset= grp.create_dataset(' data', data=self.time_list)

            # #iterator value
            # # delete
            # if it_dir in f:
            #     f.__delitem__(itp_dir)

            # # create iterator group
            # grp = f.create_group(itp_dir)
            # grp = grp.create_group(node)
            # asciiList = [n.encode('ascii', 'ignore') for n in self.node_dir_list]
            # dset = grp.create_dataset(' data', (len(asciiList),1),'S10', asciiList)

            # grp = grp.create_group(cell)
            # asciiList = [n.encode('ascii', 'ignore') for n in self.node_dir_list]
            # dset = grp.create_dataset(' data', data=self.cell_dir_list, dtype='int')

            #node value
            grp = f.create_group(node_dir)
            #dset= grp.create_dataset('TimeValue', data=time)
            dset= grp.create_dataset('Elevation[m]', data=self.zz)

            #node value
            grp = f.create_group(cell_dir)
            dset= grp.create_dataset('Move-Fix', data=self.fm)


        self.output_counter = self.output_counter + 1

    def setInitialCond(self, cond):
        pass




# root
if __name__ == "__main__":
    pass