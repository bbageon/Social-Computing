# https://wikidocs.net/233744
# About gensim Library
# pip install gensim

# Basic CODE
# from gensim.models import Word2Vec
# from gensim.test.utils import common_texts

# # Word2Vec 모델 훈련
# model = Word2Vec(sentences=common_texts, vector_size=100, window=5, min_count=1, workers=4)

# # 단어 벡터 얻기
# word_vectors = model.wv

# === Exercise 4.1: Topic Modeling ===

import re
import nltk
import matplotlib.pyplot as plt

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
from gensim import corpora, models
from gensim.parsing.preprocessing import remove_stopwords
import sqlite3
import pandas as pd

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("vader_lexicon")  # Analysis emotion
nltk.download("averaged_perceptron_tagger")
nltk.download("averaged_perceptron_tagger_eng")
nltk.download("wordnet")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger_eng")

con = sqlite3.connect("/Users/bbageon/Downloads/database.sqlite")

# Call every posts for seperating topics
posts = pd.read_sql_query("SELECT id, content FROM posts", con)


# === Prevent duplicated word and remove words list ==
stop_words = set(stopwords.words("english"))
stop_words.update(
    [
        "today",
        "day",
        "time",
        "people",
        "life",
        "world",
        "thing",
        "morning",
        "anyone",
        "wait",
        "giveaway",
        "good",
        "great",
        "make",
        "see",
        "change",
    ]
)
lemmatizer = WordNetLemmatizer()


def preprocess(text):
    if not isinstance(text, str):
        return []
    # # Change lower word
    # text = text.lower()
    # # Remove "the", "a", "is" for focusing Noun
    # text = remove_stopwords(text)
    # tokens = word_tokenize(text)
    # tokens = [word for word, pos in pos_tag(tokens) if pos.startswith("NN")]

    # Lowercasing
    text = text.lower()
    # Regular Expression
    text = re.sub(r"[^a-z\s]", "", text)

    # Tokenization
    tokens = word_tokenize(text)

    # Stopwords filtering
    tokens = [w for w in tokens if w not in stop_words and len(w) > 2]

    # lemmatization
    tokens = [lemmatizer.lemmatize(w) for w in tokens]

    # pos tagging after that, extraction only nouns
    tagged = pos_tag(tokens)
    tokens = [word for word, pos in tagged if pos.startswith("NN")]
    return tokens


posts["tokens"] = posts["content"].apply(preprocess)

# === LDA Model Train ===

dictionary = corpora.Dictionary(posts["tokens"])
# print(dictionary)
# print(dictionary.token2id)
corpus = [dictionary.doc2bow(text) for text in posts["tokens"]]
# print("123", corpus)

lda_model = models.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=10,
    random_state=42,
    passes=10,
    alpha="auto",
)

print("\n=== Top 10 Topics ===")
# top_topic = lda_model.show_topics(num_topics=1, num_words=10, formatted=False)[0][1]
# print([word for word, prob in top_topic])
for idx, topic in lda_model.show_topics(num_topics=10, num_words=6, formatted=False):
    print(f"Topic {idx+1}: {[word for word, prob in topic]}")

# Emotion Analysis
# https://www.nltk.org/howto/sentiment.html?utm_source=chatgpt.com
# Library load
E_A = SentimentIntensityAnalyzer()


posts["compound"] = (
    posts["content"].astype(str).apply(lambda x: E_A.polarity_scores(x)["compound"])
)
posts["sentiment"] = posts["compound"].apply(
    lambda x: "positive" if x > 0.05 else "negative" if x < -0.05 else "neutral"
)

print("\n=== Platform Sentiment Distribution ===")
print(posts["sentiment"].value_counts(normalize=True))


# === 4.2 Topic-wise Sentiment Analysis ===
# Top topic set
def get_main_topic(tokens):
    if not tokens:
        return None
    bow = dictionary.doc2bow(tokens)
    topic_probs = lda_model.get_document_topics(bow)
    if not topic_probs:
        return None
    # 가장 확률이 높은 토픽 번호 반환
    # print(topic_probs, "123")
    return max(topic_probs, key=lambda x: x[1])[0]


# main_topic 열 생성
posts["main_topic"] = posts["tokens"].apply(get_main_topic)

# Topic-wise sentiment rate(positive / neutral / negative) ===
sentiment_by_topic = (
    posts.groupby(["main_topic", "sentiment"]).size().unstack(fill_value=0).sort_index()
)

# 비율 계산
sentiment_by_topic_ratio = sentiment_by_topic.div(
    sentiment_by_topic.sum(axis=1), axis=0
)

print("\n=== Sentiment Ratio by Topic ===")
print(sentiment_by_topic_ratio)

# plt.figure(figsize=(10, 6))
# sentiment_by_topic_ratio.plot(
#     kind="bar",
#     stacked=True,
#     colormap="RdYlGn",
#     figsize=(10, 6),
# )
# plt.title("Sentiment Distribution by LDA Topic")
# plt.xlabel("LDA Topic Number")
# plt.ylabel("Proportion")
# plt.legend(title="Sentiment", loc="upper right")
# plt.tight_layout()
# plt.show()
