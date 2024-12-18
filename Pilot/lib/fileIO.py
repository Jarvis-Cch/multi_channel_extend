import PySimpleGUI as psg
from datetime import datetime
import pytz
import numpy as np

def saveList(comb):
    """Saving the input comb into npy file

    Args:
        comb (_list_): list or numpy array that used for saving into a npy file
    """
    folder = psg.popup_get_folder("Select the folder to save the file")
    filename = psg.popup_get_text("Enter the filename")
    fname = f"{folder}/{filename}"
    str_now = datetime.now(pytz.timezone('Australia/Melbourne')).strftime("%Y%m%d_%H%M")
    savedate = psg.popup_yes_no("Add time stamp at the end of filename?")
    if savedate == "Yes":
        fname = fname + "_" + str_now
    else:
        pass
    np.save(file = fname, arr = comb)
    
    return None

def openNpy(fname = None, b_list = False):
    """Open .npy file into numpy array or list (Default to list)\n
        If no fname is provided, a popup will ask to choose a file

    Args:
        fname (_str_, optional): File path. Defaults to None.
        b_list (bool, optional): bool for controlling the return type (True for list, False for numpy array). Defaults to True.

    Returns:
        _list/numpy.array_: .npy opened in list or numpy.array
    """
    
    if fname is None:
        while True:
            fname = psg.popup_get_file("Choose the .npy file")
            if fname != "":
                break
    
    list_out = np.load(file = fname)
    
    if b_list:
        list_out = list_out.tolist()
    
    return list_out
    