from os import times
import azure.cognitiveservices.speech as speechsdk
from continous import speech_language_detection_once_from_continuous 

# Microsoft recommendation is to use https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/batch-transcription

done = False
speech_recognizer: any;

def from_file():
    speech_config = speechsdk.SpeechConfig(subscription="", region="eastus")
    audio_input = speechsdk.AudioConfig(filename="english.wav")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    # speech_config.speech_recognition_language="ar-AE"
    print ('==> starting')
    with open('transcript-english1.txt', "w") as txtFile:
        while not done:
            result = speech_recognizer.recognize_once_async().get()
            if result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized: {}".format(result.no_match_details))
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                break
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
                    break
            txtFile.write (result.text)
            print(result.text)
        print ('-- DONE --')
        
def stop_cb(evt):
    print('CLOSING on {}'.format(evt))
    speech_recognizer.stop_continuous_recognition()
    done = True


# from_file()  - uncomment to do a one time speech recognition from a file - didn't work with english.wav

speech_language_detection_once_from_continuous()