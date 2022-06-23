#!/usr/bin/env python3

from multiprocessing.dummy import Process
from functools import partial
import os
import re
import subprocess
import sys
import tkinter
from tkinter import Button, BooleanVar, Checkbutton, END, Entry, filedialog, Frame, Label, LabelFrame, Menu, messagebox, scrolledtext, StringVar, Tk

#allows the python subprocess output to be printed in real time
os.environ['PYTHONUNBUFFERED'] = '1'

#initialize process variable, to check if process is running or not
process = False

#allows subprocess to work on unix and windows
python = 'python3'

if 'win' in sys.platform:

    python = 'python'


#functions ---------------------------------------------------------------
#about menu function
def aboutSection():

   messagebox.showinfo('About',
                       'M3U8 Tester is an easy-to-use GUI program which tests '
                       'M3U8 files as well as raw M3U8 web pages (paste.gg, '
                       'pastebin.com/raw, raw.githubusercontent.com) as well as '
                       'raw webpages and files with a list of links only, '
                       'and returns the working links in a M3U8 file.\n\n'
                       'Created by Slick9000 and IrBee.\n\n'
                       'Users can donate at: https://www.paypal.com/paypalme/irbee246'
                       )


#help menu function
def helpSection():

   messagebox.showinfo('Help',
                       'For the URL option, users may enter a raw URL formatted in '
                       'M3U8 format into the textbox manually with "Ctrl + V", or '
                       'simply press the paste button to paste into the input box.\n\n'    
                       'Checking the "Webpage not in M3U8 format" check box will allow the '
                       'user to use a URL which contains links not in M3U8 format.\n\n'
                       'For the FILE option, users may enter a file formatted in '
                       'M3U8 format into the textbox manually with Ctrl + V, or '
                       'simply press the "Browse" button to open the File Explorer.\n\n'
                       'Checking the "File not in M3U8 format" check box will allow the '
                       'user to use a file which contains links not in M3U8 format.\n\n'
                       'NOTE: If the file is not in M3U8 format, and the check box '
                       'for links only is not selected, the output file will result in '
                       '"[]" for every link. Therefore, be sure to check the option.\n\n'
                       'IMPORTANT DISCLAIMER: A 64 bit version of VLC is required to be '
                       'installed on the user\'s system, otherwise this program will not '
                       'be able to function. This is due to how python and vlc interact '
                       'with one another, and the error "Could not find module libvlc.dll" '
                       'will occur.'
                       )


#paste button function
def pasteLink():

    try:
        
        source = inputFrame.clipboard_get()

        link.set(source)
        
    #prevents error caused by empty clipboard
    except _tkinter.TclError:

        #unlock the text box to allow output to be written to the window
        txtbox.configure(state='normal')

        txtbox.delete('1.0', END)

        txtbox.insert(END, 'ERROR: Nothing is currently copied to clipboard!')

        #brings cursor to the last line of output
        txtbox.see(END)

        #relock the text box
        txtbox.configure(state='disabled')

        return


#file explorer function
def browseFiles():
    
    source = filedialog.askopenfilename(initialdir = '/',
                                          title = 'Select a File',
                                          filetypes = (('M3U Files',
                                                        '*.m3u* *.m3u8*'),
                                                       ('All Files',
                                                        '*.*')))
    
    file.set(source)


#run subprocess function
def runCommand(link, file, timeout=None, window=None):

    #first portion tests for what type of source is input, link or file (with error handling)
    #second portion executes the command and prints it in the text box in the GUI

    #error message for if both fields are empty
    if link.get() == '' and file.get() == '':

        #unlock the text box to allow output to be written to the window
        txtbox.configure(state='normal')

        txtbox.delete('1.0', END)

        txtbox.insert(END, 'ERROR: No data inserted in fields.')

        #brings cursor to the last line of output
        txtbox.see(END)

        #relock the text box
        txtbox.configure(state='disabled')

        return

    
    #error if both fields have input
    if link.get() != '' and file.get() != '':

        #unlock the text box to allow output to be written to the window
        txtbox.configure(state='normal')

        txtbox.delete('1.0', END)

        txtbox.insert(END, 'ERROR: Data inserted in both fields.')

        #brings cursor to the last line of output
        txtbox.see(END)

        #relock the text box
        txtbox.configure(state='disabled')

        return

    #error for if both link test checkboxes are ticked
    if checkVal1.get() == True and checkVal2.get() == True:

        #unlock the text box to allow output to be written to the window
        txtbox.configure(state='normal')

        txtbox.delete('1.0', END)

        txtbox.insert(END, 'ERROR: Please only tick one parameter.\n'
                           'e.g Only "Webpage with files only" or   '
                           '"File with links only".'
                      )

        #brings cursor to the last line of output
        txtbox.see(END)

        #relock the text box
        txtbox.configure(state='disabled')

        return
    
    #run testing through raw webpage with only links
    elif link.get != '' and checkVal1.get() == True:

        option = 3

        source = link.get()
        
    #run testing through raw webpage
    elif link.get() != '':
        
        option = 1

        source = link.get()
        
    #run testing through file with only links
    elif file.get != '' and checkVal2.get() == True:

        option = 4

        source = file.get()
        
    #run testing through file
    elif file.get() != '':
        
        option = 2
        
        source = file.get()

    #unlock the text box to allow output to be written to the window
    txtbox.configure(state='normal')
    
    txtbox.delete('1.0', END)

    #to get directory of process. first one gets the current working directory
    #if running as a script, second one gets the working directory from files
    #embedded within pyinstaller's exectuable if running as an exe
    #command to build pyinstaller exectuable: pyinstaller --onefile --add-data="m3u8 tester.py;." '.\m3u8 tester gui.pyw'
    running_dir = os.getcwd()

    if getattr(sys, 'frozen', False): # Running as compiled

        running_dir = sys._MEIPASS

    global process

    #if checked play vlc stream in gui window
    if checkVal3.get() == True:

        videoFrame = Frame(tkWindow, padx=5, pady=5, width=40, height=20)

        videoFrame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky=tkinter.E+tkinter.W+tkinter.N+tkinter.S)

        #subprocess for running m3u8 tester
        process = subprocess.Popen(f'{python} "{running_dir}/m3u8 tester.py" {option} "{source}" {videoFrame.winfo_id()}',
                                   shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    else:

        #subprocess for running m3u8 tester
        process = subprocess.Popen(f'{python} "{running_dir}/m3u8 tester.py" {option} "{source}"',
                                   shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    for line in process.stdout:
        
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()

        #remove vlc logging output
        clean_output = re.sub(r'\[.*', '', line)
        
        txtbox.insert(END, f'{clean_output}\n')

        #brings cursor to the last line of output
        txtbox.see(END)
        
        #this prevents the giant white space that happens at the end of the output in the GUI
        #which is caused by subprocess
        if clean_output.startswith('File removed') or clean_output.startswith('Processing time'):

            return

    #relock the text box
    txtbox.configure(state='disabled')

#end subprocess function
def endSubprocess(event):
    
    if process == False:

        return

    if process.poll() == None:

        process.kill()
    
        #unlock the text box to allow output to be written to the window
        txtbox.configure(state='normal')

        txtbox.insert(END, 'Process has been ended and all data has been saved.\n')

        #brings cursor to the last line of output
        txtbox.see(END)

        #relock the text box
        txtbox.configure(state='disabled')


#initialize window
tkWindow = Tk()

#set window to non-resizable
tkWindow.resizable(False, False)

#set title
tkWindow.title('M3U8 Tester')

#keybind to end process with ctrl + c when process is running
#works identical to the keyboard interrupt if run from command line
tkWindow.bind('<Control-c>', endSubprocess)

#link label and text entry frame -----------------------------------------
inputFrame = Frame(tkWindow)

inputFrame.grid(row=0, column=0, sticky=tkinter.W+tkinter.E)   

linkLabel = Label(inputFrame, text='URL', font=('Arial', 14))

linkLabel.grid(row=0, column=1)

link = StringVar()

linkEntry = Entry(inputFrame, textvariable=link)

linkEntry.grid(row=0, column=2, padx=(10), pady=10)

button_paste_link = Button(inputFrame, text='Paste', command=pasteLink)

button_paste_link.grid(row=0, column=3)

#file label and file entry frame -----------------------------------------
fileLabel = Label(inputFrame,text='FILE', font=('Arial', 14))

fileLabel.grid(row=1, column=1)

file = StringVar()

fileEntry = Entry(inputFrame, textvariable=file)

fileEntry.grid(row=1, column=2, padx=(10), pady=10)

button_explore = Button(inputFrame, text='Browse', command=browseFiles)

button_explore.grid(row=1, column=3)

#run command -------------------------------------------------------------
runCommand = partial(runCommand, link, file)

#function for multithreading, to allow subprocess to run without the window freezing
def runCommandThread(event):

    runCommandProcess = Process(target=runCommand)
    
    runCommandProcess.start()
    
#keybind to run process by pressing the enter key
#(works the same as pressing the button)
tkWindow.bind('<Return>', runCommandThread)

#checkbox for if raw webpage only contains links
checkVal1 = BooleanVar(tkWindow)

checkVal1.set(False)

checkbox1 = Checkbutton(inputFrame, text='Webpage not in M3U8 format', var=checkVal1)

checkbox1.grid(row=0, column=4)

#checkbox for if file only contains links
checkVal2 = BooleanVar(tkWindow)

checkVal2.set(False)

checkbox2 = Checkbutton(inputFrame, text='File not in M3U8 format', var=checkVal2)

checkbox2.grid(row=1, column=4)

#checkbox for live stream video
checkVal3 = BooleanVar(tkWindow)

checkVal3.set(False)

checkbox3 = Checkbutton(inputFrame, text='Play live video?', var=checkVal3)

checkbox3.grid(row=2, column=2)

#start button
startButton = Button(inputFrame, text='Start', font=('Arial', 14), command=runCommandThread)

startButton.grid(row=4, column=1, padx=(10), pady=10)

#menu configuration ------------------------------------------------------
menu = Menu(tkWindow)

tkWindow.config(menu=menu)

filemenu = Menu(menu)

filemenu.add_separator()

menu.add_command(label='About', command=aboutSection)

menu.add_command(label='Help', command=helpSection)

#textbox frame -----------------------------------------------------------
textboxFrame = tkinter.LabelFrame(tkWindow, text='Processing Output', font=('Arial', 12), padx=5, pady=5)

textboxFrame.grid(row=5, column=1, columnspan=3, padx=10, pady=10, sticky=tkinter.E+tkinter.W+tkinter.N+tkinter.S)

textboxFrame.rowconfigure(0, weight=1)

textboxFrame.columnconfigure(0, weight=1)

#create the textbox
txtbox = scrolledtext.ScrolledText(textboxFrame, width=40, height=10)

txtbox.grid(row=0, column=0, sticky=tkinter.E+tkinter.W+tkinter.N+tkinter.S)

txtbox.insert(END, 'All processing data will output in this text box!')

#lock the text box on initialization
txtbox.configure(state='disabled')

tkWindow.mainloop()
