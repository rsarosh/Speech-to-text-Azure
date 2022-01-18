#
# You need to standardize the input audio file format to 16 bit 16kHz mono PCM codec wav file,
# as per the audio format required for Speech Service. 
# Alternatively, you can follow this (https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-use-codec-compressed-audio-input-streams?tabs=windows%2Cdebian&pivots=programming-language-python)
# I standardized the file format as a pre-processing step, 
# using ffmpeg (check cmd script below) and the code worked for me.
#
# Download ffmpeg from https://github.com/BtbN/FFmpeg-Builds/releases and keep it 
# ffmpeg folder

# FOR /F "tokens=* delims=" %A in (files.txt) 
#     DO C:\Code\python\Audio-Microsoft\ffmpeg\bin\ffmpeg.exe -i "Audio\%A" -acodec pcm_s16le -ac 1 -ar 16000 ".\Audio_out\%~nA.wav"
#
# From command line i ran the following command to convert the audio files to 16 bit 16kHz mono PCM wav file
# C:\Code\python\Audio-Microsoft>C:\Code\python\Audio-Microsoft\ffmpeg\bin\ffmpeg.exe -i "audio.wav" -acodec pcm_s16le -ac 1 -ar 16000 "audio16.wav"

from os import times
import azure.cognitiveservices.speech as speechsdk
import time
import wave
import string
import json

# Specify the AutoDetectSourceLanguageConfig, which defines the number of possible languages
# Try using en-IN model instead of en-US model for better accuracy on Indian English speech audio.

auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["hi-IN", "en-US"])

def speech_language_detection_once_from_continuous():
    """performs continuous speech language detection with input from an audio file"""
    print("Starting --> speech_language_detection_once_from_continuous")
    # <SpeechContinuousLanguageDetectionWithFile>
    speech_config = speechsdk.SpeechConfig(subscription="", region="eastus")

    # Set the Priority (default Latency, either Latency or Accuracy is accepted)
    speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceConnection_ContinuousLanguageIdPriority, value='Latency')

    audio_config = speechsdk.audio.AudioConfig(filename="english16.wav")

    source_language_recognizer = speechsdk.SourceLanguageRecognizer(speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config, audio_config=audio_config)

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    def audio_recognized(evt):
        """
        callback that catches the recognized result of audio from an event 'evt'.
        :param evt: event listened to catch recognition result.
        :return:
        """
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("RECOGNIZED: {}".format(evt.result.properties))
            if evt.result.properties.get(speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult) == None:
                print("Unable to detect any language")
            else:
                detectedSrcLang = evt.result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
                jsonResult = evt.result.properties[speechsdk.PropertyId.SpeechServiceResponse_JsonResult]
                detailResult = json.loads(jsonResult)
                startOffset = detailResult['Offset']
                duration = detailResult['Duration']
                if duration >= 0:
                    endOffset = duration + startOffset
                else:
                    endOffset = 0
                print("Detected language = " + detectedSrcLang + ", startOffset = " + str(startOffset) + " nanoseconds, endOffset = " + str(endOffset) + " nanoseconds, Duration = " + str(duration) + " nanoseconds.")
                global language_detected
                language_detected = True

    # Connect callbacks to the events fired by the speech recognizer
    source_language_recognizer.recognized.connect(audio_recognized)
    source_language_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    source_language_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    source_language_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    source_language_recognizer.session_stopped.connect(stop_cb)
    source_language_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    source_language_recognizer.start_continuous_recognition_async()
    
    while not done:
        time.sleep(.5)

    source_language_recognizer.stop_continuous_recognition()
    # </SpeechContinuousLanguageDetectionWithFile>

speech_language_detection_once_from_continuous()