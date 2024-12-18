import serial, time, pytz
import PySimpleGUI as psg
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from serial.tools import list_ports

def ComParaGet(ser_num = '859353334373518162F1', Baudrate = None, timeout = 0.01):
    """Perform all the GUI steps for getting the Serial Communication Parameters

    Args:
        COM (str, optional): Name of the COM Port. Defaults to None.
        Baudrate (int, optional): Baudrate of the serial communication. Defaults to None.
        timeout (float, optional): timeout in miliseconds. Defaults to 0.01.

    Returns:
        _dict_: Parameters (dictionary) that contains the COM, baudrate and timeout values
    """
    dict_out = {}
    tmpbool = True
    # while tmpbool and COM is None:
    #     COM = psg.popup_get_text("Enter the COM Port", default_text='COM6')
    #     if COM != "":
    #         tmpbool = False
    
    tmpbool = True
    while tmpbool and Baudrate is None:
        Baudrate = psg.popup_get_text("Enter the Baudrate", default_text='1000000')
        if Baudrate != "":
            Baudrate = int(Baudrate)
            tmpbool = False
    
    dict_out["COM"] = find_arduino(ser_num).port
    dict_out["baudrate"] = Baudrate
    dict_out["timeout"] = timeout
    
    return dict_out
    
def COMPortList():
    """Print the port list and return port in list

    Returns:
        _list_: Info objects about serial ports
    """
    ports = list_ports.comports()
    for port in ports:
        print(port)
    return ports
    
def BYTEScmd(string):
    """Convert the string into bytes with newline character at the end and encoded in 'utf8' format

    Args:
        string (str, optional): input string command for serial communication.

    Returns:
        _bytes_: string command converted in bytes
    """
    return bytes(string+"\n", 'utf8')

def find_arduino(serial_number):
    for pinfo in serial.tools.list_ports.comports():
        if pinfo.serial_number == serial_number:
            return serial.Serial(pinfo.device)
    raise IOError("Could not find an arduino - is it plugged in?")