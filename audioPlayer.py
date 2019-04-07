import pyaudio
import wave
import numpy
import time
from WaveUtil import WaveUtil


class AudioPlayer:
    """
    Class that holds the music data and plays/streams the audio.
    Contains functions to play, pause, and stop the audio as well as
    change which audio tracks it loads.
    """
    def __init__(self):
        # instantiate PyAudio (1)
        self.pa = pyaudio.PyAudio()

        sound1 = wave.open("audio/C_90_backing_track.wav", 'rb')
        sound2 = wave.open("audio/C_90_pattern_1.wav", 'rb')
        sound3 = wave.open("audio/C_90_pattern_2.wav", 'rb')

        sounds = [sound1, sound2, sound3]

        data = [sound.readframes(sound.getnframes()) for sound in sounds]
        decodedData = [numpy.fromstring(d, numpy.int16) for d in data]

        self.backing_track = WaveUtil(decodedData[0], total_frames=len(decodedData[0]))
        self.pattern_track = WaveUtil(decodedData[1], total_frames=len(decodedData[0]))
        self.pattern_track.addTrack(decodedData[2])
        self.pattern_track.addTrack(decodedData[1])
        self.pattern_track.addTrack(decodedData[2])

        # open stream using callback (3)
        self.stream = self.pa.open(format=self.pa.get_format_from_width(sound1.getsampwidth()),
                                   channels=sound1.getnchannels(),
                                   rate=sound1.getframerate(),
                                   output=True,
                                   start=False,
                                   stream_callback=self.callback)

    # define callback (2)
    def callback(self, in_data, frame_count, time_info, status):
        data1 = self.backing_track.readframes(frame_count)
        data2 = self.pattern_track.readframes(frame_count)

        # mix as much as possible
        n = min(map(len, [data1, data2]))
        # mix by taking the mean of the two audio samples
        mix = (data1[:n] * 0.5 + data2[:n] * 0.5).astype(numpy.int16)
        return (mix.tostring(), pyaudio.paContinue)

    def play(self):
        # start the stream (4)
        self.stream.start_stream()

        # wait for stream to finish (5) (don't think this is necessary with the GUI app keeping things running)
        # while self.stream.is_active():
        #     time.sleep(0.1)

    def pause(self):
        # stop stream (6)
        self.stream.stop_stream()

    def stop(self):
        self.pause()
        self.backing_track.setCurrentFrame(0)
        self.pattern_track.setCurrentFrame(0)

    def close(self):
        self.stream.close()

        # close PyAudio (7)
        self.pa.terminate()
