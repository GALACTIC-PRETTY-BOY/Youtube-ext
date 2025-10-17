import pandas as pd
import re
import numpy as np
import tensorflow as tf
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from googleapiclient.discovery import build

model = tf.keras.models.load_model("ModelV2.keras")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

comment_max_len = 40
context_max_len = 120

appos = {
    "aren't": "are not", "can't": "cannot", "couldn't": "could not",
    "didn't": "did not", "doesn't": "does not", "dont": "do not",
    "arent": "are not", "cant": "cannot", "couldnt": "could not",
    "didnt": "did not", "doesnt": "do not"
}

stop_words = set(stopwords.words("english"))
negations = {"no", "nor", "not", "never", "cannot"}
stop_words -= negations
lemmatizer = WordNetLemmatizer()

def expand_contractions(text, mapping=appos):
    return re.sub(r'\b(' + '|'.join(mapping.keys()) + r')\b',
                  lambda x: mapping[x.group()], text)

def preprocess(text):
    text = expand_contractions(str(text).lower())
    tokens = word_tokenize(text)
    return " ".join([
        lemmatizer.lemmatize(w)
        for w in tokens
        if w.isalpha() and w not in stop_words
    ])

API_KEY = "AIzaSyAiggkZTjKRGd_3pYRTJIe-08QOjfnHYgI"
video_id = "f1mfoI1ouWE"
youtube = build("youtube", "v3", developerKey=API_KEY)

all_comments = []
next_page_token = None

while True:
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        pageToken=next_page_token
    ).execute()

    all_comments.extend(response["items"])
    next_page_token = response.get("nextPageToken")

    if not next_page_token:
        break

comments_df = pd.json_normalize(all_comments)
comments_df = pd.DataFrame({
    "COMMENT": comments_df["snippet.topLevelComment.snippet.textDisplay"]
})

comments_df["processed"] = comments_df["COMMENT"].apply(preprocess)

sequences = tokenizer.texts_to_sequences(comments_df["processed"].astype(str))

padded = pad_sequences(sequences, maxlen=comment_max_len, padding="post")

context_padded = pad_sequences(sequences, maxlen=context_max_len, padding="post")
context_padded = np.roll(context_padded, shift=1, axis=0)

pred_probs = model.predict(
    {"context_input": context_padded, "comment_input": padded}
)

pred_classes = np.argmax(pred_probs, axis=1)
label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}

for i, comment in enumerate(comments_df["COMMENT"]):
    sentiment = label_map[pred_classes[i]]
    probs = pred_probs[i]
    print(f"Comment: {comment}")
    print(f"Predicted Sentiment: {sentiment}")
    print(f"Probabilities -> Negative: {probs[0]:.2f}, Neutral: {probs[1]:.2f}, Positive: {probs[2]:.2f}")
    print("-" * 60)
