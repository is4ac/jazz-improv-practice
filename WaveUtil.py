import numpy


class WaveUtil:
    def __init__(self, data=None, total_frames=3763200, loop=True):
        if data is None:
            self.data = []
        else:
            self.data = [data] # store in an array so we can concatenate tracks later

        self.loop = loop
        self.total_frames = total_frames # default value is 16 measures in 44,100 Hz
        self.current_frame = 0
        self.joined_data = self.joinData()

    def joinData(self):
        new_data = numpy.zeros(self.total_frames, dtype=numpy.int16)

        frame = 0
        for index in range(len(self.data)):
            # copy each track into the new concatenated array
            new_data[frame:frame+len(self.data[index])] = self.data[index]

            # update the frame index
            frame += len(self.data[index])

        return new_data

    def readframes(self, frames):
        index = self.current_frame
        stereoFrames = frames * 2 # double the amount of data because it is in stereo
        self.current_frame += stereoFrames

        return_data = self.joined_data[index:index+stereoFrames]

        # loop the data back to the beginning if looping feature is on
        if self.loop:
            if self.current_frame >= self.total_frames:
                self.current_frame %= self.total_frames
                return_data = numpy.append(return_data, self.joined_data[0:self.current_frame])

        return return_data

    def addTrack(self, data):
        self.data.append(data)
        self.joined_data = self.joinData()

    def updateTrack(self, data, track_num):
        if track_num >= len(self.data) or track_num < 0:
            raise Exception("Track number is out of range.")

        self.data[track_num] = data
        self.joined_data = self.joinData()

    def updateTotalFrames(self, total_frames):
        self.total_frames = total_frames

    def setCurrentFrame(self, frame):
        self.current_frame = frame

    def clearTracks(self):
        self.data = []
        self.joined_data = self.joinData()
