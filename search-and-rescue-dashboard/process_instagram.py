import pandas as pd
import instaloader
import torch
import sys
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification

def get_instagram_captions(username, output_file_path="captions.csv", max_posts=20):
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)
    captions = []
    post_count = 0

    for post in profile.get_posts():
        captions.append(post.caption)
        post_count += 1
        if post_count >= max_posts:
            break

    df = pd.DataFrame(captions, columns=["Caption"])
    df.to_csv(output_file_path, index=False)
    return output_file_path


def process_captions(input_file_path, output_file_path):
    df = pd.read_csv(input_file_path)
    '''
    if "Caption" not in df.columns:
        raise ValueError("Input spreadsheet must have a column named 'Caption'.")
    '''

    # sentiment model
    sentiment_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
    sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
    sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)

    # NER model
    ner_model_name = "dslim/bert-base-NER"
    ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
    ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
    ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer)

    star_to_sentiment = {
        "1 star": "negative",
        "2 stars": "negative",
        "3 stars": "neutral",
        "4 stars": "positive",
        "5 stars": "positive"
    }

    sentiments = []
    named_entities = []

    for caption in df["Caption"]:
        # sentiment
        sentiment_result = sentiment_pipeline(caption)
        star_label = sentiment_result[0]["label"].lower()
        sentiment_label = star_to_sentiment.get(star_label, "unknown")
        sentiments.append(sentiment_label)

        # named entities
        ner_results = ner_pipeline(caption)
        entity_texts = []
        entity_text = ""
        for entity in ner_results:
            if entity["word"].startswith("##"):
                entity_text += entity["word"][2:]
            else:
                if entity_text:
                    entity_texts.append(entity_text)
                entity_text = entity["word"]
        if entity_text:
            entity_texts.append(entity_text)
        named_entities.append(", ".join(entity_texts))

    df["Sentiment"] = sentiments
    df["Named_Entities"] = named_entities

    df.to_csv(output_file_path, index=False)
    #print(f"Processed file saved at: {output_file_path}")


def process_instagram_account(username, max_posts=20, output_file_path="processed_captions.csv"):
    captions_file = get_instagram_captions(username, max_posts=max_posts)
    processed_file = process_captions(captions_file, output_file_path)
    return processed_file


if __name__ == "__main__":
    username = sys.argv[1]

    processed_csv_path = process_instagram_account(username)

    processed_data = pd.read_csv(processed_csv_path)

    processed_data = processed_data.where(pd.notnull(processed_data), None)

    result = processed_data.to_dict(orient="records")

    print(json.dumps(result))