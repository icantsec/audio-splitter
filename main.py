import PySimpleGUI as sg
from pygame import mixer, time
import pygame
from pydub import AudioSegment

import threading
import time

import os

global song


colors = {
    "main": "#a61111",
    "background": "white",
    "secondary": "#f2eded"

}

sg.LOOK_AND_FEEL_TABLE['Player'] = {
    'BACKGROUND': colors["background"],
     'BORDER': 0,
     'BUTTON': (colors["main"], colors["background"]),
     'INPUT': colors["secondary"],
     'PROGRESS': (colors["main"], colors["secondary"]),
     'PROGRESS_DEPTH': 0,
     'SCROLL': colors["secondary"],
     'SLIDER_DEPTH': 0,
     'TEXT': colors["main"],
     'TEXT_INPUT': colors["main"],}

sg.theme('Player')




symbol_font = ("Calibri", 20)
normal_font = ("Calibri", 14)

songSplitLayout = [
    [
        sg.Text("Portion: "),
        sg.Input("0:00", size=(5,1), key='-TS1-'),
        sg.Input("0:00", size=(5,1), key='-TE1-'),
        sg.Input("Name", size=(12,1), key='-N1-')
    ]
]

maxSongs = 200

songSplitLayoutExtraSpace = [
    [
        sg.Text("Portion: ", key='-TX' + str(i) + '-', visible=False),
        sg.Input("0:00", size=(5,1), key='-TS' + str(i) + '-', visible=False),
        sg.Input("0:00", size=(5,1), key='-TE' + str(i) + '-', visible=False),
        sg.Input("Name", size=(12,1), key='-N' + str(i) + '-', visible=False)
    ] for i in range(1, maxSongs)]

browseLayout = [
    [
        sg.Text("Choose a file: "),
        sg.Input(),
        sg.FileBrowse(key="-SOUND_PATH-")
    ],
    [
        sg.Button('Done', size=(4, 1), key='-DONE-', font=symbol_font)
    ]
]

layout= [
    [sg.Text("Untitled", key='-TITLE-')],
    [sg.ProgressBar(1, orientation="horizontal", size=(25,5), key="-PROGRESSBAR-")],
    [sg.Text("0:00/0:00", key='-PROGRESS-')],
    [
        sg.Button('↺', size=(4, 1), key='-PLAY-', font=symbol_font),
        sg.Button('⏵', size=(4, 1), key='-PAUSE-', font=symbol_font),
    ],
    [
        sg.Slider(range=(0, 100),
                orientation='h', size=(30, 10), enable_events=True, key = '-VOLUME-', default_value= 100)
    ],
    [
        sg.Column(songSplitLayoutExtraSpace, size=(400, 100), element_justification='center', justification='center', key='-ss-', scrollable=True, vertical_scroll_only=True)
    ],
    [
        sg.Button('+', size=(4, 1), key='-ADD-', font=symbol_font)
    ],
    [
        sg.Button('Export', key='-EXPORT-')
    ]
]

layout_c = [
    [sg.Column(layout, element_justification='center', justification='center')]
]

mixer.init()
is_playing = False
is_loaded = False

def verify_sound_object(audio_file):
    if not sound_path:
        sg.Popup("No song specificed.")

select_file = sg.Window('Choose File', browseLayout, finalize=True, font=normal_font)

global sound_path
sound_path = ""


while True:
    event, values = select_file.read()
    if event == sg.WIN_CLOSED or event=="-DONE-":
        sound_path = values["-SOUND_PATH-"]
        select_file.close()
        break

print(sound_path)
audio_player_window = sg.Window('Music Splitter', layout_c, finalize=True, font=normal_font)


pygame.init()

global ssNum
ssNum = 0

def genSongSplitLay():
    return [
        [
            sg.Text("Portion: "),
            sg.Input("0:00", size=(5,1), key='-TS' + str(ssNum) + '-'),
            sg.Input("0:00", size=(5,1), key='-TE' + str(ssNum) + '-'),
            sg.Input("Name", size=(12,1), key='-N' + str(ssNum) + '-')
        ]
    ]
def secToStamp(sec):
    min = str(round(sec/60))
    seconds = str(round(sec%60))
    if(len(seconds) < 2):
        seconds = "0" + seconds
    return min + ":" + seconds

class BackgroundTasks(threading.Thread):
    def run(self,*args,**kwargs):
        global song
        while True:
            try:
                song_length = round(song.get_length(), 2)
                currSec = round(mixer.music.get_pos()/1000, 2)

                currStamp = secToStamp(currSec)
                totalStamp = secToStamp(song_length)

                audio_player_window['-PROGRESS-'].update(currStamp + "/" + totalStamp)
                audio_player_window['-PROGRESSBAR-'].update(currSec/song_length)
                time.sleep(.05)
            except:
                audio_player_window['-PROGRESS-'].update("0:00/0:00")
                time.sleep(.05)

t = BackgroundTasks()
t.start()

def saveSongs(songsSave, fileName):
    for s in songsSave:
        startSplit = s["start"].split(":")
        endSplit = s["end"].split(":")
        nameSplit = s["name"].split(".")
        name = nameSplit[0]
        saveName = s["name"]
        startSec = (int(startSplit[0])*60 + int(startSplit[1]))*1000
        endSec = (int(endSplit[0])*60 + int(endSplit[1]))*1000
        exportSong = None
        format = "wav"
        if fileName.endswith("mp3") == "mp3":
            exportSong = AudioSegment.from_mp3(fileName)
            format = "mp3"
        else:
            exportSong = AudioSegment.from_wav(fileName)
        exportSong = exportSong[startSec:endSec]
        exportSong.export(saveName, format=format)

while True:
    if not sound_path:
        sg.Popup("No song specificed.")
        continue
    song_name = os.path.basename(sound_path)
    audio_player_window['-TITLE-'].update(song_name)

    event, values = audio_player_window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break

    global song


    song = mixer.Sound(sound_path)

    song_length = song.get_length()

    if event == '-PLAY-':
        is_loaded = True
        is_playing = True
        audio_player_window['-PLAY-'].update("↺")
        audio_player_window['-PAUSE-'].update("⏸")
        mixer.music.load(sound_path)
        mixer.music.play(1)

    elif event == '-PAUSE-':
        if not is_playing:
            if not is_loaded:
                is_loaded = True
                is_playing = True
                mixer.music.load(sound_path)
                mixer.music.play(1)
                audio_player_window['-PAUSE-'].update("⏸")
            else:
                is_playing = True
                audio_player_window['-PAUSE-'].update("⏸")
                mixer.music.unpause()
        else:
            is_playing = False
            audio_player_window['-PAUSE-'].update("⏵")
            mixer.music.pause()
    elif event == '-VOLUME-':
        volume = values['-VOLUME-']
        mixer.music.set_volume(volume/100)
    elif event == '-ADD-':
        ssNum += 1
        audio_player_window['-TX' + str(ssNum) + '-'].update(visible=True)#TX, TS, TE, N
        audio_player_window['-TS' + str(ssNum) + '-'].update(visible=True)
        audio_player_window['-TE' + str(ssNum) + '-'].update(visible=True)
        audio_player_window['-N' + str(ssNum) + '-'].update(visible=True)
        #audio_player_window.extend_layout(audio_player_window['-ss-'], genSongSplitLay())
        audio_player_window['-ss-'].contents_changed()
        #audio_player_window.refresh()
    elif event == '-EXPORT-':
        songsSave = []
        for i in range(1, 200):
            currSong = {}
            currSong["name"] = values['-N' + str(i) + '-']
            currSong["start"] = values['-TS' + str(i) + '-']
            currSong["end"] = values['-TE' + str(i) + '-']
            if currSong["end"] != "0:00":
                songsSave.append(currSong)
        if len(songsSave) < 1:
            sg.Popup("No portions defined.")
        else:
            saveSongs(songsSave, sound_path)
            sg.Popup("Sections exported.")

audio_player_window.close()
