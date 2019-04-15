import pyaudio
import wave
import numpy
from WaveUtil import WaveUtil


class AudioPlayer:
    """
    Class that holds the music data and plays/streams the audio.
    Contains functions to play, pause, and stop the audio as well as
    change which audio tracks it loads.
    """

    def __init__(self, bg_track="audio/C_90_backing_track.wav", num_of_patterns=4):
        # instantiate PyAudio
        self.pa = pyaudio.PyAudio()
        self.patterns = []
        self.max_patterns = num_of_patterns

        # open backing track wave file and load the data to a WaveUtil object
        bg_wave = wave.open(bg_track, 'rb')
        data = bg_wave.readframes(bg_wave.getnframes())
        decodedData = numpy.fromstring(data, numpy.int16)
        self.backing_track = WaveUtil(decodedData, total_frames=len(decodedData))
        self.pattern_track = WaveUtil(total_frames=len(decodedData))   # will add more tracks to it later

        self.total_frames = len(decodedData)

        # open stream using callback function
        self.stream = self.pa.open(format=self.pa.get_format_from_width(bg_wave.getsampwidth()),
                                   channels=bg_wave.getnchannels(),
                                   rate=bg_wave.getframerate(),
                                   output=True,
                                   start=False,
                                   stream_callback=self.callback)

    def addPattern(self, file_name):
        if len(self.patterns) > self.max_patterns:
            raise Exception("Can't add any more patterns.")

        # open track wave file and load the data to a WaveUtil object
        sound = wave.open(file_name, 'rb')
        data = sound.readframes(sound.getnframes())
        decodedData = numpy.fromstring(data, numpy.int16)
        self.patterns.append(decodedData)
        self.updatePatternTrack()

    def addEmptyPattern(self):
        data = numpy.zeros(int(self.total_frames/self.max_patterns), dtype=numpy.int16)
        self.patterns.append(data)
        self.updatePatternTrack()

    def updatePattern(self, file_name, index):
        if index >= len(self.patterns):
            raise Exception("Index out of bounds.")

        # open track wave file and load the data to a WaveUtil object
        sound = wave.open(file_name, 'rb')
        data = sound.readframes(sound.getnframes())
        decodedData = numpy.fromstring(data, numpy.int16)
        self.patterns[index] = decodedData
        self.updatePatternTrack()

    def updatePatternTrack(self):
        self.pattern_track = WaveUtil(numpy.concatenate(self.patterns, axis=None),
                                      total_frames=self.total_frames)

    def clearTracks(self):
        self.pattern_track.clearTracks()

    # define callback function for streaming
    def callback(self, in_data, frame_count, time_info, status):
        data1 = self.backing_track.readframes(frame_count)
        data2 = self.pattern_track.readframes(frame_count)

        # mix as much as possible
        n = min(map(len, [data1, data2]))

        # mix by taking the mean of the two audio samples
        mix = (data1[:n] * 0.5 + data2[:n] * 0.5).astype(numpy.int16)

        # convert to string (bytes-like) before returning data
        return (mix.tostring(), pyaudio.paContinue)

    def play(self):
        # start the stream
        self.stream.start_stream()

    def pause(self):
        # stop stream
        self.stream.stop_stream()

    def stop(self):
        self.pause()

        # reset the track so it will start playing from the first frame again
        self.backing_track.setCurrentFrame(0)
        self.pattern_track.setCurrentFrame(0)

    def close(self):
        self.stream.close()

        # close PyAudio (7)
        self.pa.terminate()
