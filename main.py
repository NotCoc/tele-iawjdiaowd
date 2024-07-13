import telebot
import http.client
import json
import re
import requests
import io

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the API token you obtained from BotFather
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_instructions(message):
    instructions = (
        "تحويل الرابط إلئ صوت\n\n"
        "@ummohbukh"
    )
    bot.reply_to(message, instructions)

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    regex = (
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/|youtube\.com/attribution_link\?a=)([a-zA-Z0-9_-]{11})'
    )
    match = re.search(regex, url)
    return match.group(1) if match else None


def sanitize_filename(filename):
    """
    Sanitize a filename to remove or replace characters that could cause issues.
    """
    # Remove characters not allowed in filenames on Windows
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

@bot.message_handler(content_types=['text'])
def handle_youtube_link(message):
    try:
        youtube_link = message.text.strip()
        video_id = extract_video_id(youtube_link)

        if not video_id:
            bot.reply_to(message, "رابط يوتيوب غير صالح. يرجى المحاولة مرة أخرى باستخدام الرابط المناسب.")
            return

        # Use the provided API to download the MP3 file
        conn = http.client.HTTPSConnection("youtube-mp36.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "youtube-mp36.p.rapidapi.com"
        }

        conn.request("GET", f"/dl?id={video_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        response_json = json.loads(data.decode("utf-8"))

        if 'link' in response_json:
            mp3_url = response_json['link']
            video_title = response_json['title']

            # Sanitize the video title for use as a filename
            sanitized_filename = sanitize_filename(video_title)

            # Download the MP3 file using requests
            response = requests.get(mp3_url)

            # Create an in-memory byte stream
            audio_bytes = io.BytesIO(response.content)
            audio_bytes.name = f"{sanitized_filename}.mp3"  # Set a filename for Telegram

            # Format the title for bold text
            formatted_title = f"<b>{video_title}</b>\n\n@ummohbukh"

            # Send the audio file directly
            bot.send_audio(message.chat.id, audio_bytes, caption=formatted_title, parse_mode='HTML')

        else:
            bot.reply_to(message, f"Failed to convert the video to MP3. Response: {response_json}")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

if __name__ == '__main__':
    bot.polling()
