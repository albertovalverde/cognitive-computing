#!/usr/bin/env python

from naoqi import ALProxy
import env


def parse(string):
    print 'Recognized: {}'.format(string)
    tts = ALProxy("ALTextToSpeech", env.nao_ip, env.nao_port)
    #tts.say('Recognized: {}'.format(string))
    tts.say('{}'.format(string))

    return None
