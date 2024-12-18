# import lib.CombTargetGen as CTGen
import lib.CombTargetGen as CTGen
import lib.fileIO as fileIO
import ExpMain
import numpy as np
import PySimpleGUI as psg
from datetime import datetime
import time, pytz, random, os
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports


###Experiment
# hist, timestamp = ExpMain.PilotExp(b_ArduinoCom=True)
ExpMain.Block3_Exp('axis_test', False)

###IC Test

# ###Randomize the target points within the same offset
# # CTGen.TargetPointsRand(seed = 23)
# b3_comb_grid = CTGen.Block3CombGen('grid')
# b3_comb_polar = CTGen.Block3CombGen('polar')
# print(list(b3_comb_grid))
# print('\n')
# print(b3_comb_polar)
# print('\n')

# #Plotting the grid and polar combinations line 
# plotting = psg.popup_yes_no("Plot the combination's lines of grid and polar understanding?")
# if plotting == "Yes":
#     #Separate the points from the [q1, q2, q1_mid, q2_mid] format to [q1, q2]
#     grid_points = []
#     for line in b3_comb_grid:
#         point_arr = []
#         for point in line:
#             point_arr.append([point[0], point[1]])
#         grid_points.append(point_arr)
#     polar_points = []
#     for line in b3_comb_polar:
#         point_arr = []
#         for point in line:
#             point_arr.append([point[0], point[1]])
#         polar_points.append(point_arr)

#     grid_points = np.array(grid_points) #[[line#1], [line#2], ..., [line#5]]
#     polar_points = np.array(polar_points) #[[line#1], [line#2], ..., [line#5]]

#     print(grid_points)
#     print('\n')
#     print(polar_points)
#     grid_color = ['#ffc100', '#ff9a00', '#ff7400', '#ff4d00', '#ff0000'] #Red-Orange Color Palette
#     polar_color = ['#234d20', '#36802d', '#77ab59', '#9ed670', '#c9df8a'] #Parrot Green Color Palette
#     radial_color = ['#dde6d5', '#a3b899','#8f9779', '#78866b', '#738276', '#738678', '#4d5d53'] #Dusty Sage & Sage Green Color Palette
#     for i, line in enumerate(grid_points):
#         tmp_line = line.T
#         plt.plot(tmp_line[0], tmp_line[1], color = grid_color[i])
#     for i, line in enumerate(polar_points):
#         tmp_line = line.T
#         plt.plot(tmp_line[0], tmp_line[1], color = polar_color[i])
    
#     magnitude = np.linspace(24, 36, 7, True)
#     angle_range = np.linspace(0, 90, 90, True)
    
#     for i, mag in enumerate(magnitude):
#         x = [mag*np.cos(np.deg2rad(angle)) for angle in angle_range]
#         y = [mag*np.sin(np.deg2rad(angle)) for angle in angle_range]
#         plt.plot(x, y, '--', color = radial_color[i])
#     plt.axis('square')
#     plt.xlim((0, 40))
#     plt.ylim((0, 40))
#     plt.title("2-DoF Understanding in Cartesian and Polar Coordinate System")
#     plt.ylabel("Skin Stretch Module 1 deg")
#     plt.xlabel("Skin Stretch Module 2 deg")
#     plt.grid()
#     plt.show()

# b3_comb_axis = CTGen.Block3CombGen('axis')
# b3_comb_grid = CTGen.Block3CombGen('grid')
# targetpoints = CTGen.Block3CombRep(b3_comb_axis, 10)
# print(targetpoints)
# CTGen.Block3CombRep(b3_comb_grid, 1)