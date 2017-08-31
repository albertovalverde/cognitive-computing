from ws4py.client.threadedclient import WebSocketClient
import base64, json, ssl, subprocess, threading, time

class SpeechToTextClient(WebSocketClient):
    def __init__(self):
        ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"

        username = "0c5d1d35-0a77-45b9-a7f7-c10e61c9f183"
        password = "GXYkve2EXApL"
        auth_string = "%s:%s" % (username, password)
        base64string = base64.encodestring(auth_string).replace("\n", "")

        self.listening = False

        try:
            WebSocketClient.__init__(self, ws_url,
                headers=[("Authorization", "Basic %s" % base64string)])
            self.connect()
        except: print "Failed to open WebSocket."

    def opened(self):
        self.send('{"action": "start", "content-type": "audio/l16;rate=16000"}')
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()

    def received_message(self, message):
        message = json.loads(str(message))
        if "state" in message:
            if message["state"] == "listening":
                self.listening = True
        print "Message received: " + str(message)

    def stream_audio(self):
        while not self.listening:
            time.sleep(0.1)

        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
        print reccmd
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)

        while self.listening:
            data = p.stdout.read(1024)

            try: self.send(bytearray(data), binary=True)
            except ssl.SSLError: pass

        p.kill()

    def close(self):
        self.listening = False
        self.stream_audio_thread.join()
        WebSocketClient.close(self)

try:
    stt_client = SpeechToTextClient()
    raw_input()
finally:
    stt_client.close()