import numpy as np
import PySimpleGUI as psg
import pytz, random, os
from datetime import datetime
import matplotlib.pyplot as plt

def CombGen(q1_midpoint = 30, q2_midpoint = 30, q1_inc = 2, q2_inc = 2, q1_offset_midpoint = 30, q2_offset_midpoint = 30, q1_offset_increment = 2, q2_offset_increment = 2, JND_level = 5, Offset_level = 5, mode = "polar", singleLineBlock3 = True):
    """Generate Target points combination file for multi-channel skin stretch interference pilot study
        Block 1 = q2 effect on the JND of q1 + Perception of q1
        Block 2 = q1 effect on the JND of q2 + Perception of q2
        Block 3 = difference between q1q2 on the perception of q1q2

    Args:
        q1_midpoint (int, optional): Standard Stimulus of JND in q1 (in deg). Defaults to 30.\n
        q2_midpoint (int, optional): Standard Stimulus of JND in q2 (in deg). Defaults to 30.\n
        q1_inc (int, optional): Increment in q1 for JND calculation (in deg). Defaults to 2.\n
        q2_inc (int, optional): Increment in q2 for JND calculation (in deg). Defaults to 2.\n
        q1_offset_midpoint (int, optional): The midpoint on q1 when q1 is used as an interfering factor (in deg). Defaults to 30.\n
        q2_offset_midpoint (int, optional): The midpoint on q2 when q2 is used as an interfering factor (in deg). Defaults to 30.\n
        q1_offset_increment (int, optional): The increment of q1 when q1 is used as an interfering factor (in deg) . Defaults to 2.\n
        q2_offset_increment (int, optional): The increment of q2 when q2 is used as an interfering factor (in deg). Defaults to 2.\n
        JND_level (int, optional): Number of levels in JND (The number of points that used to generate a JND). Defaults to 5.\n
        Offset_level (int, optional): The number of points that used to observe the interfering factors effect on the JND. Defaults to 5.\n
        mode (String, optional): Mode of generating the block 3 either in grid interpretation or polar interpretation. Defaults to "grid".\n
        singleLineBlock3 (bool, optional): Generate block 3 with single line or with offsets\n
        
    Returns:
        out: Combination of target points in [Block1, Block2, Block 3]
    """
    modeIn = ["grid", "polar"]
    if mode not in modeIn:
        psg.Popup("Mode input is not included!")
        out = None
    
    else:
    ###BLOCK 1 GENERATION
        b1_q1 = linGen(q1_midpoint, q1_inc, level = JND_level)                  #Block 1 q1 axis (measure JND)
        b1_q2 = linGen(q2_offset_midpoint, q2_offset_increment, Offset_level)   #Block 1 q2 axis (interfering factor)
        block1 = []
        
        #Create all the combinations requried e.g. [[[q1_1, q2_1, q1_mid, q2_1], [q1_2, q2_1, q1_mid, q2_1]...], [[q1_1, q2_2, q1_mid, q2_2], [q1_2, q2_2, q1_mid, q2_2]...]]
        for offset in b1_q2:
            tmp = []
            for condition in b1_q1:
                tmp.append([condition, offset, q1_midpoint, offset])
            block1.append(tmp)
        
        del b1_q1, b1_q2, offset, tmp, condition
        ###End of Block 1 combination generation
        
        ###BLOCK 2 GENERATION
        b2_q1 = linGen(q1_offset_midpoint, q1_offset_increment, Offset_level)   #Block 2 q1 axis (interfering factor)
        b2_q2 = linGen(q2_midpoint, q2_inc, JND_level)                          #Block 2 q2 axis (measure JND)
        block2 = []
        #Create all the combinations requried e.g. [[[q1_1, q2_1, q1_1, q2_mid], [q1_1, q2_2, q1_1, q2_mid]...], [[q1_2, q2_1, q1_2, q2_mid], [q1_2, q2_2, q1_2, q2_mid]...]]
        for offset in b2_q1:
            tmp = []
            for condition in b2_q2:
                tmp.append([offset, condition, offset, q2_midpoint])
            block2.append(tmp)
        
        del b2_q1, b2_q2, offset, condition, tmp 
        ###End of BLock 2 combination generation
        
        ###BLOCK 3 GENERATION
        block3 = [] #Have some problem with the linGen input of +-4
        #Calculate midpoint for grid and polar interpretation
        if mode == "grid":
            pass
        elif mode == "polar":
            q1_midpoint = round(q1_midpoint*np.cos(0.25*np.pi))
            q2_midpoint = round(q2_midpoint*np.sin(0.25*np.pi))
            q1_inc = q1_inc*np.cos(0.25*np.pi)
            q2_inc = q2_inc*np.sin(0.25*np.pi)
        
        if not singleLineBlock3:
            if Offset_level % 2 == 0:
                    b3_q1 = linGen((q1_midpoint + Offset_level/2*q1_offset_increment/2), q1_inc, JND_level)
                    b3_q2 = linGen((q2_midpoint - Offset_level/2*q2_offset_increment/2), q2_inc, JND_level)
                    combination = np.column_stack((b3_q1, b3_q2))
                    for i in range(0, Offset_level):
                        tmp = []
                        for q1q2 in combination:
                            tmp.append([round(q1q2[0]-i*q1_offset_increment/2), round(q1q2[1]+i*q2_offset_increment/2), round((q1_midpoint + Offset_level/2*q1_offset_increment/2)-i*q1_offset_increment/2), round((q2_midpoint - Offset_level/2*q2_offset_increment/2)+i*q2_offset_increment/2)])
                        block3.append(tmp)
                    
            else:
                b3_q1 = linGen((q1_midpoint + (Offset_level-1)/2*q1_offset_increment/2), q1_inc, JND_level)
                b3_q2 = linGen((q2_midpoint - (Offset_level-1)/2*q2_offset_increment/2), q2_inc, JND_level)
                combination = np.column_stack((b3_q1, b3_q2))
                for i in range(0, Offset_level):
                    tmp = []
                    for q1q2 in combination:
                        tmp.append([round(q1q2[0]-i*q1_offset_increment/2), round(q1q2[1]+i*q2_offset_increment/2), round((q1_midpoint + (Offset_level-1)/2*q1_offset_increment/2)-i*q1_offset_increment/2), round((q2_midpoint - (Offset_level-1)/2*q2_offset_increment/2)+i*q2_offset_increment/2)])
                    block3.append(tmp)
        else:
            b3_q1 = linGen(midpoint=q1_midpoint, inc = q1_inc, level = JND_level)
            b3_q2 = linGen(midpoint=q2_midpoint, inc = q2_inc, level = JND_level)
            combination = np.column_stack((b3_q1, b3_q2))
            tmp = []
            i = 0
            for q1q2 in combination:
                tmp.append([round(q1q2[0]), round(q1q2[1]), round(q1_midpoint), round(q2_midpoint)])
            block3.append(tmp)
        
        
        del b3_q1, b3_q2, i, tmp, combination, q1q2
        ###End of Block 3 Generation
        
        out = [block1, block2, block3]
    return out
    
def CombPlot(comb = None):
    """Plot the target point combinations

    Args:
        comb (list, optional): Target Point combinations. Defaults to None.

    Returns:
        _NoneType_: None
    """
    comb = getList(comb=comb)
    nd_comb = np.array(comb)
    for block in nd_comb:
        for offset in block:
            plt.plot(offset[:,0], offset[:,1])
            print(offset[:,0], offset[:,1])
    plt.axis('equal')
    plt.grid()
    plt.show()
    
    return None
    
def linGen(midpoint, inc, level, bEnd = True):
    """Function to Generate a numpy linspace

    Args:
        midpoint (_type_): midpoint of the linspace
        inc (_type_): increment of the linspace
        level (_type_): number of levels in the linspace
        bEnd (bool, optional): Boo for including the endpoint. Defaults to True.

    Returns:
        _ndarray_: return a numpy linspace object
    """
    if (level % 2) != 0:
       start_pt = midpoint - ((level-1)/2)*inc
       stop_pt = midpoint + ((level-1)/2)*inc
    else:
        start_pt = midpoint - ((level)/2)*inc
        stop_pt = midpoint + ((level)/2)*inc
    
    return np.linspace(start=start_pt, stop = stop_pt, num = level, endpoint = bEnd)
        
def TargetRep(comb = None, rep = 10):
    """Replicate the target points combination in default of 10 times

    Args:
        comb (list, optional): Target point list in a nested structure of (blocks, offsets, conditions). Defaults to None.
        rep (int, optional): Number of replications. Defaults to 10.

    Returns:
        _list_: The list data that got replicated according to the rep input
    """
    
    comb = getList(comb)
    
    tmp_comb = []
    for block in comb:
        tmp_block = []
        for offset in block:
            tmp_offset = []
            for cond in offset:
                for i in range(10):
                    tmp_offset.append(cond)
            tmp_block.append(tmp_offset)
        tmp_comb.append(tmp_block)
    
    return tmp_comb

def TargetSplitTrial(comb = None):
    """Split the target points [a1_1, a2_1, a1_2, a2_2] into [[a1_1, a2_1], [a1_2, a2_2]] format

    Args:
        comb (list, optional): Target point nested list (blocks, offset, condition). Defaults to None.

    Returns:
        _list_: Splitted target points
    """
    comb = getList(comb)
    
    tmp_comb = []
    for block in comb:
        tmp_block = []
        for offset in block:
            tmp_offset = []
            for cond in offset:
                tmp_offset.append([[cond[0], cond[1]], [cond[2], cond[3]]])
            tmp_block.append(tmp_offset)
        tmp_comb.append(tmp_block)
    
    return tmp_comb

def TargetRepSplit(comb = None, rep = 10):
    """Perform TargetPoints Combination Replication and TargetPoints trial Splitting in sequence

    Args:
        comb (list, optional): Target point list in a nested structure of (blocks, offsets, conditions). Defaults to None.
        rep (int, optional): Number of replications. Defaults to 10.

    Returns:
        list: Target Point list in replicated and trial splitted manner
    """
    return TargetSplitTrial(TargetRep(comb=comb, rep=rep))

def getList(comb):
    """Use a popup to select the npy file and format into list object if comb is None\n
        Only using for functions within CombTargetGen module

    Args:
        comb (List or None): 

    Returns:
        _list_: numpy.load npy file and format into list object
    """
    if comb is None:
        fname = psg.popup_get_file("Choose the file")
        comb = np.load(fname).tolist()
    return comb
    
def TargetRand(comb = None, seed = None):
    """Randomizing the Target Points in the Conditions level (Block, Offset, Condition, Trial)\n
        Fixed seed for consistent random order for all offset level\n
        None seed for inconsistent random order for all offset level

    Args:
        comb (list, optional): Target Points list. Defaults to None.
        seed (_type_, optional): Randomization seed. Defaults to None.

    Returns:
        _list_: The Randomized Target Points
    """
    comb = getList(comb)
    nd_comb = np.array(comb) #nd_comb.shape  = (block, offset, conditions, trial, axes) = (3,5,50,2,2)
    
    if nd_comb.shape[2] % 2 == 0: #Even number of the conditions 
        ones = np.ones(shape = int(nd_comb.shape[2]/2), dtype = int)
        zeros = np.zeros(shape = int(nd_comb.shape[2]/2), dtype = int)
    else: #odd number of the conditions (Has one more zeros than ones)
        ones = np.ones(shape = int(round(nd_comb.shape[2]/2)), dtype = int)
        zeros = np.zeros(shape = int((round(nd_comb.shape[2]/2) + 1)), dtype = int) 
    
    nd_order = np.concatenate((ones, zeros), axis = None)
    order = nd_order.tolist()
    
    if seed is not None:
        random.Random(seed).shuffle(order)
    
    # print(order)
    # print(type(order))
    
    ### WARNING: This random sequence is currently only doing the first lopp
    for block in comb:
        for offset in block:
            if seed is not None:
                random.shuffle(order)
                order = list(order)
            for i, condition in enumerate(offset):
                if order[i] == 1: #Swapping condition[0] and condition[1]
                    tmp = condition[0]
                    condition[0] = condition[1]
                    condition[1] = tmp
                else:
                    pass
                    
    return comb

def Comb2TargetPoints(comb = None, rep = 10, seed = None):
    """ Turn Target Points Combination into Target Points with Replication, Trial Split and Randomization of the conditions within each Offset level

    Args:
        comb (list, optional): Target Points Combinations. Defaults to None.
        rep (int, optional): Number of replications. Defaults to 10.
        seed (_type_, optional): Randomization seed (Input integer for consistent randomized order for all offset level, None for inconsistent randomized order for all offset level). Defaults to None.

    Returns:
        _list_: The Generated Target Points
    """
    comb = getList(comb=comb)
    TargetPoints = TargetRand(TargetRepSplit(comb), seed = seed)
    return TargetPoints

def TargetPointsRand(target = None, seed = None) -> None:
    
    if target is None:
        fname = psg.popup_get_file("Choose the target file")
        target = np.load(fname)
    
    tmp_target = []
    if seed is not None:
        random.seed(seed)
    for block in target:
        tmp_block = []
        for offset in block:
            ls_offset = offset.tolist()
            random.shuffle(ls_offset)
            tmp_block.append(list(ls_offset))
        tmp_target.append(tmp_block)
    
    folder = psg.popup_get_folder("Pick a location to save the target file")
    fname = psg.popup_get_text("Enter the filename for the target")
    fname = f"{folder}/{fname}"
    np.save(fname, tmp_target)

def Block3CombGen(mode, q1_midpoint = 30, q2_midpoint = 30, q1_inc = 2, q2_inc = 2, JND_level = 7, offset_level = 5, angle_mid = 45, angle_inc = 5):
    """Generate combinations points (5 lines) for Block 3

    Args:
        mode (string): 'grid' or 'polar' for understanding coordination, 'axis' for verticle, horizontal and diagonal lines.
        q1_midpoint (int, optional): primary standard stretch angle. Defaults to 30.
        q2_midpoint (int, optional): secondary standard stretch angle. Defaults to 30.
        q1_inc (int, optional): primary stretch increment. Defaults to 2.
        q2_inc (int, optional): secondary stretch increment. Defaults to 2.
        JND_level (int, optional): Number of conditions for testing the JND. Defaults to 7.
        offset_level (int, optional): Number of lines for testing. Defaults to 5.
        angle_mid (int, optional): (For polar mode) middle line's angle in polar coordinate. Defaults to 45.
        angle_inc (int, optional): (For polar mode) increments of lines' angle. Defaults to 5.

    Returns:
        b3_comb (ndarray): default (5,7,4) shaped -> 5 lines, 7 conditions, 4 points [q1, q2, q1_standard, q2_standard]
    """
    q1_range = linGen(q1_midpoint, q1_inc, JND_level, True)
    q2_range = linGen(q2_midpoint, q2_inc, JND_level, True)
    mode_arr = ['grid', 'polar', 'axis']
    if mode not in mode_arr:
        print("mode input out off arr\n")
        print(f"mode: {mode_arr}")
        exit()
    
    else:
        b3_comb = []
        if mode == 'grid':
            offset_i = linGen(0, q1_inc, offset_level, True)
            for i in offset_i:
                tmp_comb = []
                tmp_q1 = [q1+i for q1 in q1_range]
                tmp_q2 = [q2-i for q2 in q2_range]
                for j in range(JND_level):
                    tmp_comb.append([tmp_q1[j], tmp_q2[j], q1_midpoint+i, q2_midpoint-i])
                b3_comb.append(tmp_comb)
        
        if mode == 'polar':
           angle_range = linGen(angle_mid, angle_inc, offset_level, True)
           for angle in angle_range:
                tmp_comb = []
                tmp_q1 = [q1*np.cos(np.deg2rad(angle)) for q1 in q1_range]
                tmp_q2 = [q2*np.sin(np.deg2rad(angle)) for q2 in q2_range]
                for j in range(JND_level):
                    tmp_comb.append([tmp_q1[j], tmp_q2[j], q1_midpoint*np.cos(np.deg2rad(angle)), q2_midpoint*np.sin(np.deg2rad(angle))])
                b3_comb.append(tmp_comb)
        
        if mode == 'axis':
            dia_line = []
            ver_line = []
            hor_line = []
            for j in range(JND_level):
                dia_line.append([q1_range[j], q2_range[j], q1_midpoint, q2_midpoint])
                hor_line.append([q1_range[j], q2_midpoint, q1_midpoint, q2_midpoint])
                ver_line.append([q1_midpoint, q2_range[j], q1_midpoint, q2_midpoint])
            b3_comb = [dia_line, hor_line, ver_line]
    return np.array(b3_comb)
                
def Block3CombRep(b3_comb, rep = 10, b_save = True):
    """Repeat and Suffle the combination of block 3 into a Target Point Sets

    Args:
        b3_comb (ndarray): block 3 combination generated by Block3CombGen
        rep (int, optional): Number of repetition for each combination point. Defaults to 10.
    """
    b3_comb = b3_comb.tolist()
    # b3_comb_polar = b3_comb_polar.tolist()
    b3_rep = []
    # b3_rep_polar = []
    for line in b3_comb:
        tmp_block = []
        for i in range(rep):
            random.shuffle(line)
            tmp_line = list(line)
            for point in tmp_line:
                tmp_block.append(point)
        b3_rep.append(tmp_block)
    # for line in b3_comb_polar:
    #     tmp_polar_block = []
    #     for i in range(rep):
    #         random.shuffle(line)
    #         tmp_line = list(line)
    #         for point in tmp_line:
    #             tmp_polar_block.append(point)
    #     b3_rep_polar.append(tmp_polar_block)
    b3_comb= np.array(b3_comb)
    # b3_comb_polar = np.array(b3_comb_polar)
        
    print(b3_rep)
    print(np.shape(b3_rep))
    # print('\n')
    # print(b3_rep_polar)
    # print(np.shape(b3_rep_polar))


    if b_save:
        cwd = os.getcwd()
        fname = cwd + "\\Pilot\\targetpoint\\" + "block3targetspoints"
        mode = psg.popup_get_text("Mode being 'grid', 'polar' or 'axis'")
        # if mode == "Yes":
        #     mode = 'grid'
        # elif mode == "No":
        #     mode = 'polar'
        # else:
        #     mode = ""
        if mode != "":
            np.save(fname + "_" + mode, b3_rep)
        else:
            np.save(fname, b3_rep)
        # np.save(fname + "_polar", b3_rep_polar)
    
    return b3_rep
           