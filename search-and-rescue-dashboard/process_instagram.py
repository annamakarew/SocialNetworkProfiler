import pandas as pd
import instaloader
import torch
import sys
import json
import requests
import io
import logging
from PIL import Image, ImageDraw, ImageFont
import base64
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification, SegformerImageProcessor, SegformerForSemanticSegmentation, BlipProcessor, BlipForConditionalGeneration
from dotenv import load_dotenv
load_dotenv()
from time import sleep
from ultralytics import YOLO
from contextlib import redirect_stdout

# # Get all logger names
# logger_names = logging.getLogger().manager.loggerDict.keys()

# # Filter logger names for "instaloader"
# instaloader_loggers = [name for name in logger_names if "instaloader" in name.lower()]

# # Print the filtered logger names
# print("Instaloader-related loggers:", instaloader_loggers)

# Override the context's log method
def suppress_log(self, message: str, *args, **kwargs):
    pass  # Do nothing

yolo_logger = logging.getLogger('ultralytics')
yolo_logger.disabled = True

processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
segformer_model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
yolo_model = YOLO("https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt", verbose=False)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# Clothing labels for segmentation
CLOTHING_LABELS = [
    "Background", "Hat", "Hair", "Sunglasses", "Upper-clothes", "Skirt", "Pants",
    "Dress", "Belt", "Left-shoe", "Right-shoe", "Face", "Left-leg", "Right-leg",
    "Left-arm", "Right-arm", "Bag", "Scarf"
]

def segment_clothing(image):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = segformer_model(**inputs)
    logits = outputs.logits
    upsampled_logits = torch.nn.functional.interpolate(
        logits, size=image.size[::-1], mode='bilinear', align_corners=False
    )
    seg_map = upsampled_logits.argmax(dim=1)[0].cpu().numpy()
    return seg_map

def generate_caption(image):
    inputs = blip_processor(image, return_tensors="pt")
    with torch.no_grad():
        caption_ids = blip_model.generate(**inputs)
    caption = blip_processor.decode(caption_ids[0], skip_special_tokens=True)
    return caption

def detect_objects(image):
    results = yolo_model(image, verbose=False)
    objects = []
    for result in results:
        for box in result.boxes:
            objects.append({
                "label": yolo_model.names[int(box.cls.item())],
                "coordinates": list(map(int, box.xyxy[0]))
            })
    return objects

def draw_bounding_boxes(image, objects_detected):
    """
    Draw bounding boxes on the image for detected objects.
    """
    draw = ImageDraw.Draw(image)

    for obj in objects_detected:
        label = obj["label"]
        coordinates = obj["coordinates"]  # [x_min, y_min, x_max, y_max]
        draw.rectangle(coordinates, outline="red", width=3)  # Draw the box
        draw.text((coordinates[0], coordinates[1] - 10), label, fill="red")  # Add label

    # Save the processed image or return as base64
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_image



def get_instagram_captions(username, output_file_path="captions.csv", max_posts=20):
    L = instaloader.Instaloader()
    
    # Try to load the session or log in
    acct_username = os.getenv("IG_USERNAME")
    acct_password = os.getenv("IG_PASSWORD")
    if not acct_username or not acct_password:
        raise ValueError("Instagram account credentials are not set.")

    try:
        L.load_session_from_file(acct_username)
        #print("Session loaded successfully.")
    except FileNotFoundError:
        try:
            #print("Session file not found. Logging in...", flush=True)
            L.login(acct_username, acct_password)
            L.save_session_to_file()
            #print("Session created and saved successfully.")
        except:
            raise ValueError("Failed to log in. Please check your credentials.")
    except Exception as e:
        #print(f"Error loading session: {e}. Recreating session...", flush=True)
        L.login(acct_username, acct_password)
        L.save_session_to_file()
        
    # Fetch profile data
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.LoginRequiredException:
        raise ValueError("Login is required to fetch this profile. Check your credentials.")
    except instaloader.AbortDownloadException as e:
        raise ValueError("Rate-limited or session expired. Recreate the session and retry.")

    captions = []
    post_count = 0

    for post in profile.get_posts():
        captions.append(post.caption)
        post_count += 1
        if post_count >= max_posts:
            break
        sleep(5) # Delay between requests to avoid rate-limiting


    df = pd.DataFrame(captions, columns=["Caption"])
    df.to_csv(output_file_path, index=False)
    return output_file_path


def analyze_caption(caption):
    """
    Analyze the sentiment and named entities of a given caption.

    Parameters:
        caption (str): The text caption to analyze.

    Returns:
        dict: A dictionary containing the sentiment and recognized entities.
    """
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

    # Perform sentiment analysis
    sentiment_result = sentiment_pipeline(caption)
    star_label = sentiment_result[0]["label"].lower()
    sentiment_label = star_to_sentiment.get(star_label, "unknown")

    # Perform named entity recognition
    ner_results = ner_pipeline(caption)
    recognized_entities = []
    current_entity = ""

    for entity in ner_results:
        if entity["word"].startswith("##"):
            current_entity += entity["word"][2:]
        else:
            if current_entity:
                recognized_entities.append(current_entity)
            current_entity = entity["word"]

    # Append the last entity if it exists
    if current_entity:
        recognized_entities.append(current_entity)

    # Return sentiment and entities
    return {
        "sentiment": sentiment_label,
        "entities": recognized_entities
    }

'''
def process_instagram_account(username, max_posts=20, output_file_path="processed_captions.csv"):
    captions_file = get_instagram_captions(username, max_posts=max_posts)
    processed_file = process_captions(captions_file, output_file_path)
    #print(f"Captions file generated at: {captions_file}")
    #print(f"Processed captions saved at: {processed_file}")

    return processed_file
'''

def process_instagram_account(username, max_posts=5):
    loader = instaloader.Instaloader()
    loader.context.quiet = True

    # Try to load session or log in
    try:
        loader.load_session_from_file(os.getenv("IG_USERNAME"))
    except FileNotFoundError:
        try:
            # Log in and save session if not already logged in
            loader.login(os.getenv("IG_USERNAME"), os.getenv("IG_PASSWORD"))
            loader.save_session_to_file()
        except instaloader.TwoFactorAuthRequiredException:
            print("Two-factor authentication required. Please provide the code:")
            two_factor_code = input("Enter the 2FA code: ")
            loader.two_factor_login(two_factor_code)
            loader.save_session_to_file()
        except instaloader.ConnectionException as e:
            if "challenge_required" in str(e):
                print("Challenge required. Please verify your account manually in the Instagram app.")
                return None
            else:
                raise e

    profile = instaloader.Profile.from_username(loader.context, username)
    data = []

    for post_index, post in enumerate(profile.get_posts()):
        if post_index >= max_posts:
            break

        caption = post.caption or "No caption"
        # Call the function to get sentiment and entities
        analysis_result = analyze_caption(caption)
        sentiment = analysis_result["sentiment"]  # Get the sentiment
        entities = ", ".join(analysis_result["entities"])  # Join entities into a single string

        # Validate post URL
        if not post.url:
            print(f"Post {post_index + 1} has no valid image URL. Skipping.", file=sys.stderr)
            continue

        try:
            response = requests.get(post.url)
            response.raise_for_status()  # Raise an error for bad status codes
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
        except Exception as e:
            print(f"Failed to download or process image for post {post_index + 1}: {e}", file=sys.stderr)
            continue

        # Perform image analysis
        #seg_map = segment_clothing(image)
        objects_detected = detect_objects(image)
        generated_caption = generate_caption(image)
        
        # Draw bounding boxes
        processed_image = draw_bounding_boxes(image, objects_detected)

        # Append results
        data.append({
            "Caption": caption,
            "Sentiment": sentiment,
            "Named Entities": entities,
            "Generated Caption": generated_caption,
            "Image": f"data:image/jpeg;base64,{processed_image}",  # Embed the processed image
            "Objects Detected": objects_detected
        })

    return data


if __name__ == "__main__":
    username = sys.argv[1]
    try:
        processed_data = process_instagram_account(username)
        print(json.dumps(processed_data, indent=4))
    except Exception as e:
        print(f"Error: {e}", flush=True)
        sys.exit(1)
