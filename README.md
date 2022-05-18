# m3u8-tester
program which tests m3u8 stream files (or any stream, really) and outputs working streams to a m3u8 file named by date and time.

i created this program due to the fact that although many stream testers are available out there, none of them seem to have the simple option of outputting all working streams to a text file. i may be wrong, but it doesn't seem so.

many of these stream testers also don't have the flexibility of my m3u8-tester, which allows you to see the process in real time and see the number of streams which are working vs failing, and test streams regardless of the format they are in.

## [download](https://github.com/Slick9000/m3u8-tester/releases/latest)

## requirements
[requests](https://pypi.org/project/requests/)

[python-vlc](https://pypi.org/project/python-vlc/), as well as a 64 bit vlc installation.

## documentation
there are comments all over the code within both the gui and main program files explaining literally everything. if there is anything you are unsure about, be sure to check in them.

## features

**command line usage**

you can give `m3u8 tester.pyw`, `m3u8 tester.py` or the executable `m3u8-tester.exe` **direct command line arguments**

**e.g: `m3u8-tester.exe {option-number} {link/file-path}`, or you can use the tkinter gui included with the program.**

<br/>

**1: allows you to input a raw url formatted in m3u8 format**

**e.g:  [link](https://pastebin.pl/view/raw/f4892fcc)**

```
Adding new data entries...
New entries added to masterdata file.
Loading 383 URLS...


Press 'Ctrl+C' to end process at any time.
All current progress will be saved.

Stream is dead. Current state = State.Ended
Failed links: 1
Working links: 0
Completed: 1/383
Press 'Ctrl+C' to end process at any time.
All current progress will be saved.
```
...and so on

<br/>

**2: allows you to input a file formatted in m3u8 format**

**e.g: test.m3u8**

**contents:**

```
#EXTM3U

#EXTINF:-1 tvg-logo="https://album.mediaset.es/file/10002/2017/11/21/energy_circular_500_-1_4048.png" group-title="SPAIN",Energy
https://mdslivehlsb-i.akamaihd.net/hls/live/623617/energy/bitrate_1.m3u8
```

```
Adding new data entries...
New entries added to masterdata file.
Loading 1 URLS...


Press 'Ctrl+C' to end process at any time.
All current progress will be saved.

Stream is dead. Current state = State.Ended
Failed links: 1
Working links: 0
Completed: 1/1
No links available.
Removing 17th May, 2022 (16-24-01).m3u8 from folder...
File removed.
```

<br/>

**3: allows you to input a url with links, and does not have to be in m3u8 format. it will pull all of the stream links, test them, and output them to a m3u8 file**

**e.g: [link](https://pastebin.com/raw/SLZf7d4y)**

```
Adding new data entries...
New entries added to masterdata file.
Loading 10 URLS...


Press 'Ctrl+C' to end process at any time.
All current progress will be saved.

Stream is dead. Current state = State.Ended
Failed links: 1
Working links: 0
Completed: 1/10
Press 'Ctrl+C' to end process at any time.
All current progress will be saved.
```
...and so on

<br/>

**4: allows you to input a file with links, and does not have to be in m3u8 format. it will pull all of the stream links, test them, and output them to a m3u8 file**

**e.g: test2.m3u8 (this time, with a stream link that works lol)**

**contents:**

```
Stream 1: https://mdslivehlsb-i.akamaihd.net/hls/live/623617/energy/bitrate_1.m3u8
Stream 2: https://cnn-cnninternational-1-de.samsung.wurl.com/manifest/playlist.m3u8
```

```
Adding new data entries...
New entries added to masterdata file.
Loading 2 URLS...


Press 'Ctrl+C' to end process at any time.
All current progress will be saved.

Stream is dead. Current state = State.Ended
Failed links: 1
Working links: 0
Completed: 1/2
Press 'Ctrl+C' to end process at any time.
All current progress will be saved.

Stream is working. Current state = State.Playing
Failed links: 1
Working links: 1
Completed: 2/2
Link testing complete! Working links can be located in {current-working-directory}/17th May, 2022 (16-32-58).m3u8.
Failed links: 1/2
Working links: 1/2
Processing time: 0:00:16.110000

```
