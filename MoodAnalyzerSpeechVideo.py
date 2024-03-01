import speech_recognition as sr
from textblob import TextBlob
import cv2
from deepface import DeepFace
import time
import pyttsx3

engine = pyttsx3.init()

print("System started. Waiting for you to speak...")
def speak(text):
    engine.say(text)
    engine.runAndWait()
# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Response dictionary based on mood
responses = {
    'positive': "It's great to see you happy!",
    'negative': "I'm here to help you. Tell me more.",
    'neutral': "I see. Please continue.",
}

# Function to analyze mood from text using TextBlob
def analyze_mood_from_text(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'

# Function to capture audio and analyze mood
def capture_and_analyze_audio():
    with sr.Microphone() as source:
        # Wait for a second to let the recognizer adjust the energy threshold
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Detected speech: {text}")
            return analyze_mood_from_text(text)
        except sr.UnknownValueError:
            print("I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

# Function to analyze mood from video using DeepFace
def analyze_mood_from_video(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return result['dominant_emotion']
    except Exception as e:
        print(f"Video analysis exception: {e}")
        return "neutral"

# Start video capture
cap = cv2.VideoCapture(0)

# Main loop
try:
    while True:
        # Capture video frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video.")
            break

        # Display the frame
        cv2.imshow('Video', frame)

        # Check for speech input every 10 seconds
        if time.time() % 10 < 2:  # Check for speech input in a 2-second window every 10 seconds
            text_mood = capture_and_analyze_audio()
            if text_mood:
                visual_mood = analyze_mood_from_video(frame)
                # Generate response based on mood
                response = responses.get(text_mood, "I'm not sure how you're feeling.")
                print(f"Speech Mood: {text_mood}, Visual Mood: {visual_mood}")
                print(f"Response: {response}")
                speak(response)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
