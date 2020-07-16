import numpy as np
from cls_cond import CalcCond
from cls_flow2d import Flow2d

# main
def main(args):

    # calculation condition constractor
    cond = CalcCond(args[1])

    # flow constractor
    flow = Flow2d(args[1])
    
    # set Initial hydraulic conditions
    flow.setInitialCond(cond)

    #main loop
    for it in range(cond.start_count, cond.end_count):

        #current time
        time = cond.start_time + it * cond.cond['dt']

        # simulation model
        #ier = flow.calc()



        # output time
        if it % cond.out_interval == 0:
            print('time = ' + str(time) + '[sec]')
            #flow.result_output_for_cgns(args[1], time)
            #flow.result_output_for_mplt(time)


    return 0


# root
if __name__ == "__main__":
    import sys
    args = sys.argv
    main(args)