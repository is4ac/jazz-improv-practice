from tkinter import Tk, Label, Button
from audioPlayer import AudioPlayer
from NFCReader import readTag
from threading import Thread


# the beginning file path for all pattern track files. ends with a number + .wav
PATTERN_FILE = "audio/C_90_pattern_"
# total number of patterns. update this when adding more pattern cards
NUMBER_OF_PATTERNS = 4


class ImprovApp:
    def __init__(self, master):
        self.master = master
        master.title("Jazz Patterns Practice")

        self.label = Label(master, text="Scan the jazz pattern cards and play along!")
        self.label.pack()

        self.play_button = Button(master, text="Play", command=self.play)
        self.play_button.pack()

        self.pause_button = Button(master, text="Pause", command=self.pause)
        self.pause_button.pack()

        self.stop_button = Button(master, text="Stop", command=self.stop)
        self.stop_button.pack()

        self.clear_button = Button(master, text="Clear", command=self.clear)
        self.clear_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.audioPlayer = AudioPlayer()

        # start a new thread to listen for NFC reader input
        t = Thread(target=self.listenNFC)
        t.daemon = True
        t.start()

    def play(self):
        """
        Starts playing the music and patterns
        """
        print("Play!")
        self.audioPlayer.play()

    def pause(self):
        """
        Pauses the music
        """
        print("Pause!")
        self.audioPlayer.pause()

    def stop(self):
        """
        Stops the music
        """
        print("Stop!")
        self.audioPlayer.stop()

    def clear(self):
        """
        Clears all pattern tracks and stops the music
        """
        print("Clear!")
        self.stop()
        self.audioPlayer.clearTracks()

    def listenNFC(self):
        # infinite loop, keep listening until the program quits
        # happens in another thread from the main GUI loop
        while True:
            card = readTag()
            number = int(card) # extract the int value from the string

            if 1 <= number <= NUMBER_OF_PATTERNS:
                # stop the audio first so it doesn't insert the pattern into a weird spot
                self.stop()
                self.audioPlayer.addPattern(PATTERN_FILE + str(number) + ".wav")


root = Tk()
my_gui = ImprovApp(root)
root.mainloop()
