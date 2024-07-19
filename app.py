from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

app = Flask(__name__)

summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')
executor = ThreadPoolExecutor(max_workers=4)

@app.get('/summary')
def summary_api():
    url = request.args.get('url', '')
    video_id = url.split('=')[1]
    future = executor.submit(get_summary_for_video, video_id)
    summary = future.result()
    if 'error' in summary:
        return jsonify(summary), 404
    return summary, 200

def get_summary_for_video(video_id):
    try:
        transcript = get_transcript(video_id)
    except NoTranscriptFound as e:
        return {"error": str(e)}
    return get_summary(transcript)

@lru_cache(maxsize=32)
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except NoTranscriptFound:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-GB'])
    transcript = ' '.join([d['text'] for d in transcript_list])
    return transcript

def get_summary(transcript):
    batch_size = 2000
    summary = ''
    for i in range(0, (len(transcript) // batch_size) + 1):
        batch_text = transcript[i * batch_size:(i + 1) * batch_size]
        if batch_text:
            summary_text = summarizer(batch_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            summary += summary_text + ' '
    return summary.strip()

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
