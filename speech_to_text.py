import speech_recognition as sr
from typing import Optional

class SpeechToText:
    def __init__(self, google_api_key: Optional[str] = None):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.google_api_key = google_api_key
        
    def transcribe_file(self, audio_file: str, language: str = "zh-CN") -> Optional[str]:
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            if self.google_api_key:
                text = self.recognizer.recognize_google(audio, language=language, key=self.google_api_key)
            else:
                text = self.recognizer.recognize_google(audio, language=language)
            return text
        except (sr.UnknownValueError, sr.RequestError, Exception) as e:
            print(f"转录错误: {e}")
            return None
    
    def transcribe_realtime(self, microphone_index: Optional[int] = None) -> str:
        with sr.Microphone(device_index=microphone_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                if self.google_api_key:
                    return self.recognizer.recognize_google(audio, language="zh-CN", key=self.google_api_key)
                else:
                    return self.recognizer.recognize_google(audio, language="zh-CN")
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return ""
            except sr.RequestError as e:
                print(f"语音识别服务错误: {e}")
                return ""
    
    def transcribe_stream(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        try:
            audio = sr.AudioData(audio_data, sample_rate, 2)
            if self.google_api_key:
                return self.recognizer.recognize_google(audio, language="zh-CN", key=self.google_api_key)
            else:
                return self.recognizer.recognize_google(audio, language="zh-CN")
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            return None

