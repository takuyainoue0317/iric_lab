'''
comment
'''
import h5py

class CalcCond:
    
    def __init__(self, f_cgns):

        #make calc condition dict from cgns file
        with h5py.File(f_cgns, mode='r') as f:
            #set items
            items = f['iRIC/CalculationConditions/'].items()
            
            cond_list = []
            for item in items:
                k = item[0]; v = item[1]

                if len(v) == 1:
                    val = v['Value'][' data'][(0)]
                    #print(v['Value'][' data'][(0)])
                    cond_list.append((k, val))

                elif len(v) == 0:
                    pass

                else:
                    for x in v:
                        val = v[x][' data'][()]
                        cond_list.append((x, val))

        # self.cond  is dictionary
        self.cond = dict(cond_list)

        # time min, max from function
        self.start_time = min(self.cond['time'])
        self.end_time = max(self.cond['time'])
        self.start_count = 0
        self.end_count = int(round(max(self.cond['time']) / self.cond['dt']) + 1)
        self.out_interval = int(self.cond['tuk'] / self.cond['dt'])

            
# root
if __name__ == "__main__":
    pass
