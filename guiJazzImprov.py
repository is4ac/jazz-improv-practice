from tkinter import Tk, Label, Button, StringVar
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

        self.playing = False

        self.label = Label(master, text="Scan the jazz pattern cards and play along!\n\n\nSelected patterns:\n\n")
        self.label.grid(columnspan=8)

        self.pattern_labels = []
        for i in range(4):
            self.pattern_labels.append(Label(master, text="[none]\n\n"))
            self.pattern_labels[i].grid(row=2, columnspan=2, column=i*2)

        self.patterns_count = 0

        self.play_pause_button = Button(master, text="Play", command=self.playAndPause)
        self.play_pause_button.grid(row=5, column=2)

        self.stop_button = Button(master, text="Stop", command=self.stop)
        self.stop_button.grid(row=5, column=3)

        self.clear_button = Button(master, text="Clear", command=self.clear)
        self.clear_button.grid(row=5, column=4)

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.grid(row=5, column=5)

        self.audioPlayer = AudioPlayer()

        # start a new thread to listen for NFC reader input
        t = Thread(target=self.listenNFC)
        t.daemon = True
        t.start()

    def playAndPause(self):
        """
        Starts playing the music and patterns
        """
        self.playing = not self.playing
        print("Play/Pause!")

        if self.playing:
            self.audioPlayer.play()
            self.play_pause_button.config(text="Pause")
        else:
            self.audioPlayer.pause()
            self.play_pause_button.config(text="Play")

    def stop(self):
        """
        Stops the music
        """
        print("Stop!")
        self.audioPlayer.stop()

        if self.playing:
            self.play_pause_button.config(text="Play")
            self.playing = False

    def clear(self):
        """
        Clears all pattern tracks and stops the music
        """
        print("Clear!")
        self.stop()
        self.audioPlayer.clearTracks()
        self.patterns_count = 0

        for label in self.pattern_labels:
            label.config(text="[none]\n\n")

    def listenNFC(self):
        # infinite loop, keep listening until the program quits
        # happens in another thread from the main GUI loop
        while True:
            card = readTag()
            number = int(card) # extract the int value from the string

            if 1 <= number <= NUMBER_OF_PATTERNS:
                # stop the audio first so it doesn't insert the pattern into a weird spot
                self.stop()

                # add the audio track of the selected pattern
                self.audioPlayer.addPattern(PATTERN_FILE + str(number) + ".wav")

                # change the label on the screen
                self.pattern_labels[self.patterns_count].config(text="Pattern " + str(number) + "\n\n")

                # update the number of patterns currently scanned
                self.patterns_count += 1


root = Tk()
my_gui = ImprovApp(root)
root.mainloop()
