import pyaudio
import wave
import numpy

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

sound1 = wave.open("audio/C_90_backing_track.wav", 'rb')
sound2 = wave.open("audio/C_90_pattern_1.wav", 'rb')
sound3 = wave.open("audio/C_90_pattern_2.wav", 'rb')

sounds = [sound1, sound2, sound3]

data = [sound.readframes(sound.getnframes()) for sound in sounds]
decodedData = [numpy.fromstring(d, numpy.int16) for d in data]

combined_data = numpy.append(decodedData[1], decodedData[2])
combined_data = numpy.append(combined_data, combined_data)

print(len(decodedData[0]))
print(len(decodedData[1]))
print(len(combined_data))

# mix as much as possible
n = min(map(len, [decodedData[0], combined_data]))
# mix by taking the mean of the two audio samples
mix = (decodedData[0][:n] * 0.5 + combined_data[:n] * 0.5).astype(numpy.int16)
print(len(mix))

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(sound1.getsampwidth()),
                channels=sound1.getnchannels(),
                rate=sound1.getframerate(),
                output=True)

# play stream (3)
stream.write(mix.tostring())

# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()
