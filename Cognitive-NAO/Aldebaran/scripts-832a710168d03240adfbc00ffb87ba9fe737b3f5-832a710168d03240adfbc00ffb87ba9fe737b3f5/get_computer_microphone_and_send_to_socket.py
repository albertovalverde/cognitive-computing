# Echo client program
import socket
import struct

class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024, input_device_index=None):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.input_device = input_device_index
        self.wavebuffer=[]
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        input_device_index=self.input_device,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer,self.input_device)

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavebuffer.append(in_data)
            return in_data, pyaudio.paContinue
        return callback

class Recorder(object):
    def __init__(self, fname, mode, channels,
                rate, frames_per_buffer,input_device_index):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.input_device=input_device_index
        # self._pa = pyaudio.PyAudio()
        # self._pa=p
        # self.wavefile = self._prepare_file(self.fname, self.mode)
        # self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        input_device_index=self.input_device)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        # self._stream = self._pa.open(format=pyaudio.paInt16,
        #                                 channels=self.channels,
        #                                 rate=self.rate,
        #                                 input=True,
        #                                 frames_per_buffer=self.frames_per_buffer,
        #                                 input_device_index=self.input_device,
        #                                 stream_callback=self.get_callback())
        # self._stream.start_stream()
        # stream.start_stream()
        return self

    def set_new_file(self,fname,mode):
        # self.wavefile.close()
        # self.wavefile = self._prepare_file(fname, mode)
        self.fname=fname
        return self

    # def stop_recording(self):
        # self._stream.stop_stream()
        # stream.stop_stream()

        # return self.wavebuffer

    # def get_callback(self):
    #     def callback(in_data, frame_count, time_info, status):
    #         self.wavefile.writeframes(in_data)
    #         return in_data, pyaudio.paContinue
    #     return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

    

def sendFile( strHost, nPortNumber, strFilename, bPrefixDataWithSize = True, bRemoveWavHeader =  False, bWaitForAnswer = False, bSendEmptyBuffer = False ):
    """
    Send file over network
    Return: 1 if ok or 0 on error
    """
    print( "INF: sending data to %s:%s" % (strHost,nPortNumber) )
    data = getBuffer( strFilename )
    if( data == None ):
        return 0        
        
    print( "INF: data size: %s" % len(data) )
    
    if( bRemoveWavHeader ):
        data = data[44:]
        print( "INF: data size after remove wav header: %s" % len(data) )
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((strHost, nPortNumber))
    
    if( bPrefixDataWithSize ):
        data = struct.pack('>I', len(data)) + data
    s.sendall( data ) # prefix with a 4 bytes network ordered containing the size
    print( "GOOD: everything has been sent..." )
    if( bSendEmptyBuffer ):
        chZero = struct.pack('>I', 0 )
        sZero = chZero*1024*100
        s.sendall( sZero )
        print( "GOOD: Zeroes has been sent also..." )
    if( bWaitForAnswer ):
        data = s.recv(1024)
    s.close()
    #print 'answer: ', repr(data)
    return 1
# sendFile - end
    
strIP = "192.168.1.36"
#~ strIP = "192.168.2.104"
strFile = "/tmp/input.wav"
strFile = "/tmp2/nimoy_spock.wav"
strFile = "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_data/sounds/test/nao_mic_no_song__speaks.wav"
strFile = "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_data/sounds/test/texts/fr/alexandre_clean__la_salle_de_kine.wav"
#~ strFile = "/home/likewise-open/ALDEBARAN/amazel/worksound/HelloHowAreYou32b.wav"
#~ strFile = "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_shared/scripts/python/speech_recognition_server.py"
bPrefixDataWithSize = 0
bRemoveWavHeader = 1
bSendEmptyBuffer=1
sendFile( strIP, 50007, strFile, bPrefixDataWithSize = bPrefixDataWithSize, bRemoveWavHeader = bRemoveWavHeader, bSendEmptyBuffer = bSendEmptyBuffer )