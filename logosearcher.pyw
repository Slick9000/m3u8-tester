#!/usr/bin/env python3

from bs4 import BeautifulSoup
from functools import partial
from io import BytesIO
from multiprocessing.dummy import Process
from PIL import ImageTk, Image
from pyperclip import copy as Copy
import requests
import tkinter
from tkinter import Button, END, Entry, Frame, Label, LabelFrame, Menu, messagebox, Scale, scrolledtext, StringVar, Tk


def aboutSection():

   messagebox.showinfo('About',
                       'Logo Searcher is an easy-to-use GUI program which scrapes '
                       'Google for a logo for the channel you input.\n\n'
                       'It automatically copies the tvg-logo="(link)" to clipboard, so '
                       'all you have to do is input the channel you want. It\'s that simple.\n\n'
                       'It also displays the way the logo looks, and allows you to scroll the '
                       'index to find a different logo if you don\'t like the default given.\n\n'
                       'Created by Slick9000'
                       )

def pasteLink():

   source = inputFrame.clipboard_get()

   channel.set(source)

def runCommand(channel, timeout=None, window=None):

   global image

   #prevent image from being garbage collected by python

   #error message for if both fields are empty
   if channel.get() == '':

      #unlock the text box to allow output to be written to the window
      txtbox.configure(state='normal')

      txtbox.delete('1.0', END)

      txtbox.insert(END, 'ERROR: No data inserted in field.')

      #brings cursor to the last line of output
      txtbox.see(END)

      #relock the text box
      txtbox.configure(state='disabled')

      return

   check_startup = txtbox.get("1.0",'end-1c')

   #unlock the text box to allow output to be written to the window
   txtbox.configure(state='normal')

   if check_startup == startup_message:

      txtbox.delete('1.0', END)

   txtbox.insert(END, 'Processing...')

   url = f"https://www.google.com/search?q={channel.get()}&source=lnms&tbm=isch"

   HEADERS = {'content-type': 'image/png'}

   html = requests.get(url, headers=HEADERS).text

   soup = BeautifulSoup(html, "html.parser")

   img = soup.find_all("img")[slider.get()]['src']

   #image preview request
   imgRequest = requests.get(img)

   #bytesio object for image
   imgData = BytesIO(imgRequest.content)

   #create image from imgData
   image = ImageTk.PhotoImage(Image.open(imgData))

   #label to display image
   imgLabel = Label(tkWindow, image=image).place(x=450,y=20)

   txtbox.insert(END, f"\n\ntvg-logo=\"{img}\"\n\n")

   Copy(f"tvg-logo=\"{img}\"")

   txtbox.insert(END, "Copied to clipboard!\n")

   #brings cursor to the last line of output
   txtbox.see(END)

   #relock the text box
   txtbox.configure(state='disabled')

#window
tkWindow = Tk()

tkWindow.geometry('720x350')

tkWindow.resizable(False, False)

tkWindow.title('Logo Searcher')

#link label and text entry box
inputFrame = Frame(tkWindow)

inputFrame.grid(row=0, column=0, sticky=tkinter.W+tkinter.E)   

channelLabel = Label(inputFrame, text='Enter Channel Name', font=('Arial', 12))

channelLabel.grid(row=0, column=1)

channel = StringVar()

channelEntry = Entry(inputFrame, textvariable=channel)

channelEntry.grid(row=0, column=2, padx=(10), pady=10)

button_paste_link = Button(inputFrame, text='Paste', command=pasteLink)

button_paste_link.grid(row=0, column=3)

runCommand = partial(runCommand, channel)

#function for multithreading, to allow subprocess to run without the window freezing
def runCommandThread(event):

    runCommandProcess = Process(target=runCommand)
    
    runCommandProcess.start()

#keybind to run process by pressing the enter key
#(works the same as pressing the button)
tkWindow.bind('<Return>', runCommandThread)

#start button
startButton = Button(inputFrame, text='Find Logo!', font=('Arial', 12), command=runCommandThread)

startButton.grid(row=4, column=1, padx=(10), pady=10)

menu = Menu(tkWindow)

tkWindow.config(menu=menu)

filemenu = Menu(menu)

filemenu.add_separator()

menu.add_command(label='About', command=aboutSection)

#group2 Frame ----------------------------------------------------
textboxFrame = LabelFrame(tkWindow, font=('Arial', 12), padx=5, pady=5)

textboxFrame.grid(row=5, column=1, columnspan=3, padx=10, pady=10, sticky=tkinter.E+tkinter.W+tkinter.N+tkinter.S)

tkWindow.columnconfigure(0, weight=1)

tkWindow.rowconfigure(1, weight=1)

textboxFrame.rowconfigure(0, weight=1)

textboxFrame.columnconfigure(0, weight=1)

#image index slider
slider = Scale(tkWindow, from_=1, to=20,orient='vertical')

slider.grid(row=0, column=1, sticky=tkinter.E+tkinter.W+tkinter.N+tkinter.S)
    
#create the textbox
txtbox = scrolledtext.ScrolledText(textboxFrame, width=40, height=7)

txtbox.grid(row=0, column=0, sticky=tkinter.E+tkinter.W+tkinter.N+tkinter.S)

startup_message = 'Logo string is automatically entered to clipboard, as well as output here!'

txtbox.insert(END, startup_message)

#lock the text box
txtbox.configure(state='disabled')

tkWindow.mainloop()
