#!/usr/bin/python
#coding:utf-8
#~ NAO_IP = "10.0.253.99" # Nao Alex Blue


# install modules in python
# pip isntall google.auth
# pip install numpy
# pip install grpc-google-cloud-speech-v1beta1
# pip install ansible


from __future__ import division

from optparse import OptionParser
import naoqi
import numpy as np
import time
import sys
import random
from naoqi import ALProxy, ALBroker, ALModule


import contextlib
import functools
import re
import signal
import sys
import urllib
import urllib2
import threading
import wave


import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
from google.cloud.speech.v1beta1 import cloud_speech_pb2
from google.rpc import code_pb2
import grpc
import pyaudio
from six.moves import queue


# Audio recording parameters
NAO_IP = "192.168.1.33" # Romeo on table
RATE = 48000
CHUNK = int(RATE / 10)  # 100ms

SERVER_MODE = 1
WAKE_UP = 0
SPEECH_DICT = {}
SPEECH_DICT['S1']="^start(animations/Sit/BodyTalk/BodyTalk_1)让我来吧！我们现在有请陈繁昌校长主持论坛。论坛主题是香港如何跑赢智能的未来。我们的嘉宾包括 港科大计算机科学及工程系主任－杨强教授，香港X科技创业平台联合创办人－李泽湘教授，科大讯飞轮值总裁及联合创办人－胡郁博士，红杉资本中国基金合伙人计越先生和港科大学生创业代表 Mind Vivid 营运总监 卢慧德小姐 上台。"
SPEECH_DICT['S2']="你好"
SPEECH_DICT['S3']="^start(animations/Sit/BodyTalk/BodyTalk_3)你好"
SPEECH_DICT['S4']="^start(animations/Sit/BodyTalk/BodyTalk_4)你好"
SPEECH_DICT['S5']="^startTag(body language)你好"
SPEECH_DICT['S6']="^startTag(body language)你好"
SPEECH_DICT['T0']="^startTag(body language)欢迎光临"
SPEECH_DICT['T1']="^startTag(body language)请问你想喝什么？"
SPEECH_DICT['T2']="^startTag(body language)拿铁，请问你要中杯，大杯还是超大杯？冰的还是热的？"
SPEECH_DICT['T3']="^startTag(body language)冰的还是热的？送到哪里？"
SPEECH_DICT['T4']="^startTag(body language)中杯热拿铁，送到哪里？"
SPEECH_DICT['T5']="^startTag(body language)好的，您的中杯热拿铁送到香港科技大学下单成功"
SPEECH_DICT['T6']="^startTag(body language)微信支付哈"
SPEECH_DICT['T7']="^startTag(body language)好的呢"
SPEECH_DICT['T8']="^startTag(body language)欢迎下次光临"
SPEECH_DICT['TE']="^startTag(body language)哎哟，我出错了。请您再说一遍。"

# The Speech API has a streaming limit of 60 seconds of audio*, so keep the
# connection alive for that long, plus some more to give the API time to figure
# out the transcription.
# * https://g.co/cloud/speech/limits#content
DEADLINE_SECS = 60 * 3 + 5
SPEECH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'
BASE_URL = 'http://qycpu6.cse.ust.hk:8080/mobile/dialogue'

_audio_buffer = queue.Queue()

class TTSEventWatcher(ALModule):
	""" An ALModule to react to the ALTextToSpeech/Status event """

	def __init__(self, ip_robot, port_robot):
		super(TTSEventWatcher, self).__init__("tts_event_watcher")
		global memory
		global tts_event_watcher
		memory = ALProxy("ALMemory", ip_robot, port_robot)
		self.tts = ALProxy("ALAnimatedSpeech", ip_robot, port_robot)
		self.asr = ALProxy('ALSpeechRecognition',ip_robot,port_robot)
		self.asr.setLanguage("Chinese")
		# self.audio = ALProxy("ALAudioDevice",ip_robot,port_robot)
		self.record = ALProxy("ALAudioRecorder",ip_robot,port_robot)
		# self.aup = ALProxy("ALAudioPlayer",ip_robot,port_robot)
		self.record_path = '/home/nao/record.wav'

			# memory.raiseEvent("ALSpeechRecognition/Status","ListenOn")


	def on_tts_status(self, key, value, message):
		""" callback for event ALStatus """
		print "TTS Status value:", value


	def shutdown(self):
		self.shutdown_value = 1


def make_channel(host, port):
	"""Creates a secure channel with auth credentials from the environment."""
	# Grab application default credentials from the environment
	credentials, _ = google.auth.default(scopes=[SPEECH_SCOPE])

	# Create a secure channel using the credentials.
	http_request = google.auth.transport.requests.Request()
	target = '{}:{}'.format(host, port)

	return google.auth.transport.grpc.secure_authorized_channel(
		credentials, http_request, target)


def _audio_data_generator(buff):
	"""A generator that yields all available data in the given buffer.

	Args:
		buff - a Queue object, where each element is a chunk of data.
	Yields:
		A chunk of data that is the aggregate of all chunks of data in `buff`.
		The function will block until at least one data chunk is available.
	"""
	stop = False
	while not stop:
		# Use a blocking get() to ensure there's at least one chunk of data.
		data = [buff.get()]
		# Now consume whatever other data's still buffered.
		while True:
			try:
				data.append(buff.get(block=False))
			except queue.Empty:
				break

		# `None` in the buffer signals that the audio stream is closed. Yield
		# the final bit of the buffer and exit the loop.
		if None in data:
			stop = True
			data.remove(None)

		yield b''.join(data)


def _fill_buffer(buff, in_data, frame_count, time_info, status_flags):
	"""Continuously collect data from the audio stream, into the buffer."""
	global _audio_buffer
	buff.put(in_data)
	_audio_buffer.put(in_data)
	#print("fill")
	return None, pyaudio.paContinue


# [START audio_stream]
@contextlib.contextmanager
def record_audio(rate, chunk):
	"""Opens a recording stream in a context manager."""
	# Create a thread-safe buffer of audio data
	buff = queue.Queue()
	#print("record")
	audio_interface = pyaudio.PyAudio()
	audio_stream = audio_interface.open(
		format=pyaudio.paInt16,
		# The API currently only supports 1-channel (mono) audio
		# https://goo.gl/z757pE
		channels=1, rate=rate,
		input=True, frames_per_buffer=chunk,
		# Run the audio stream asynchronously to fill the buffer object.
		# This is necessary so that the input device's buffer doesn't overflow
		# while the calling thread makes network requests, etc.
		stream_callback=functools.partial(_fill_buffer, buff),
	)

	yield _audio_data_generator(buff)

	audio_stream.stop_stream()
	audio_stream.close()
	# Signal the _audio_data_generator to finish
	buff.put(None)
	print("End")
	audio_interface.terminate()
# [END audio_stream]


def request_stream(data_stream, rate, interim_results=True):
	"""Yields `StreamingRecognizeRequest`s constructed from a recording audio
	stream.

	Args:
		data_stream: A generator that yields raw audio data to send.
		rate: The sampling rate in hertz.
		interim_results: Whether to return intermediate results, before the
			transcription is finalized.
	"""
	# The initial request must contain metadata about the stream, so the
	# server knows how to interpret it.
	print("request_stream")
	recognition_config = cloud_speech_pb2.RecognitionConfig(
		# There are a bunch of config options you can specify. See
		# https://goo.gl/KPZn97 for the full list.
		encoding='LINEAR16',  # raw 16-bit signed LE samples
		sample_rate=rate,  # the rate in hertz
		# See http://g.co/cloud/speech/docs/languages
		# for a list of supported languages.
		language_code='zh-CN',  # a BCP-47 language tag
	)
	streaming_config = cloud_speech_pb2.StreamingRecognitionConfig(
		interim_results=interim_results,
		config=recognition_config,
	)

	yield cloud_speech_pb2.StreamingRecognizeRequest(
		streaming_config=streaming_config)

	for data in data_stream:
		# Subsequent requests can all just have the content
		#print(len(data))
		yield cloud_speech_pb2.StreamingRecognizeRequest(audio_content=data)

def getRes(text):
	global WAKE_UP
	if WAKE_UP == 0:
		if text == u'你好' or text == u"您好":
			url = BASE_URL+"_RESET"
			req = urllib2.Request(url.encode('utf-8'))
			res_data = urllib2.urlopen(req)
			res = res_data.read()
			time.sleep(0.5)
			print res
			url = BASE_URL+"_RESETUSER"
			req = urllib2.Request(url.encode('utf-8'))
			res_data = urllib2.urlopen(req)
			res = res_data.read()
			time.sleep(0.5)
			print res
			tts_event_watcher.tts.say("欢迎光临")
			WAKE_UP = 1
	else:
		if text == u'谢谢':
			tts_event_watcher.tts.say("欢迎下次光临")
			WAKE_UP = 0
		else:
			url = BASE_URL+"_"+text
			print(text)
			req = urllib2.Request(url.encode('utf-8'))
			res_data = urllib2.urlopen(req)
			res = res_data.read()
			print res
			if "Error" in res:
				print("error")
				res = ""
			if "num" in res:
				if "num个小时内送到" in res:
					res = res.replace("num个小时内送到","")
				print("in")
				price = random.randint(0,10)+30
				res = res.replace("num",str(price))
			tts_event_watcher.tts.say(res)
			


def listen_print_loop(recognize_stream):
	"""Iterates through server responses and prints them.

	The recognize_stream passed is a generator that will block until a response
	is provided by the server. When the transcription response comes, print it.

	In this case, responses are provided for interim results as well. If the
	response is an interim one, print a line feed at the end of it, to allow
	the next result to overwrite it, until the response is a final one. For the
	final one, print a newline to preserve the finalized transcription.
	"""
	num_chars_printed = 0
	for resp in recognize_stream:
		if SERVER_MODE != 1:
			return 0
		if resp.error.code != code_pb2.OK:
			#raise RuntimeError('Server error: ' + resp.error.message)
			print('Server error: ' + resp.error.message)
			return 

		if not resp.results:
			continue

		# Display the top transcription
		result = resp.results[0]
		print(result)
		transcript = result.alternatives[0].transcript

		# Display interim results, but with a carriage return at the end of the
		# line, so subsequent lines will overwrite them.
		#
		# If the previous result was longer than this one, we need to print
		# some extra spaces to overwrite the previous result
		overwrite_chars = ' ' * max(0, num_chars_printed - len(transcript))

		if result.is_final or result.stability>0.5:
			print("Answer:")
			getRes(transcript)
			return 0

		if not result.is_final:
			sys.stdout.write(transcript + overwrite_chars + '\r')
			sys.stdout.flush()

			num_chars_printed = len(transcript)

		else:
			print(transcript + overwrite_chars)

			# Exit recognition if any of the transcribed phrases could be
			# one of our keywords.
			if re.search(r'\b(exit|quit)\b', transcript, re.I):
				print('Exiting..')
				break

			num_chars_printed = 0


class SoundReceiverModule(naoqi.ALModule):
	"""
	Use this object to get call back from the ALMemory of the naoqi world.
	Your callback needs to be a method with two parameter (variable name, value).
	"""

	def __init__( self, strModuleName, strNaoIp ):
		try:
			naoqi.ALModule.__init__(self, strModuleName );
			self.BIND_PYTHON( self.getName(),"callback" );
			self.strNaoIp = strNaoIp;
			self.outfile = open('/Users/liuw/Downloads/python-docs-samples-master/speech/grpc/out.raw','ab+');
			self.aOutfile = [None]*(4-1); # ASSUME max nbr channels = 4
		except BaseException, err:
			print( "ERR: abcdk.naoqitools.SoundReceiverModule: loading error: %s" % str(err) );

	# __init__ - end
	def __del__( self ):
		print( "INF: abcdk.SoundReceiverModule.__del__: cleaning everything" );
		self.stop();

	def start( self ):
		audio = naoqi.ALProxy( "ALAudioDevice", self.strNaoIp, 9559 );
		nNbrChannelFlag = 3; # ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
		nDeinterleave = 0;
		nSampleRate = 48000;
		audio.setClientPreferences( self.getName(),  nSampleRate, nNbrChannelFlag, nDeinterleave ); # setting same as default generate a bug !?!
		audio.subscribe( self.getName() );
		#print( "INF: SoundReceiver: started!" );
		# self.processRemote( 4, 128, [18,0], "A"*128*4*2 ); # for local test

		# on romeo, here's the current order:
		# 0: right;  1: rear;   2: left;   3: front,  

	def stop( self ):
		print( "INF: SoundReceiver: stopping..." );
		audio = naoqi.ALProxy( "ALAudioDevice", self.strNaoIp, 9559 );
		audio.unsubscribe( self.getName() );        
		print( "INF: SoundReceiver: stopped!" );
		if( self.outfile != None ):
			self.outfile.close();

	#def process( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer ):
	#	print("OK")

	def processRemote( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer ):
		"""
		This is THE method that receives all the sound buffers from the "ALAudioDevice" module
		"""
		global _audio_buffer
		_audio_buffer.put(buffer)
		wf.writeframes("".join(buffer))

		#audio.subscribe( self.getName() ); 
		#_audio_buffer = []
		#print(aTimeStamp)
		#print( "process!" );
		#print( "processRemote: %s, %s, %s, lendata: %s, data0: %s (0x%x), data1: %s (0x%x)" % (nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, len(buffer), buffer[0],ord(buffer[0]),buffer[1],ord(buffer[1])) );
		#print( "raw data: " ),
		#for i in range( 8 ):
		#    print( "%s (0x%x), " % (buffer[i],ord(buffer[i])) ),
		#print( "" );
		#print(buffer)
		#aSoundDataInterlaced = np.fromstring( str(buffer), dtype=np.short );
		#print(aSoundDataInterlaced)
		#~ print( "len data: %s " % len( aSoundDataInterlaced ) );
		#~ print( "data interlaced: " ),
		#~ for i in range( 8 ):
			#~ print( "%d, " % (aSoundDataInterlaced[i]) ),
		#~ print( "" );
		#aSoundData = np.reshape( aSoundDataInterlaced, (nbOfChannels, nbrOfSamplesByChannel), 'F' );
		#print( "len data: %s " % len( aSoundData ) );
		#print( "len data 0: %s " % len( aSoundData[0] ) );
		#if( False ):
			# compute average
		#    aAvgValue = np.mean( aSoundData, axis = 1 );
		#    print( "avg: %s" % aAvgValue );
		#if( False ):
			# compute fft
		#    nBlockSize = nbrOfSamplesByChannel;
		#    signal = aSoundData[0] * np.hanning( nBlockSize );
		#    aFft = ( np.fft.rfft(signal) / nBlockSize );
		 #   print aFft;
		#if( False ):
			# compute peak
		#    aPeakValue = np.max( aSoundData );
		#    if( aPeakValue > 16000 ):
		#        print( "Peak: %s" % aPeakValue );
		#if( True ):
		#    bSaveAll = True;
			# save to file
		#    if( self.outfile == None ):
		#        strFilenameOut = "/out.raw";
		#        print( "INF: Writing sound to '%s'" % strFilenameOut );
		#        self.outfile = open( strFilenameOut, "wb" );
		#        if( bSaveAll ):
		#            for nNumChannel in range( 1, nbOfChannels ):
		#                strFilenameOutChan = strFilenameOut.replace(".raw", "_%d.raw"%nNumChannel);
		#                self.aOutfile[nNumChannel-1] = open( strFilenameOutChan, "wb" );
		#                print( "INF: Writing other channel sound to '%s'" % strFilenameOutChan );

			#~ aSoundDataInterlaced.tofile( self.outfile ); # wrote the 4 channels
			#aSoundData[0].tofile( self.outfile ); # wrote only one channel
			
			#print(len(buffer))
			#self.outfile.write(buffer)
			#~ print( "aTimeStamp: %s" % aTimeStamp );
			#~ print( "data wrotten: " ),
			#~ for i in range( 8 ):
				#~ print( "%d, " % (aSoundData[0][i]) ),
			#~ print( "" );            
			#~ self.stop(); # make naoqi crashes
		#    if( bSaveAll ):
		#        for nNumChannel in range( 1, nbOfChannels ):
		#            aSoundData[nNumChannel].tofile( self.aOutfile[nNumChannel-1] ); 


	# processRemote - end


	def version( self ):
		return "0.6";

# SoundReceiver - end

def getAudioStream(service):
	global _audio_buffer
	print("getAudioStream")
	count = 0
	try:
		while True:
			SoundReceiver.start()
			time.sleep(0.17)
			#SoundReceiver.stop()
	except KeyboardInterrupt:
		print "Interrupted by user, shutting down"
		myBroker.shutdown()
		sys.exit(0)
		#with record_audio(RATE,CHUNK) as buff:
		 #   for data in buff:
		   #     count+=1
				#print("test")

def getInputMode(service):
	global SERVER_MODE
	global WAKE_UP
	global _audio_buffer
	while True:
		if SERVER_MODE == 1:
			mode_text = raw_input("")
			if mode_text == "M2":
				SERVER_MODE = 2
				print("Change Server Mode to MODE 2")
		if SERVER_MODE == 2:
			print("Mode 2:")
			speech_text = raw_input("请输入台词（预设台词请直接输入S+数字）：")
			if speech_text == "M1":
				SERVER_MODE = 1
				_audio_buffer = queue.Queue()
				WAKE_UP = 0;
				print("Change Server Mode to MODE 1")
			else:
				if speech_text in SPEECH_DICT.keys():
					tts_event_watcher.tts.say(SPEECH_DICT[speech_text])
				else:
					tts_event_watcher.tts.say(speech_text)


def main():
	""" Main entry point

	"""
	global wf
	global SERVER_MODE
	global _audio_buffer
	wf = wave.open("test.wav", 'wb') 
	wf.setnchannels(1) 
	wf.setsampwidth(2) 
	wf.setframerate(RATE) 
	
	
	parser = OptionParser()
	parser.add_option("--pip",
		help="Parent broker port. The IP address or your robot",
		dest="pip")
	parser.add_option("--pport",
		help="Parent broker port. The port NAOqi is listening to",
		dest="pport",
		type="int")
	parser.set_defaults(
		pip=NAO_IP,
		pport=9559)

	(opts, args_) = parser.parse_args()
	pip   = opts.pip
	pport = opts.pport

	# We need this broker to be able to construct
	# NAOqi modules and subscribe to other modules
	# The broker must stay alive until the program exists
	myBroker = naoqi.ALBroker("myBroker",
	   "0.0.0.0",   # listen to anyone
	   0,           # find a free port and use it
	   pip,         # parent broker IP
	   pport)       # parent broker port


	# Warning: SoundReceiver must be a global variable
	# The name given to the constructor must be the name of the
	# variable
	global SoundReceiver
	SoundReceiver = SoundReceiverModule("SoundReceiver", pip)
	
	SoundReceiver.start()

	service = cloud_speech_pb2.SpeechStub(
		make_channel('speech.googleapis.com', 443))

	request_thread=threading.Thread(target=getAudioStream, args=(service,))
	request_thread.setDaemon(True)
	request_thread.start()
	mode_thread=threading.Thread(target=getInputMode, args=(service,))
	mode_thread.setDaemon(True)
	mode_thread.start()
	global tts_event_watcher
	tts_event_watcher = TTSEventWatcher(pip, pport)
	#print("你好")
	# For streaming audio from the microphone, there are three threads.
	# First, a thread that collects audio data as it comes in
	try:
		while True:
			if SERVER_MODE == 1:
				print(SERVER_MODE)
				request_data = _audio_data_generator(_audio_buffer)
				requests = request_stream(request_data, RATE)
				recognize_stream = service.StreamingRecognize(
						requests, DEADLINE_SECS)

				signal.signal(signal.SIGINT, lambda *_: recognize_stream.cancel())

					# Now, put the transcription responses to use.
				try:
					listen_print_loop(recognize_stream)

					recognize_stream.cancel()
				except grpc.RpcError as e:
					code = e.code()
					print("Error")
					myBroker.shutdown()
					tts_event_watcher.shutdown()
					wf.close()
					sys.exit(0)
					# CANCELLED is caused by the interrupt handler, which is expected.
					if code is not code.CANCELLED:
						raise
				

	except KeyboardInterrupt:
		print "Interrupted by user, shutting down"
		myBroker.shutdown()
		sys.exit(0)
	
			




if __name__ == "__main__":
	main()