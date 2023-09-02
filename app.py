from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

@app.route('/')
def summary_api():
    url = request.args.get('url', '')
    
    # Extract video_id from the URL
    video_id = extract_video_id(url)
    
    if video_id:
        try:
            summary = get_summary(video_id)
            return jsonify({"summary": summary}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid YouTube URL"}), 400

def extract_video_id(url):
    # Parse video_id from the URL
    video_id = None
    if '=' in url:
        url_parts = url.split('=')
        if len(url_parts) >= 2:
            video_id = url_parts[1]
    return video_id

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([d['text'] for d in transcript_list])
    return transcript

def get_summary(video_id):
    transcript = get_transcript(video_id)
    summarizer = pipeline('summarization')
    
    # Split the transcript into manageable chunks
    chunk_size = 1000
    chunks = [transcript[i:i + chunk_size] for i in range(0, len(transcript), chunk_size)]
    
    # Generate summaries for each chunk and combine them
    summary = ''
    for chunk in chunks:
        summary_text = summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
        summary += summary_text + ' '
    
    return summary

if __name__ == '__main__':
    app.run()
