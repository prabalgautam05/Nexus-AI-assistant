from flask import Flask, render_template, request, jsonify
import requests
from config import API_KEY, WEATHER_API_KEY, NEWS_API_KEY

app = Flask(__name__)

@app.route("/get-news", methods=["POST"])
def get_news():
    topic = request.json.get("topic", "latest")
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&language=en&pageSize=10&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    try:
        articles = response.json().get("articles", [])
        if not articles:
            return jsonify({"reply": f"No news found for topic: {topic}"})

        # Build clean HTML with spacing and styling
        news_html = f"<strong>🗞 Top 10 News for '{topic.title()}':</strong><br><br>"
        for i, article in enumerate(articles):
            title = article['title']
            url = article['url']
            news_html += f"<div style='margin-bottom: 15px;'><strong>{i+1}.</strong> {title}<br>🔗 <a href='{url}' target='_blank'>{url}</a></div>"

        return jsonify({"reply": news_html})
    except Exception as e:
        print("Error fetching news:", e)
        return jsonify({"reply": "Couldn't fetch news. Try again later."})


@app.route("/get-weather", methods=["POST"])
def get_weather():
    lat = request.json.get("lat")
    lon = request.json.get("lon")

    if not lat or not lon:
        return jsonify({"reply": "Location coordinates are missing."})

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    try:
        data = response.json()
        if data.get("cod") != 200:
            return jsonify({"reply": "Weather data unavailable for your location."})

        weather_info = (
            f"📍 {data['name']}, {data['sys']['country']}\n"
            f"🌤 {data['weather'][0]['description'].title()}\n"
            f"🌡 Temperature: {data['main']['temp']}°C\n"
            f"💧 Humidity: {data['main']['humidity']}%\n"
            f"🌬 Wind: {data['wind']['speed']} m/s"
        )
        return jsonify({"reply": weather_info})
    except:
        return jsonify({"reply": "Couldn't fetch weather details. Try again later."})


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask-gemini", methods=["POST"])
def ask_gemini():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"reply": "Please enter a message."})

    print(f"Querying Gemini with: {user_input}")  # 🔍 Log what you're asking

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-thinking-exp-01-21:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": user_input}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 400
        }
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)

    print("Gemini response:", response.text)  # 🔍 Log raw Gemini response

    try:
        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        reply = "I couldn't process that right now. Please try again."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
