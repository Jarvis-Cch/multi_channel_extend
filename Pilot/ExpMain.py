import numpy as np
import PySimpleGUI as psg
from datetime import datetime
import serial, io, time, pytz, os
import serial.tools.list_ports
import lib.fileIO as fileIO
import lib.SerialComm as serialCOM
from lib.SerialComm import BYTEScmd as bytescmd
import lib.CombTargetGen as CTGen


def PilotExp(subjectID = None, b_ArduinoCom = True, bTest = False) -> None:
    psg.theme('NeutralBlue')
    #If not testing and no subject ID input, ask for subjectID
    if not bTest and subjectID is None:
        while True:
            subjectID = psg.popup_get_text("Please enter the subject ID")
            if subjectID != "":
                break
    #If using Arduino COM, ask for serial COM parameters
    
    if b_ArduinoCom:
        initcmd = target2cmd(np.array([[0, 0], [0, 0]]), 1000)
        d_COMPara = serialCOM.ComParaGet()
        arduino = serial.Serial(port = d_COMPara["COM"], baudrate=d_COMPara["baudrate"], timeout = d_COMPara["timeout"])
        time.sleep(0.005)
        arduino.write(serialCOM.BYTEScmd(initcmd[0]))
        del initcmd
        time.sleep(1)
        arduino.reset_input_buffer()
    
    #Obtain the target point file
    # fname = psg.popup_get_file(message="Choose the target point .npy file")
    folder = os.getcwd()
    fname = f"{folder}\\Pilot\\targetpoint\\polar_seed1024_offseed23.npy"
    targetPoints = fileIO.openNpy(fname=fname, b_list=False) #Targetpoints =  3 Blocks > 5 Offsets > 5 JND Conditions * 10 Reps (randomized) > Trials x 2
    
    #Record the Start time of the experiment
    timestamp = {} #Dict to save different timestamp with label
    timestamp["Starttime"] = datetime.now()
    print(f"Start Time: {timestamp['Starttime']}") #Print the Start Time of the experiment
    
    hist = []
    blockorder = set(np.linspace(start = 1, stop = len(targetPoints), num = len(targetPoints), endpoint= True)) # blockorder = {1,2,3}
    blocknow = -1
    for i in range(len(targetPoints)):
        
        while(not (blocknow in blockorder)): 
            blocknow = int(psg.popup_get_text(f"Pick the block (OPTIONS: {blockorder})")) #Ask which block to perform
            if(blocknow in blockorder):
                blockorder.discard(blocknow) #Discard the picked block from blockorder
                break
        
        
        block_len = len(targetPoints[blocknow-1]) #Get the length of the block to setup to for loop to complete the selected block
        offsetorder = set(np.linspace(start = 1, stop = block_len, num = block_len, endpoint= True)) #offsetorder = {1,2,3,4,5}
        offsetnow = -1
        block_hist = []
        
        for j in range(block_len):
            while(not (offsetnow in offsetorder)):
                offsetnow = int(psg.popup_get_text(f"Pick the offset (OPTIONS: {offsetorder})")) #Ask which offset to perform
                if(offsetnow in offsetorder):
                    offsetorder.discard(offsetnow)
                    offsetnow
                    break
            offset_len = len(targetPoints[blocknow-1][offsetnow-1])
            trialnow = int(psg.popup_get_text(f"Enter the starting trial number (1 - {offset_len})")) #Start from 1 to the end as len() returns index + 1
            trialnow = trialnow - 1 #Convert back to list index
            
            offset_hist = []
            entry = []
            for k in range(offset_len - trialnow):
                nd_trial = targetPoints[blocknow-1][offsetnow-1][trialnow+k]
                #730 is the actuation time of servo moving from 512(0 deg) to 614(30deg) with 150 spd
                #Calculation: time = 50 + (614-512)/150*1000 = 50 + (102/150)*1000 = 50 + 680 = 730
                targetcmd = target2cmd(nd_trial, 730)
                resettrial = np.array([[0, 0], [0, 0]])
                resetcmd = target2cmd(resettrial, 1000)
                
                for stretch_num in range(2):
                    entry.append(int(nd_trial[stretch_num][0]))
                    entry.append(int(nd_trial[stretch_num][1]))
                    title = f"Trial {trialnow + 1 + k} / {offset_len}"
                    
                    if(stretch_num == 1): #Pause popup before 2nd stretch
                        psg.popup_no_buttons("Pause for 2s", auto_close = True, auto_close_duration=2)
                    
                    
                    #Stretch
                    if b_ArduinoCom:
                        arduino.write(bytescmd(targetcmd[stretch_num]))
                        time.sleep(0.03)
                        arduino.reset_output_buffer()
                    else:
                        print(f"{targetcmd[stretch_num]}\n")
                    
                    psg.popup_no_buttons("Stretching", title = title, auto_close=True, auto_close_duration=0.8, background_color='red')
                    
                    if b_ArduinoCom:
                        arduino.reset_input_buffer() #Clear the actuation time data from the Arduino side
                    
                    
                    #Hold at stretch position for 2s
                    psg.popup_no_buttons("Hold for 2s", title = title, auto_close=True, auto_close_duration=2) 
                    
                    
                    #Return to 0 position
                    if b_ArduinoCom:
                        arduino.write(bytescmd(resetcmd[stretch_num]))
                        time.sleep(0.03)
                        arduino.reset_output_buffer()
                    else:
                        print(f"{resetcmd[stretch_num]}\n")
                    psg.popup_no_buttons("Returning", title = title, auto_close=True, auto_close_duration=1) #Returning back to 0 position
                    if b_ArduinoCom:
                        arduino.reset_input_buffer() #Clear the actuation time data from the Arduino side
                        
                    if(stretch_num == 1): #Ask the comparison question
                        QLayout = [[psg.Text("Which stretch sensation felt stronger/moving more?")],
                            [psg.Radio("1st", "respond", key = 0), psg.Radio("2nd", "respond", key = 1)],
                            [psg.OK()]]
                        window = psg.Window(title = "Comparison Question" + title, layout = QLayout, size = (500, 500))
                        while True:
                            event, values = window.read()
                            if event == "OK" and (list(values.values())[0] != 0 or list(values.values())[1] != 0):
                                if(list(values.values())[0] == True):
                                    entry.append(0)
                                else:
                                    entry.append(1)
                                offset_hist.append(entry)
                                break
                            elif event == psg.WIN_CLOSED:
                                entry = []
                                quit()
                        window.close()
                        del QLayout
                        entry = []
            saveStr = psg.popup_yes_no("Save this offsets result?")
            if saveStr == "Yes":
                timestamp['Endtime'] = datetime.now()
                saveNpz(subjectID, offset_hist, timestamp)
                timestamp['Starttime'] = datetime.now() #Reset the starttime for the next line
                nasa_question(subjectID, blocknow, offsetnow)
                quit = psg.popup_yes_no("Want to quit now?")
                if quit == "Yes":
                    quit()
                else:
                    pass
            else:
                pass
            block_hist.append(offset_hist)
        hist.append(block_hist)
    timestamp['Endtime'] = datetime.now()
    saveStr = psg.popup_yes_no("Save all result ?")
    if saveStr == "Yes":
        timestamp['Endtime'] = datetime.now()
        saveNpz(subjectID, offset_hist, timestamp)
    else:
        pass
    return hist, timestamp

def target2cmd(nd_trial, time):
    """Converting trial (numpy.ndarray shape(2,2), time) into str[2] command
        []

    Args:
        nd_trial (numpy.ndarray): numpy.ndarray with a shape of (2,2) and structure of [[stretch1_q1, stretch1_q2], [stretch2_q1, stretch2_q2]]
        time (int): time in milliseconds

    Raises:
        TypeError: nd_trial type or shape error
        TypeError: time type error

    Returns:
        _str_: string list[2] with str[0] for the first stretch and str[1] for the second stretch
    """
    if (not isinstance(nd_trial, np.ndarray)) and nd_trial.shape != (2,2):
        raise TypeError("target2cmd nd_trial input type not numpy.ndarray or shape is not (2,2)")
    elif not isinstance(time, int):
        raise TypeError("target2cmd time input is not type 'int'")
    else:
        pos1_q1 = pos2motor(int(nd_trial[0][0]))
        pos1_q2 = pos2motor(int(nd_trial[0][1]))
        pos2_q1 = pos2motor(int(nd_trial[1][0]))
        pos2_q2 = pos2motor(int(nd_trial[1][1]))
        cmd1 = f"{pos1_q1},{pos1_q2};{time},{time}"
        cmd2 = f"{pos2_q1},{pos2_q2};{time},{time}"
        cmd = [cmd1, cmd2]
    return cmd

def pos2motor(val):
    """Converting angles values (-150, 150) to motor position values (0, 1023)

    Args:
        val (int): Angle values within (-150, 150)

    Raises:
        TypeError: val input is not type int

    Returns:
        int: rounded motor command value (0, 1023)
    """
    if isinstance(val, int):
        val = np.clip(val, -150, 150, dtype = int)
        val = np.interp(val, [-150, 150], [0, 1023])
        val = round(val)
    else:
        val = None
        raise TypeError("pos2motor input should be int type only")
    return val

def saveNpz(subjectID, hist, timestamp) -> None:
    """Function for saving hist/timestamp var after each offset in the block was done

    Args:
        subjectID (_str_): Subject ID in str format
        hist (_list_): [t1_q1, t1_q2, t2_q1, t2_q2, ans]
        timestamp (_dict_): Starttime and Endtime timestamp
    """
    time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = psg.popup_get_text("Enter the file name")
    folder = psg.popup_get_folder("Choose the folder to save file")
    fname = f"{folder}/{time_now}_subjectID{subjectID}_{fname}"
    np.savez(file=fname, hist = hist, timestamp = timestamp)
    
def nasa_question(subjectID, block, offset) -> None:
    subjectID = str(subjectID)
    block = str(block)
    offset = str(offset)
    t1 = [psg.Multiline("Please indicate on a scale from 0 to 10 for your agreement toward the following adjectives relative to the experience during the trial:", size = (60,5), key = "multiline1")]
    t2 = psg.Text("Mental Demand")
    t2_1 = []
    t2_1.append(psg.Text("Very Low"))
    t2_1.append(psg.Slider(range = (0, 10), default_value = 5, resolution = 1, key = "mental_demand", orientation='horizontal'))
    t2_1.append(psg.Text("Very High"))
    t3 = psg.Text("Physical Demand")
    t3_1 = []
    t3_1.append(psg.Text("Very Low"))
    t3_1.append(psg.Slider(range = (0, 10), default_value = 5, resolution = 1, key = "physical_demand", orientation='horizontal'))
    t3_1.append(psg.Text("Very High"))
    t4 = psg.Text("Temporal Demand")
    t4_1 = []
    t4_1.append(psg.Text("Very Low"))
    t4_1.append(psg.Slider(range = (0, 10), default_value = 5, resolution = 1, key = "temporal_demand", orientation='horizontal'))
    t4_1.append(psg.Text("Very High"))
    t5 = psg.Text("Performance")
    t5_1 = []
    t5_1.append(psg.Text("Perfect"))
    t5_1.append(psg.Slider(range = (0, 10), default_value = 5, resolution = 1, key = "performance", orientation='horizontal'))
    t5_1.append(psg.Text("Failure"))
    t6 = psg.Text("Effort")
    t6_1 = []
    t6_1.append(psg.Text("Very Low"))
    t6_1.append(psg.Slider(range = (0, 10), default_value = 5, resolution = 1, key = "effort", orientation='horizontal'))
    t6_1.append(psg.Text("Very High"))
    t7 = psg.Text("Frustration")
    t7_1 = []
    t7_1.append(psg.Text("Very Low"))
    t7_1.append(psg.Slider(range = (0, 10), default_value = 5, resolution = 1, key = "frustration", orientation='horizontal'))
    t7_1.append(psg.Text("Very High"))
    
    layout  = [
        [t1],
        [t2],
        [t2_1],
        [t3],
        [t3_1],
        [t4],
        [t4_1],
        [t5],
        [t5_1],
        [t6],
        [t6_1],
        [t7],
        [t7_1],
        [psg.Button("OK")]
    ]
    
    window = psg.Window("Questionaire - Task Load Index", layout, size = (700,700))
    while True:
        event, values = window.read()
        print(event, values)
        if event == "OK":
            break
    window.close()
    timenow = datetime.now().strftime("%Y%m%d_%H%M%S")
    remarks = psg.popup_get_text("Any Remarks?")
    if remarks != "":
        remarks = f"_{remarks}"
    else:
        pass
    folder = os.getcwd()
    filename = f"{folder}\\Pilot\\nasa\\{timenow}_subject{subjectID}_block{block}_off{offset}_nasa{remarks}"
    np.save(filename, values, allow_pickle=True)

def find_arudino(serial_number):
    for pinfo in serial.tools.list_ports.comports():
        if pinfo.serial_number == serial_number:
            return serial.Serial(pinfo.device)
    raise IOError("Could not find an arduino - is it plugged in?")

def Block3_Exp(mode, b_ArduinoCom = True, ser_num = '859353334373518162F1') -> None:
    
    #Check mode input
    mode_arr = ['polar', 'grid', 'axis', 'grid_test', 'axis_test']
    if mode not in mode_arr:
        exit()
    else:
        pass

    psg.theme('NeutralBlue')
    #Ask for subjectID
    while True:
        subjectID = psg.popup_get_text("Please enter the subject ID")
        if subjectID != "":
            break
    
    #Arduino initialization and reset the motor pos to 0, 0
    if b_ArduinoCom:
        Initcmd = target2cmd(np.array([[0, 0], [0, 0]]), 1000) #Set skin stretch module back to 0, 0 in 1 second
        d_COMPara = serialCOM.ComParaGet(ser_num = ser_num)
        arduino = serial.Serial(port = d_COMPara['COM'], baudrate = d_COMPara['baudrate'], timeout = d_COMPara['timeout'])
        time.sleep(0.005)
        arduino.write(bytescmd(Initcmd[0]))
        del Initcmd
        time.sleep(1)
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
    targetpoints = None
    #Load the targetpoints file depending on the coordinate system
    if mode == 'grid':
        # fname = os.getcwd() + "\\Pilot\\targetpoint\\block3targetspoints_grid.npy"
        b3_comb = CTGen.Block3CombGen('grid')
        targetpoints = CTGen.Block3CombRep(b3_comb, 10, False)
    elif mode == 'polar':
        # fname = os.getcwd() + "\\Pilot\\targetpoint\\block3targetspoints_polar.npy"
        b3_comb = CTGen.Block3CombGen('polar')
        targetpoints = CTGen.Block3CombRep(b3_comb, 10, False)
    elif mode == 'axis':
        # fname = os.getcwd() + "\\Pilot\\targetpoint\\block3targetspoints_axis.npy"
        b3_comb = CTGen.Block3CombGen('axis')
        targetpoints = CTGen.Block3CombRep(b3_comb, 10, False)
    elif mode == 'grid_test':
        # fname = os.getcwd() + "\\Pilot\\targetpoint\\block3targetspoints_grid_test.npy"
        b3_comb = CTGen.Block3CombGen('grid')
        targetpoints = CTGen.Block3CombRep(b3_comb, 1, False)
    elif mode == 'axis_test':
        # fname = os.getcwd() + "\\Pilot\\targetpoint\\block3targetspoints_axis_test.npy"
        b3_comb = CTGen.Block3CombGen('axis')
        targetpoints = CTGen.Block3CombRep(b3_comb, 1, False)
    # targetpoints =  np.load(fname) #ndarray(5,70,4) for 'grid' & 'polar'; (3,70,4) for 'axis'
    if targetpoints != None:
        print("Auto-Generation of targetpoint success\n")
        print(f"Auto-Generated targetpoints shape: {np.shape(targetpoints)}")
    
    #timestamp recording
    timestamp = {} #Dict to save all the timestamp (recording session time)
    timestamp['Startime'] = datetime.now()
    print(f"Start Time: {timestamp['Startime']}")
    
    #SETUP PHASE
    title = "Setup"
        #Attaching the skin stretch modules
    b_setup = True
    while(b_setup):
        attachment = psg.popup_ok("Is the skin stretch modules attached?\nIf OK, test stretches will be delivered.", title = title)
        if attachment == "OK":
            #Pre-stretch warning for 1 second
            psg.popup_no_buttons("Test Stretches Incoming", title = title, auto_close=True, auto_close_duration=1, background_color='yellow')
            
            #Stretching
            testcmd = target2cmd(np.array([[30, 30], [0, 0]]), 1000) #Set both skin stretch modules to 30 deg in 1 second
            if b_ArduinoCom:
                arduino.write(bytescmd(testcmd[0]))
                time.sleep(0.03)
                arduino.reset_output_buffer()
            else:
                print(f"{testcmd[0]}\n")
            psg.popup_no_buttons("Stretching", title = title, auto_close=True, auto_close_duration=1, background_color='red')
            if b_ArduinoCom:
                arduino.reset_input_buffer() #Clear the actuation time date from the Arduino
            
            #Hold at stretch position for 2s
            psg.popup_no_buttons("Hold for 2s", title = title, auto_close=True, auto_close_duration=2)
            
            #Return back to 0 position
            if b_ArduinoCom:
                arduino.write(bytescmd(testcmd[1]))
                time.sleep(0.03)
                arduino.reset_output_buffer()
            else:
                print(f"{testcmd[1]}\n")
            psg.popup_no_buttons("Returning", title = title, auto_close=True, auto_close_duration=1)
            if b_ArduinoCom:
                arduino.reset_input_buffer() #Clear the actuation time data from the Arduino
            
            attachment = psg.popup_yes_no("Is the attachment secure and comfortable?")
            if attachment == "Yes":
                b_setup = False
            elif attachment == "No":
                b_setup = True
            else:
                exit()
    
    timestamp['SetupEnd'] = datetime.now() #Store the setup end time
    print(f"Setup Time End: {timestamp['SetupEnd']}")
    #TRAINING SESSION
        
        
    
    #MAIN EXPERIMENT
        #Decide the line sequence first so that the experiment can run automatically
    line_sequence = np.linspace(1, len(targetpoints), num=len(targetpoints), endpoint=True, dtype=int).tolist()
    str_main = psg.popup_ok("Ready to start the main experiment?")
    if str_main == "OK":
        timestamp['MainStart'] = datetime.now()
        print(f"Main Experiment Start Time: {timestamp['MainStart']}")
        points_seq = np.concatenate((np.zeros(35), np.ones(35)))
        rng = np.random.default_rng()
        hist = []
        for iter, line in enumerate(line_sequence): #targetpoints has 5 offset lines (parallel in grid or different angle in polar)
            line_hist = []
            entry = []
            line_targetpoints = targetpoints[line-1] #Compensate for line starting from 1 instead of 0
            rng.shuffle(points_seq)
            LineStart = datetime.now()
            for i, points in enumerate(line_targetpoints): #Have 70 pairs of points [q1, q2, q1_standard, q2_standard]
                tmp_points = np.reshape(points, (2,2))
                targetcmd = target2cmd(tmp_points, 730)
                resetcmd = target2cmd(np.array([[0,0],[0,0]]), 1000)
                seq = int(points_seq[i])
                for stretch_num in range(2):
                    if stretch_num == 0:
                        entry.append(tmp_points[seq][0]) #First stretch
                        entry.append(tmp_points[seq][1])
                        entry.append(tmp_points[1-seq][0]) #Second stretch
                        entry.append(tmp_points[1-seq][1])
                    # entry.append(points[seq][0]) #First stretch q1
                    # entry.append(points[seq][1]) #First stretch q2
                    # entry.append(points[1-seq][0]) #Second Stretch q1
                    # entry.append(points[1-seq][1]) #Second Stretch q2
                    title = f"Trial {i+1} / {len(line_targetpoints)}"
                    
                    #Pause popup before 2nd stretch
                    if stretch_num == 1:
                        psg.popup_no_buttons("Pause for 2s", auto_close=True, auto_close_duration=2)
                    
                    #Stretch
                    if b_ArduinoCom:
                        if stretch_num == 0:
                            arduino.write(bytescmd(targetcmd[seq]))
                        else:
                            arduino.write(bytescmd(targetcmd[1-seq]))
                        time.sleep(0.03)
                        arduino.reset_output_buffer()
                    else:
                        if stretch_num == 0:
                            print(f"{targetcmd[seq]}\n")
                        else:
                            print(f"{targetcmd[1-seq]}\n")
                    
                    psg.popup_no_buttons("Stretching", title = title, auto_close=True, auto_close_duration=0.8, background_color='red')
                    if b_ArduinoCom:
                        arduino.reset_input_buffer() #Clear the actuation time data from Arduino
                    
                    #Hold at stretch position for 2s
                    psg.popup_no_buttons("Hold for 2s", title = title, auto_close=True, auto_close_duration=2)
                    
                    #Return to 0 position
                    if b_ArduinoCom:
                        arduino.write(bytescmd(resetcmd[stretch_num]))
                        time.sleep(0.03)
                        arduino.reset_output_buffer()
                    else:
                        print(f"{resetcmd[stretch_num]}\n")
                    psg.popup_no_buttons("Returning", title = title, auto_close=True, auto_close_duration=1) #Returning back to 0 position
                    if b_ArduinoCom:
                        arduino.reset_input_buffer() #Clear the acutation time data from Arduino
                    
                    #Ask the comparison question
                    if(stretch_num == 1):
                        QLayout = [[psg.Text("Which stretch sensation felt stronger/moving more?")],
                            [psg.Radio("1st", "respond", key = 0), psg.Radio("2nd", "respond", key = 1)],
                            [psg.OK()]]
                        window = psg.Window(title = "Comparison Question" + title, layout = QLayout, size = (500, 200), element_justification='c')
                        Q_start = datetime.now() #The start of the popup question
                        while True:
                            event, values = window.read()
                            if event == "OK" and (list(values.values())[0] != 0 or list(values.values())[1] != 0):
                                Q_end = datetime.now() #Record the moment of clicking OK button
                                Q_time = Q_end - Q_start #Response time of each entry
                                if(list(values.values())[0] == True):
                                    entry.append(0)
                                    entry.append(Q_time)
                                else:
                                    entry.append(1)
                                    entry.append(Q_time)
                                line_hist.append(entry)
                                break
                            elif event == psg.WIN_CLOSED:
                                entry = []
                                if b_ArduinoCom:
                                    arduino.close()
                                quit()
                            
                        window.close()
                        del QLayout
                        entry = []
            hist.append(line_hist)
            LineEnd = datetime.now()
            nasa_question(subjectID = subjectID, block = 3, offset = line)
            timestamp_label = f"Line{line}_Duration"
            timestamp[timestamp_label] = LineEnd - LineStart
            print(f"{timestamp_label}: {timestamp[timestamp_label]}")
            
            if iter != len(line_sequence)-1: #5-min Rest between lines
                #Timer Window Layout
                TLayout = [[psg.Column([[psg.Text(size = (500,1), justification='center', key = '-OUT-')],
                            [psg.Button('Start')]],
                            element_justification='center')]]
                Twindow = psg.Window('5-min Rest', TLayout, auto_size_buttons=False, size = (500, 200))
                #Timer Loop
                amount = 0 #Set to 0 to stop the timer from auto counting
                b_Tstart = True
                while True:
                    Tevent, Tvalues = Twindow.read(timeout = 1000 if amount else None)
                    if Tevent is None:
                        break
                    elif Tevent == 'Start' and b_Tstart:
                        amount = 300 #5 x 60 sec = 300 sec
                        Twindow['-OUT-'].update(amount)
                        b_Tstart = False
                    if amount:
                        amount -= 1
                        Twindow['-OUT-'].update(amount)
                    if amount == 0 and not b_Tstart:
                        Twindow["-OUT-"].update('Close this window to start the next block')
                Twindow.close()
            elif iter == len(line_sequence)-1:
                print(hist)
                print('\n')
                print(hist[-1])
                timestamp['MainEnd'] = datetime.now()
                print(f"\nMain Experiment End: {timestamp['MainEnd']}")
                fname = os.getcwd() + "\\Pilot\\hist\\extendExp_raw\\" + datetime.now().strftime("%Y%m%d_%H%M%S_") + "subject" + subjectID
                np.savez(file=fname, hist = hist, timestamp = timestamp)
                if b_ArduinoCom:
                    arduino.close()
