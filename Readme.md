YouTube Video Finder Using Gemini API
This project is a YouTube video search and video analysis tool that uses Gemini API to analyze and rank videos based on relevance, title clarity, and informativeness.

Key Features:
Search YouTube: Search for videos on YouTube based on a given query.

Filter Videos: Filter videos based on duration (4-20 minutes) and publish date (last 14 days).

Analyze with Gemini API: Use the Gemini API to evaluate video titles and select the most relevant, clear, and informative video.

Voice and Text Input: Users can input search queries via text or voice (simulated).

Result Logging: Log each search query along with the selected video to a CSV file.

Technologies Used:
YouTube API: For searching and getting video data.

Gemini API (Google Cloud): For video analysis and ranking.

Python: For backend processing and logic.

CSV: For logging search results.

Table of Contents
Installation

Environment Variables Setup

Running the Project

Usage

How It Works






Installation
1. Clone the repository
2. Create a Virtual Environment
Make sure you have Python 3.7+ installed.
3. Activate Virtual Environment
4. Install Dependencies
pip install -r requirements.txt

Environment Variables Setup
1. Set YouTube API Key
Create a Google Developer Account and set up a project to get the YouTube API key.

Add the key in a .env file:

YOUTUBE_API_KEY=your_youtube_api_key_here

2. Set Gemini API Credentials
Follow Google Cloud documentation to create a service account and download the JSON credentials file.

To start the YouTube Video Finder application:

'python app.py'


Input Type:

Text Input: You can type the search query directly.

Voice Input: Simulate a voice query by choosing "voice" when prompted.

Search Result:

The program will filter videos based on the duration (4–20 minutes) and the publish date (within the last 14 days).

It will then analyze the video titles using the Gemini API to determine which video is most relevant, clear, and informative.

Usage
Start the program by running python app.py.

Enter a search query (e.g., "AI tools for students").

The program will:

Search YouTube for videos matching the query.

Filter results based on the video length and publish date.

Analyze the filtered videos using the Gemini API.

Output the best match based on video relevance and clarity.

Log the search result into a CSV file for reference.

How It Works
YouTube Search: The YouTube API is queried using a search term. It fetches video details like title, duration, views, and publish date.

Video Filtering: The videos are filtered to ensure they meet the duration (4-20 minutes) and are published within the last 14 days.

Gemini Analysis: The filtered videos are passed to the Gemini API, which evaluates the relevance, clarity, and informativeness of the video titles.

Best Video Selection: The program selects the best video based on the analysis and displays the details.
