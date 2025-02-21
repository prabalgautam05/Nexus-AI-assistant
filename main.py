import tkinter as tk
from tkinter import Scrollbar, Text, Entry, Button, filedialog
import google.generativeai as genai
import pyttsx3
import threading
import speech_recognition as sr
from PIL import Image, ImageTk
import config  # Ensure you have config.py with your API key
import os
import subprocess
import psutil
import webbrowser

# Configure Nexus AI
genai.configure(api_key=config.API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")

# Initialize Text-to-Speech Engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 200)  # Adjust speaking speed

# List available voices
voices = tts_engine.getProperty('voices')
for voice in voices:
    print(f"Voice: {voice.name}, ID: {voice.id}")

# Set the desired voice (example: setting the first available voice)
tts_engine.setProperty('voice', voices[0].id)  # Change index to select a different voice

# Global flag to stop speaking
stop_speaking = False

# Function to stop speaking
def stop_speech():
    global stop_speaking
    stop_speaking = True
    tts_engine.stop()  # Immediately stop speaking

def speak_text(text):
    global stop_speaking
    stop_speaking = False  # Reset flag before speaking

    def run_speech():
        if not stop_speaking:
            tts_engine.say(text)  # Speak the entire response at once
            tts_engine.runAndWait()

    speech_thread = threading.Thread(target=run_speech)
    speech_thread.start()

# Function to send a message
def send_message():
    user_text = user_input.get()
    if not user_text:
        return

    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "🧑‍💻 You: " + user_text + "\n", "user")
    chat_display.config(state=tk.DISABLED)
    user_input.delete(0, tk.END)

    # Get response from Nexus AI
    try:
        response = model.generate_content(user_text)
        bot_response = response.text
    except Exception:
        bot_response = "⚠️ Error: Unable to connect to Nexus AI."

    chat_display.config(state=tk.NORMAL)
    
    # Display Nexus's response first
    chat_display.insert(tk.END, "🤖 Nexus: " + bot_response + "\n\n", "bot")
    chat_display.config(state=tk.DISABLED)
    chat_display.yview(tk.END)  # Auto-scroll

    # Save chat history after displaying
    save_chat_history(user_text, bot_response)

    # Speak the response after displaying it
    root.after(500, lambda: speak_text(bot_response))  # Delayed execution for natural feel

    # Execute system command if recognized
    execute_system_command(user_text)

# Save chat history to a file
def save_chat_history(user_msg, bot_msg):
    with open("chat_history.txt", "a", encoding="utf-8") as file:
        file.write(f"🧑‍💻 You: {user_msg}\n")
        file.write(f"🤖 Nexus: {bot_msg}\n\n")

# Load chat history from a file
def load_chat_history():
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)  # Clear current chat
    try:
        with open("chat_history.txt", "r", encoding="utf-8") as file:
            chat_display.insert(tk.END, file.read(), "history")
    except FileNotFoundError:
        chat_display.insert(tk.END, "No previous chat history found.", "history")
    chat_display.config(state=tk.DISABLED)

# Export chat history to a chosen file
def export_chat_history():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            with open("chat_history.txt", "r", encoding="utf-8") as chat_file:
                file.write(chat_file.read())

# Clear chat display and history file
def clear_chat():
    chat_display.config(state=tk.NORMAL)
    chat_display.delete(1.0, tk.END)
    chat_display.config(state=tk.DISABLED)
    if os.path.exists("chat_history.txt"):
        os.remove("chat_history.txt")

# Exit Button (Press ESC to close)
def exit_app(event=None):
    root.quit()

# Function to open applications
def open_application(app_name):
    try:
        if app_name.lower() == "notepad":
            subprocess.Popen(["notepad.exe"])
        elif app_name.lower() == "calculator":
            subprocess.Popen(["calc.exe"])
        elif app_name.lower() == "chrome":
            subprocess.Popen(["chrome.exe"])
        else:
            speak_text("Application not recognized.")
    except Exception as e:
        speak_text(f"Error opening {app_name}: {str(e)}")

# Function to control system
def control_system(action):
    try:
        if action.lower() == "shutdown":
            os.system("shutdown /s /t 1")
        elif action.lower() == "restart":
            os.system("shutdown /r /t 1")
        elif action.lower() == "log off":
            os.system("shutdown /l")
        elif action.lower() == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        else:
            speak_text("Action not recognized.")
    except Exception as e:
        speak_text(f"Error performing {action}: {str(e)}")

# Function to fetch system information
def fetch_system_info(info_type):
    try:
        if info_type.lower() == "battery":
            battery = psutil.sensors_battery()
            speak_text(f"Battery is at {battery.percent}%")
        elif info_type.lower() == "cpu":
            cpu_usage = psutil.cpu_percent(interval=1)
            speak_text(f"CPU usage is at {cpu_usage}%")
        elif info_type.lower() == "ram":
            ram_usage = psutil.virtual_memory().percent
            speak_text(f"RAM usage is at {ram_usage}%")
        else:
            speak_text("Information type not recognized.")
    except Exception as e:
        speak_text(f"Error fetching {info_type} information: {str(e)}")

# Function to perform web search
def web_search(query):
    try:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak_text(f"Searching for {query} on the web.")
    except Exception as e:
        speak_text(f"Error performing web search: {str(e)}")

# Function to execute system commands
def execute_system_command(command):
    if "open" in command.lower():
        app_name = command.lower().replace("open ", "")
        open_application(app_name)
    elif "shutdown" in command.lower():
        control_system("shutdown")
    elif "restart" in command.lower():
        control_system("restart")
    elif "log off" in command.lower():
        control_system("log off")
    elif "lock" in command.lower():
        control_system("lock")
    elif "battery" in command.lower():
        fetch_system_info("battery")
    elif "cpu" in command.lower():
        fetch_system_info("cpu")
    elif "ram" in command.lower():
        fetch_system_info("ram")
    elif "search" in command.lower():
        query = command.lower().replace("search ", "")
        web_search(query)
    else:
        speak_text("⚠️ Command not recognized.")

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak_text("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            speak_text(f"You said: {command}")
            execute_system_command(command)
        except sr.UnknownValueError:
            speak_text("Sorry, I did not understand that.")
        except sr.RequestError:
            speak_text("Sorry, my speech service is down.")

# Function to execute selected command from dropdown
def execute_selected_command():
    global command_var
    selected_command = command_var.get()
    if selected_command:
        execute_system_command(selected_command)

# Function to show the welcome image
def show_welcome_image():
    splash = tk.Tk()
    splash.title("Welcome to Nexus AI")
    splash.geometry("600x400")  # Adjust window size
    splash.configure(bg="#1e1e1e")

    # Center the splash screen on the screen
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (600 // 2)
    y = (screen_height // 2) - (400 // 2)
    splash.geometry(f"600x400+{x}+{y}")

    # Load and display the image
    image = Image.open("nexus AI.png")
    image = image.resize((600, 400))  # Resize image to fit window
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(splash, image=photo, bg="#1e1e1e")
    label.image = photo  # Keep a reference to avoid garbage collection
    label.pack()

    # Set a delay before closing the splash window and showing the main application
    splash.after(3000, lambda: (splash.destroy(), show_main_application()))

    splash.mainloop()

# Function to show the main application
def show_main_application():
    global root
    root = tk.Tk()
    root.title("Nexus AI Chatbot with Chat History & Speech Control")
    root.configure(bg="#1e1e1e")

    # Set initial window size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width-20}x{screen_height-20}+10+10")
    root.resizable(True, True)
    root.bind("<Escape>", exit_app)

    # Chat Display
    global chat_display
    chat_display = Text(root, wrap="word", state=tk.DISABLED, bg="#2b2b2b", fg="white",
                        font=("Arial", 14), padx=20, pady=20)
    chat_display.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = Scrollbar(chat_display)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_display.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=chat_display.yview)

    # Custom styles
    chat_display.tag_config("user", foreground="#00ffcc", font=("Arial", 14, "bold"))
    chat_display.tag_config("bot", foreground="#ffcc00", font=("Arial", 14))
    chat_display.tag_config("history", foreground="#888888", font=("Arial", 12, "italic"))

    # Load previous chat history
    load_chat_history()

    # User Input Field
    global user_input
    user_input = Entry(root, font=("Arial", 16), bg="#333", fg="white", insertbackground="white")
    user_input.pack(pady=10, padx=20, fill=tk.X)
    user_input.bind("<Return>", lambda event: send_message())

    # Button Frame
    button_frame = tk.Frame(root, bg="#1e1e1e")
    button_frame.pack(pady=5)

    # Send Button
    send_button = Button(button_frame, text="⤴️Send", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                         relief="flat", command=send_message)
    send_button.grid(row=0, column=0, padx=2)

    # Load Chat Button
    load_button = Button(button_frame, text="📂Load Chat", font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                         relief="flat", command=load_chat_history)
    load_button.grid(row=0, column=1, padx=2)

    # Export Chat Button
    export_button = Button(button_frame, text="💾Export Chat", font=("Arial", 12, "bold"), bg="#FFC107", fg="black",
                           relief="flat", command=export_chat_history)
    export_button.grid(row=0, column=2, padx=2)

    # Speak Button
    speak_button = Button(button_frame, text="🔊Speak", font=("Arial", 12, "bold"), bg="#FF9800", fg="black",
                          relief="flat", command=listen_for_command)
    speak_button.grid(row=0, column=3, padx=2)

    # Clear Chat Button
    clear_button = Button(button_frame, text="🗑️Clear Chat", font=("Arial", 12, "bold"), bg="#F44336", fg="white",
                          relief="flat", command=clear_chat)
    clear_button.grid(row=0, column=4, padx=2)

    # Stop Speaking Button
    stop_button = Button(button_frame, text="🚫Stop Speaking", font=("Arial", 12, "bold"), bg="#E91E63", fg="white",
                         relief="flat", command=stop_speech)
    stop_button.grid(row=0, column=5, padx=2)

    # Exit Button
    exit_button = Button(button_frame, text="🚪Exit", font=("Arial", 12, "bold"), bg="#9E9E9E", fg="black",
                         relief="flat", command=root.quit)
    exit_button.grid(row=0, column=6, padx=2)

    # Dropdown for commands
    command_var = tk.StringVar(root)
    command_var.set("Select Command")  # Default value

    commands = [
        "Open notepad", "Open calculator", "Open chrome",
        "Shutdown", "Restart", "Log off", "Lock",
        "Battery", "Cpu", "Ram"
    ]

    command_dropdown = tk.OptionMenu(button_frame, command_var, *commands)
    command_dropdown.config(font=("Arial", 12, "bold"), bg="#1e1e1e", fg="white", relief="flat")
    command_dropdown.grid(row=0, column=7, padx=2)

    # Execute Button for dropdown
    execute_button = Button(button_frame, text="Execute", font=("Arial", 12, "bold"), bg="#673AB7", fg="white",
                            relief="flat", command=execute_selected_command)
    execute_button.grid(row=0, column=8, padx=2)

    # Greet the user
    greeting_message = "Welcome, my name is Nexus. I can perform multiple tasks. How can I help you today?"
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "🤖 Nexus: " + greeting_message + "\n\n", "bot")
    chat_display.config(state=tk.DISABLED)
    speak_text(greeting_message)

    root.mainloop()

# Show the welcome image first
show_welcome_image()