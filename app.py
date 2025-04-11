from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai
from config import GEMINI_API_KEY, WEATHER_API_KEY, NEWS_API_KEY

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
# ✅ Proper Gemini configuration
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")  # or "gemini-1.5-pro" if enabled

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask-gemini", methods=["POST"])
def ask_gemini():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please enter a message."})

    try:
        chat = model.start_chat()
        response = chat.send_message(user_input)
        reply_text = response.text

        # Just return raw text as plain string
        return jsonify({"reply": reply_text})
    except Exception as e:
        print("Gemini Error:", e)
        return jsonify({"reply": "⚠️ Gemini API error. Please try again."})


@app.route("/get-news", methods=["POST"])
def get_news():
    topic = request.json.get("topic", "latest")
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&language=en&pageSize=10&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    try:
        articles = response.json().get("articles", [])
        if not articles:
            return jsonify({"reply": f"No news found for topic: {topic}"})

        news_html = f"<strong>🗞 Top 10 News for '{topic.title()}':</strong><br><br>"
        for i, article in enumerate(articles):
            title = article['title']
            link = article['url']
            news_html += f"<div style='margin-bottom: 15px;'><strong>{i+1}.</strong> {title}<br>🔗 <a href='{link}' target='_blank'>{link}</a></div>"

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
            f"📍 {data['name']}, {data['sys']['country']}<br>"
            f"🌤 {data['weather'][0]['description'].title()}<br>"
            f"🌡 Temperature: {data['main']['temp']}°C<br>"
            f"💧 Humidity: {data['main']['humidity']}%<br>"
            f"🌬 Wind: {data['wind']['speed']} m/s"
        )
        return jsonify({"reply": weather_info})
    except Exception as e:
        print("Error fetching weather:", e)
        return jsonify({"reply": "Couldn't fetch weather details. Try again later."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
