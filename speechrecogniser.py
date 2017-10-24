import speech_recognition as sr
from speech_recognition import * 
from os import path

# import from user-defined class
from credentials import APICredentials

# variables_list is list of string of variables
# input_user: 1 for Google, 2 for Google Cloud
# input_method: 1 for voice, 2 for audio file
def get_voice_input(variables_list, input_user, input_method):
        enableGoogle = False
        enableGoogleCloud = False # free 60 mins, $0.006 per 15 seconds thereafter
        enableMicrosoftBing = False # free 5000 transactions, $4 per 1000 transactions thereafter

        # process the API to be used based on user input
        try:
                input_user = int(input_user)
        except ValueError:
                print "Error: input_user is not a number"
                return None
                
        if (input_user == 1):
                enableGoogle = True
        elif (input_user == 2):
                enableGoogleCloud = True 
        else:
                print "Error: input_user is not 1 nor 2"
                return None # terminate the program
                                                                      
        r = sr.Recognizer()

        try:
                input_method = int(input_method)
        except ValueError:
                print "Error: input_method is not a number"
                return None # terminate the program
                
        if (input_method == 1):
                # record from voice
                audio = read_from_microphone(r)
        elif (input_method == 2):
                # read from audio file
                audio = read_from_audio_file(r)
        else:
                print "Error: input_method is not 1 nor 2"
                return None # terminate the program

        print "Analyzing..."


        # Recognize the speech         
        try:
                if (enableGoogle):
                        # recognize speech using Google Speech Recognition
                        read_words = r.recognize_google(audio)
                        print("Google finished deciphering ! \n")
                        return read_words

                if (enableGoogleCloud):
                        # recognize speech using Google Cloud Speech Recognition
                        credential_object = APICredentials()
                        google_cloud_json = credential_object.get_google_json_file()
                        preferred_phrases = ["equal", "if", "then", "else", "end", "declare integer", "integer", "boolean", \
                                             "declare boolean", "declare string", "declare float", "declare double", "declare character", \
                                             "string", "float", "double", "character", "size", "index", "create function", \
                                             "function", "return", "return type", "parameter", "call function", "for", "plus", "plus plus", \
                                             "minus", "minus minus", "times", "divide", "while", "switch", "case", "dot", "end if", \
                                             "end switch", "end declare", "for loop", "end equal", "for loop condition i", "end while"]
                        preferred_phrases += variables_list
                        
                        read_words_google = RecognizerGA().recognize_google_cloud(audio, google_cloud_json, "en-US", preferred_phrases, False)
                        print("Google Cloud finished deciphering ! \n")
                        return read_words_google

                if (enableMicrosoftBing):
                        # recognize speech using Microsoft Bing Speech Recognition
                        credential_object = APICredentials()
                        bing_key = credential_object.get_bing_key()

                        read_words_bing = r.recognize_bing(audio, bing_key, "en-US", False)
                        print("Microsoft Bing : " + read_words_bing + "\n\n")               

        except sr.UnknownValueError:
                print("Could not understand audio")
        except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

def read_from_microphone(r):
        print "Reading from microphone selected! \n"
        print "Adjusting for environment ambient noise ... \n"
        with sr.Microphone() as source: r.adjust_for_ambient_noise(source)

        print("Minimum energy threshold to {}".format(r.energy_threshold))

        with sr.Microphone() as source:                                                                       
                print("You can start speaking now:")                                                                                   
                audio = r.listen(source)
                return audio


def read_from_audio_file(r):
        print "Reading from audio file selected! \n"
        input_filename = raw_input('Please enter the filename (Work\\...\\filenamewithoutwav) : \n')
        
        print "Reading from audio file..."
        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "TestSamples\\" + input_filename + ".wav")

        with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source)  # read the entire audio file
                return audio


# This inherits the parent Recognizer class so we can override its functions
class RecognizerGA( Recognizer ):
        # this is needed because of google cloud speech migration to GA
        def recognize_google_cloud(self, audio_data, credentials_json=None, language="en-US", preferred_phrases=None, show_all=False):
                """
                Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Cloud Speech API.
                This function requires a Google Cloud Platform account; see the `Google Cloud Speech API Quickstart <https://cloud.google.com/speech/docs/getting-started>`__ for details and instructions. Basically, create a project, enable billing for the project, enable the Google Cloud Speech API for the project, and set up Service Account Key credentials for the project. The result is a JSON file containing the API credentials. The text content of this JSON file is specified by ``credentials_json``. If not specified, the library will try to automatically `find the default API credentials JSON file <https://developers.google.com/identity/protocols/application-default-credentials>`__.
                The recognition language is determined by ``language``, which is a BCP-47 language tag like ``"en-US"`` (US English). A list of supported language tags can be found in the `Google Cloud Speech API documentation <https://cloud.google.com/speech/docs/languages>`__.
                If ``preferred_phrases`` is a list of phrase strings, those given phrases will be more likely to be recognized over similar-sounding alternatives. This is useful for things like keyword/command recognition or adding new phrases that aren't in Google's vocabulary. Note that the API imposes certain `restrictions on the list of phrase strings <https://cloud.google.com/speech/limits#content>`__.
                Returns the most likely transcription if ``show_all`` is False (the default). Otherwise, returns the raw API response as a JSON dictionary.
                Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the credentials aren't valid, or if there is no Internet connection.
                """
                
                assert isinstance(audio_data, AudioData), "``audio_data`` must be audio data"
                if credentials_json is not None:
                    try: json.loads(credentials_json)
                    except: raise AssertionError("``credentials_json`` must be ``None`` or a valid JSON string")
                assert isinstance(language, str), "``language`` must be a string"
                assert preferred_phrases is None or all(isinstance(preferred_phrases, (type(""), type(u""))) for preferred_phrases in preferred_phrases), "``preferred_phrases`` must be a list of strings"

                # See https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionConfig
                flac_data = audio_data.get_flac_data(
                    convert_rate=None if 8000 <= audio_data.sample_rate <= 48000 else max(8000, min(audio_data.sample_rate, 48000)),  # audio sample rate must be between 8 kHz and 48 kHz inclusive - clamp sample rate into this range
                    convert_width=2  # audio samples must be 16-bit
                )

                try:
                    from oauth2client.client import GoogleCredentials
                    from googleapiclient.discovery import build
                    import googleapiclient.errors

                    # cannot simply use 'http = httplib2.Http(timeout=self.operation_timeout)'
                    # because discovery.build() says 'Arguments http and credentials are mutually exclusive'
                    import socket
                    import googleapiclient.http
                    if self.operation_timeout and socket.getdefaulttimeout() is None:
                        # override constant (used by googleapiclient.http.build_http())
                        googleapiclient.http.DEFAULT_HTTP_TIMEOUT_SEC = self.operation_timeout

                    if credentials_json is None:
                        api_credentials = GoogleCredentials.get_application_default()
                    else:
                        # the credentials can only be read from a file, so we'll make a temp file and write in the contents to work around that
                        with PortableNamedTemporaryFile("w") as f:
                            f.write(credentials_json)
                            f.flush()
                            api_credentials = GoogleCredentials.from_stream(f.name)

                    speech_service = build("speech", "v1", credentials=api_credentials, cache_discovery=False)
                except ImportError:
                    raise RequestError("missing google-api-python-client module: ensure that google-api-python-client is set up correctly.")

                if preferred_phrases is None:
                    speech_config = {"encoding": "FLAC", "sampleRateHertz": audio_data.sample_rate, "languageCode": language}
                else:
                    speech_config = {"encoding": "FLAC", "sampleRateHertz": audio_data.sample_rate, "languageCode": language, "speechContexts": {"phrases": preferred_phrases}}
                request = speech_service.speech().recognize(body={"audio": {"content": base64.b64encode(flac_data).decode("utf8")}, "config": speech_config})

                try:
                    response = request.execute()
                except googleapiclient.errors.HttpError as e:
                    raise RequestError(e)
                except URLError as e:
                    raise RequestError("recognition connection failed: {0}".format(e.reason))

                if show_all: return response
                if "results" not in response or len(response["results"]) == 0: raise UnknownValueError()
                transcript = ""
                for result in response["results"]:
                    transcript += result["alternatives"][0]["transcript"].strip() + " "

                return transcript

