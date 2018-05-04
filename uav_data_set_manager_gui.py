#!/usr/bin/python
#
# This program provides a graphical user interface component for renaming Micasense flight folders to conform
# to the naming requirements for input files to the Micasense data archiving program.
#
# Version 0.1 November 08,2017 Initial Version
# Version 0.2 November 27,2017 Removed experiment_id from output file name since flights can now cover
# multiple experiments.
# Version 0.3 May 2,2018 Saved the original flight folder name in file 'source_flight_folder_name.txt'
# so that uas_run.notes can be updated without manual intervention.
#


try:
    from Tkinter import *  # noqa
except:
    from tkinter import *  # noqa
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename,asksaveasfilename,askdirectory

import os
import subprocess
import piexif # Use this to find start date and time of the 100th image
import shutil
import time
from pathlib import Path


def getFlight_start_date_time(oldFolderName,flightSet):
    imageList = []
    imageFileType = 'tif'
    imagePath = os.path.join(oldFolderName, flightSet, '000')
    imageFileList = get_image_file_list(imagePath, imageFileType, imageList)
    for i in imageFileList:
        imageID = os.path.join(imagePath, imageFileList[1])
        exif_dict = piexif.load(imageID)
        dateTimeStr = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        dateStr = dateTimeStr.split(' ')[0].replace(':', '')
        timeStr = dateTimeStr.split(' ')[1].replace(':', '')
        if dateStr[0:4] > '2015':
            startDate.set(dateStr)
            startTime.set(timeStr)
            print("Flight Date and Time", flightSet, dateStr, timeStr)
            break
    pass

def get_flight_data_sets():
    global flightSets
    oldFolderName= askdirectory()
    if oldFolderName:
        oldFolderPath.set(oldFolderName)
        newFolderParent.set(os.path.abspath(os.path.join(oldFolderName, os.pardir)))
        flightSets = []
        flightSets = next(os.walk(oldFolderName))[1]
        flights = flightSets.sort()
        ttk.Button(mainframe, text='Rename Data Set(s)', state=NORMAL,command=onRename).grid(row=10, column=2,
                                                                            sticky=W,
                                                                            pady=(10, 0),
                                                                            padx=(5, 0))
        pass


def onRename():

    ttk.Button(mainframe, text='Rename Data Set(s)', state=DISABLED).grid(row=10, column=2, sticky=W, pady=(10, 0),
                                                                          padx=(5, 0))
    parentPath=str(newFolderParent.get())
    oldFolderName=str(oldFolderPath.get())
    flights=flightSets
    flightIndex=0
    for count,flight in enumerate(flights):
        flightSet=flightSets[flightIndex]
        getFlight_start_date_time(oldFolderName, flightSet)
        filename=str(dateEntry.get()) + '_' + str(timeEntry.get()) + '_' \
                 + str(elevationEntry.get()) + '_'+ str(cameraType.get()) + '_'\
                 + str(angleEntry.get()) + '_' + str(imageFormat.get()) + '_'\
                 + str(count)
        oldFlightPath.set(os.path.join(oldFolderName, flight))
        oldFlightFolder=(os.path.join(oldFolderName,flight))
        newFolder.set(os.path.join(parentPath,filename))
        newFlightPath=str(newFolder.get())
        time.sleep(2)
        setparameters=messagebox.showinfo("Set File Name Parameters","Please check or set the filename parameters and click OK.")
        renameFolder=messagebox.askyesno("Rename", "Do you want to rename the folder \n FROM: \n" + oldFlightFolder + "\n TO: \n" + str(newFolder.get()))
        print("Old Name: " + oldFlightFolder + " New Name: " + newFlightPath)
        if renameFolder:
            temp=oldFlightPath.get()
            origPath = Path(temp)
            origFilename = temp.split(os.sep)[-2]
            outFilePath = origPath / 'source_flight_folder_name.txt'
            with open(outFilePath, 'a') as out:
                out.write(origFilename + '\n')
            os.rename(str(oldFlightFolder),newFlightPath)
        else:
            print('Skipping rename of '+str(oldFlightPath))
        flightIndex+=1
    deleteFolder=messagebox.askyesno("Remove", "Do you want to remove the old folder: " + oldFolderName)
    if deleteFolder:
        shutil.rmtree(oldFolderName) #Not sure if we want to do this - Error Scenarios!
        print("Removed old folder " + oldFolderName)

def center_window(width,height):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def clearFields():
    pass


def get_image_file_list(uasPath, imageType, imageFileList):
    # Return a list of the names and sample date & time for all image files.

    # Get list of files in uas staging directory

    print("Fetching list of image files...")

    filestocheck = subprocess.check_output(['ls', '-1', uasPath], universal_newlines=True)

    afile = ''
    filelist = []

    for char in filestocheck:
        if char != '\n':
            afile += char
        else:
            filelist.append(afile)
            afile = ''

            # Get the subset of files that are the image files

    for f in filelist:
        imageFileType=f.split('.')[1]
        isimagefile = (f != '' and imageFileType == imageType)
        if isimagefile:
            imageFileList.append(f)
    return imageFileList


if __name__ == '__main__':

# Initialize Tkinter

    sequence=1

    root = Tk()
    root.geometry('1025x350')
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    root.title("UAV Data Set Manager")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

    ttk.Label(mainframe,text="Date (YYYYMMDD)").grid(row=2,sticky=W,padx=(5,0))
    startDate = StringVar(None)
    dateEntry = ttk.Entry(mainframe, textvariable=startDate)
    dateEntry.grid(row=2,column=1,sticky=W)

    ttk.Label(mainframe,text="Time (hhmmss)").grid(row=3,sticky=W,padx=(5,0))
    startTime = StringVar(None)
    timeEntry = ttk.Entry(mainframe, textvariable=startTime)
    timeEntry.grid(row=3,column=1,sticky=W)

    ttk.Label(mainframe,text="Planned Elevation (m)").grid(row=5,sticky=W,padx=(5,0))
    elevation = StringVar(None)
    elevation.set('20m')
    elevationEntry = ttk.Entry(mainframe, textvariable=elevation)
    elevationEntry.grid(row=5,column=1,sticky=W)

    ttk.Label(mainframe, text="Camera Type").grid(row=6, sticky=W, padx=(5, 0))
    cameraType = StringVar(mainframe)
    cameraChoices = ['MRE', 'DJI', 'Nano']
    cameraType.set('MRE')
    cameraMenu = OptionMenu(mainframe, cameraType, *cameraChoices)
    cameraMenu.grid(row=6, column=1, sticky=W)

    ttk.Label(mainframe,text="Lens Angle (Deg)").grid(row=7,sticky=W,padx=(5,0))
    angle = StringVar(None)
    angle.set('90')
    angleEntry = ttk.Entry(mainframe, textvariable=angle)
    angleEntry.grid(row=7,column=1,sticky=W)

    ttk.Label(mainframe, text="Image Format").grid(row=8, sticky=W, padx=(5, 0))
    imageFormat = StringVar(mainframe)
    imageChoices=['Still', 'Video']
    imageFormat.set('Still')
    imageMenu = OptionMenu(mainframe, imageFormat, *imageChoices)
    imageMenu.grid(row=8, column=1,sticky=W)

    ttk.Label(mainframe, text="Selected Dataset").grid(row=0, sticky=W,pady=(10,0),padx=(5,0))
    oldFolderPath = StringVar(None)
    oldFolder = StringVar(None)
    newFolderParent = StringVar(None)
    oldFolderEntry = ttk.Entry(mainframe, textvariable=oldFolderPath,width=80)
    oldFolderEntry.grid(row=0, column=1,pady=(10,0))

    ttk.Label(mainframe, text="New Dataset Name").grid(row=10, sticky=W,pady=(10,0),padx=(5,0))
    newFolderPath=StringVar(None)
    newFolder = StringVar(None)
    outPath = StringVar(None)
    oldFlightPath = StringVar(None)
    newFolderEntry = ttk.Entry(mainframe, textvariable=newFolder,width=80)
    newFolderEntry.grid(row=10, column=1,pady=(10,0))

    ttk.Button(mainframe, text='Quit', command=mainframe.quit).grid(row=12, column=2, sticky=E)
    ttk.Button(mainframe, text='Choose Data Set', command=get_flight_data_sets).grid(row=0, column=2, sticky=W,pady=(10,0),padx=(5,0))
    ttk.Button(mainframe, text='Rename Data Set(s)', state=DISABLED).grid(row=10, column=2, sticky=W, pady=(10, 0),
                                                                                           padx=(5, 0))

    root.mainloop()

    root.destroy()
