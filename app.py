import os
import json
import datetime
import csv
import re
#import openai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up API keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#openai.api_key = OPENAI_API_KEY

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_user_input():
    """Get input from the user via text or simulated voice."""
    input_type = input("Enter input type (text/voice): ").lower()
    
    if input_type == "voice":
        print("Simulating voice input...")
        # In a real implementation, this would be replaced by speech-to-text
    query = input("Enter your search query: ")
    return query

def search_youtube_videos(query, max_results=20):
    """Search YouTube for videos with specific filters."""
    try:
        # Date filtering: last 14 days
        two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=14)
        published_after = two_weeks_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

        search_response = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=max_results,
            type="video",
            publishedAfter=published_after,
            order="relevance"
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response['items']]

        videos_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids)
        ).execute()

        filtered_videos = []
        for video in videos_response['items']:
            duration = video['contentDetails']['duration']
            duration_seconds = parse_duration(duration)
            if 240 <= duration_seconds <= 1200:
                filtered_videos.append({
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'channelTitle': video['snippet']['channelTitle'],
                    'publishedAt': video['snippet']['publishedAt'],
                    'duration': duration,
                    'duration_seconds': duration_seconds,
                    'viewCount': video['statistics'].get('viewCount', 0),
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                })

        return filtered_videos

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []

def parse_duration(duration_str):
    """Convert ISO 8601 duration format to seconds."""
    hours = re.search(r'(\d+)H', duration_str)
    minutes = re.search(r'(\d+)M', duration_str)
    seconds = re.search(r'(\d+)S', duration_str)

    total_seconds = 0
    if hours:
        total_seconds += int(hours.group(1)) * 3600
    if minutes:
        total_seconds += int(minutes.group(1)) * 60
    if seconds:
        total_seconds += int(seconds.group(1))

    return total_seconds

def analyze_videos_with_llm(videos, query):
    """Use OpenAI GPT-4o to analyze and select the best video."""
    if not videos:
        return None

    video_info = []
    for i, video in enumerate(videos, 1):
        video_info.append(f"{i}. Title: '{video['title']}' by {video['channelTitle']} ({format_duration(video['duration_seconds'])})")

    prompt = f"""
You are an intelligent assistant. Given the following YouTube video search results for the query "{query}", select the best video based on:

1. Relevance to the query
2. Title clarity and informativeness (not clickbait)
3. Likely educational value

Here are the videos:
{chr(10).join(video_info)}

Return only the number (like 1 or 2 or 3) of the best video. Do not return anything else.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant that returns the best video number."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5,
            temperature=0
        )
        content = response.choices[0].message["content"].strip()
        best_video_number = int(re.search(r'\d+', content).group())
        if 1 <= best_video_number <= len(videos):
            return videos[best_video_number - 1]
        else:
            print("LLM returned an out-of-range index. Defaulting to first video.")
            return videos[0]
    except Exception as e:
        print(f"Error analyzing with OpenAI: {e}")
        return videos[0]

def format_duration(seconds):
    """Format seconds into HH:MM:SS or MM:SS format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"

def log_result(query, video, filename="search_history.csv"):
    """Log the search query and selected video to a CSV file."""
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'query', 'video_id', 'title', 'channel', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'query': query,
            'video_id': video['id'],
            'title': video['title'],
            'channel': video['channelTitle'],
            'url': video['url']
        })
    print(f"Result logged to {filename}")

def display_results(video, query):
    """Display the selected video nicely."""
    if not video:
        print("\n😞 No matching videos found.")
        return

    print("\n" + "="*60)
    print(f"🔍 Search Query: \"{query}\"")
    print("="*60)
    print(f"🏆 BEST MATCH:")
    print(f"📺 Title: {video['title']}")
    print(f"👤 Channel: {video['channelTitle']}")
    print(f"⏱️ Duration: {format_duration(video['duration_seconds'])}")
    print(f"📅 Published: {video['publishedAt'].split('T')[0]}")
    print(f"👁️ Views: {int(video['viewCount']):,}")
    print(f"🔗 URL: {video['url']}")
    print("="*60)

def main():
    print("🎯 YouTube Video Finder")
    print("------------------------")
    query = get_user_input()

    print(f"\n🔎 Searching YouTube for: \"{query}\"")
    print("🎛️ Filtering videos (4–20 minutes, posted in last 14 days)...")
    videos = search_youtube_videos(query)

    if not videos:
        print("❌ No matching videos found.")
        return

    print(f"✅ Found {len(videos)} relevant videos.")
    print("🧠 Using GPT-4o to analyze titles and pick the best one...")

    best_video = analyze_videos_with_llm(videos, query)
    display_results(best_video, query)
    log_result(query, best_video)

if __name__ == "__main__":
    main()
