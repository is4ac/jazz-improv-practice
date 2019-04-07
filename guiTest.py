from tkinter import Tk, Label, Button
from audioPlayer import AudioPlayer

class ImprovApp:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="This is our first GUI!")
        self.label.pack()

        self.play_button = Button(master, text="Play", command=self.play)
        self.play_button.pack()

        self.pause_button = Button(master, text="Pause", command=self.pause)
        self.pause_button.pack()

        self.stop_button = Button(master, text="Stop", command=self.stop)
        self.stop_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.audioPlayer = AudioPlayer()

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


root = Tk()
my_gui = ImprovApp(root)
root.mainloop()