import os
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract video ID from YouTube URL
def extract_video_id(youtube_video_url):
    
    try:
        if "youtu.be" in youtube_video_url:
            video_id = youtube_video_url.split("/")[-1].split("?")[0]  # Handle short URL format
        elif "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[-1].split("&")[0]  # Handle long URL format
        else:
            raise ValueError("Invalid YouTube URL format")
        return video_id
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")pi
        return None

# Function to fetch captions using youtube-transcript-api
def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        return formatted_transcript
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Function to summarize text, focusing on important teaching points
def summarize_text_with_spacy(transcript_text):
    # Use spaCy to process the text
    doc = nlp(transcript_text)

    # Tokenize into sentences
    sentences = list(doc.sents)

    # Filter out introductory content (start of video, greetings)
    filtered_sentences = [str(sent) for sent in sentences if len(str(sent).split()) > 5 and not any(greeting in str(sent).lower() for greeting in ["hi", "welcome", "hello", "hey", "today", "in this video"])]

    # Focus on key teaching content (keywords)
    key_phrases = ["phrasal verb", "example", "use", "meaning", "sentence", "teach", "explain", "suggest", "plan", "help"]

    filtered_sentences = [str(sent) for sent in filtered_sentences if any(phrase in str(sent).lower() for phrase in key_phrases)]

    # Join sentences and ensure the summary is between 100 and 150 words
    summary = " ".join(filtered_sentences)
    words = summary.split()

    # Ensure the summary is between 100 and 150 words
    if len(words) < 500:
        # If the summary is too short, add more sentences to reach the word count
        additional_sentences = [str(sent) for sent in sentences[len(filtered_sentences):] if len(str(sent).split()) > 5]
        additional_words = " ".join(additional_sentences).split()
        words.extend(additional_words[:550 - len(words)])

    # Return the summary with 500 to 550 words
    return " ".join(words[:550]).strip()

# Streamlit UI
st.title("YouTube Transcript to Focused Summary Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)  # Extract the video ID correctly
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Focused Summary"):
    if video_id:
        transcript_text = fetch_transcript(video_id)

        if transcript_text:
            # Show full transcript (optional)
            st.write("### Transcript")
            st.text_area("Transcript", transcript_text, height=300)

            # Attempt to summarize using spaCy, filtering for teaching-related content
            summary = summarize_text_with_spacy(transcript_text)
            
            if summary:
                st.markdown("## Focused Summary (500-550 Words):")
                st.write(summary)
        else:
            st.error("Could not fetch transcript.")
    else:
        st.error("Invalid YouTube link. Please try again.")
