from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import instaloader
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification

app = FastAPI()

# Load models at startup
sentiment_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
ner_model_name = "dslim/bert-base-NER"

sentiment_pipeline = pipeline("sentiment-analysis", 
                               model=AutoModelForSequenceClassification.from_pretrained(sentiment_model_name), 
                               tokenizer=AutoTokenizer.from_pretrained(sentiment_model_name))

ner_pipeline = pipeline("ner", 
                        model=AutoModelForTokenClassification.from_pretrained(ner_model_name), 
                        tokenizer=AutoTokenizer.from_pretrained(ner_model_name))

class UserRequest(BaseModel):
    username: str
    max_posts: int = 20

def get_instagram_captions(username, max_posts=20):
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)
    captions = [post.caption for post in profile.get_posts()][:max_posts]
    return pd.DataFrame(captions, columns=["Caption"])

@app.post("/process")
def process_instagram_account(request: UserRequest):
    try:
        #df = get_instagram_captions(request.username, request.max_posts)
        df = pd.read_csv("processed_captions.csv")
        sentiments = []
        named_entities = []

        star_to_sentiment = {
            "1 star": "negative",
            "2 stars": "negative",
            "3 stars": "neutral",
            "4 stars": "positive",
            "5 stars": "positive"
        }

        for caption in df["Caption"]:
            sentiment_result = sentiment_pipeline(caption)
            star_label = sentiment_result[0]["label"].lower()
            sentiment_label = star_to_sentiment.get(star_label, "unknown")
            sentiments.append(sentiment_label)

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
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
