import pyaudio
import wave
import numpy
import time
from WaveUtil import WaveUtil

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

sound1 = wave.open("audio/C_90_backing_track.wav", 'rb')
sound2 = wave.open("audio/C_90_pattern_1.wav", 'rb')
sound3 = wave.open("audio/C_90_pattern_2.wav", 'rb')

sounds = [sound1, sound2, sound3]

data = [sound.readframes(sound.getnframes()) for sound in sounds]
decodedData = [numpy.fromstring(d, numpy.int16) for d in data]

backing_track = WaveUtil(decodedData[0], total_frames=len(decodedData[0]))
pattern_track = WaveUtil(decodedData[1], total_frames=len(decodedData[0]))
pattern_track.addTrack(decodedData[2])
pattern_track.addTrack(decodedData[1])
pattern_track.addTrack(decodedData[2])


# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data1 = backing_track.readframes(frame_count)
    data2 = pattern_track.readframes(frame_count)

    # mix as much as possible
    n = min(map(len, [data1, data2]))
    # mix by taking the mean of the two audio samples
    mix = (data1[:n] * 0.5 + data2[:n] * 0.5).astype(numpy.int16)
    return (mix.tostring(), pyaudio.paContinue)


# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(sound1.getsampwidth()),
                channels=sound1.getnchannels(),
                rate=sound1.getframerate(),
                output=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()
