import pyaudio
import wave
import webrtcvad
from google.cloud import speech

def record_and_save_user_voice():
    # Parameters for audio recording
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK_DURATION_MS = 30
    CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)  # Number of frames per buffer
    SILENCE_THRESHOLD = 100  # Adjust for sensitivity
    RECORDING_TIME = 10  # Recording duration in seconds

    # Initialize audio recording
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    # Initialize VAD
    vad = webrtcvad.Vad()
    vad.set_mode(3)  # Aggressive mode for voice activity detection

    print("Recording...")

    frames = []
    silence_frames = 0
    silent = True

    while len(frames) * CHUNK_DURATION_MS < RECORDING_TIME * 1000:
        data = stream.read(CHUNK_SIZE)
        
        if vad.is_speech(data, RATE):
            silent = False
            silence_frames = 0
            frames.append(data)
        else:
            silence_frames += 1
            if not silent and silence_frames * CHUNK_DURATION_MS >= 500:  # Silence threshold
                break

    print("Recording finished.")

    # Clean up audio recording
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Convert audio data to a format suitable for saving
    audio_data = b''.join(frames)

    # Save audio as a WAV file
    wav_file_path = r"speech/user_speech_file.wav"
    with wave.open(wav_file_path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(audio_data)

    print("captured voice successfully")

# Transcribe the recorded audio using the transcribe_audio function
def convert_user_voice_to_text(mp3_file_path):
    client = speech.SpeechClient.from_service_account_file(r'keys/myproject-google-key.json')

    with open(mp3_file_path, 'rb') as f:
        mp3_data = f.read()

    audio_file = speech.RecognitionAudio(content=mp3_data)

    configuration = speech.RecognitionConfig(
        sample_rate_hertz=16000,
        enable_automatic_punctuation=True,
        language_code='en-US'
    )

    response = client.recognize(
        config=configuration,
        audio=audio_file
    )

    transcribed_text = ""
    for result in response.results:
        transcribed_text += result.alternatives[0].transcript + " "

    return transcribed_text.strip()

# Call the transcribe_audio function with the recorded WAV file
record_and_save_user_voice()
user_voice_path = r"speech/user_speech_file.wav"
voice_to_text_output = convert_user_voice_to_text(user_voice_path)
print("Transcription:", voice_to_text_output)
