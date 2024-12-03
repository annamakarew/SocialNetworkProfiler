from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation, BlipProcessor, BlipForConditionalGeneration
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
import numpy as np
import torch

#Segformer model and processor for clothing segmentation
processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
segformer_model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")

#YOLO model for general object detection
yolo_model = YOLO("https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt")

#BLIP model for image captioning
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# Define label map for Segformer
CLOTHING_LABELS = [
    "Background", "Hat", "Hair", "Sunglasses", "Upper-clothes", "Skirt", "Pants",
    "Dress", "Belt", "Left-shoe", "Right-shoe", "Face", "Left-leg", "Right-leg",
    "Left-arm", "Right-arm", "Bag", "Scarf"
]

def segment_clothing(image):
    # Process the image and get clothing segmentation map
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = segformer_model(**inputs)

    # Upsample the logits to the original image size
    logits = outputs.logits
    upsampled_logits = torch.nn.functional.interpolate(
        logits, size=image.size[::-1], mode='bilinear', align_corners=False
    )
    seg_map = upsampled_logits.argmax(dim=1)[0].cpu().numpy()

    return seg_map

def generate_caption(image):
    # Generate a caption for the image using BLIP
    inputs = blip_processor(image, return_tensors="pt")
    with torch.no_grad():
        caption_ids = blip_model.generate(**inputs)
    caption = blip_processor.decode(caption_ids[0], skip_special_tokens=True)
    return caption

def detect_and_draw_boxes(image, seg_map, caption, output_path="output1.jpg"):
    draw = ImageDraw.Draw(image, "RGBA")
    font = ImageFont.load_default()

    yolo_results = yolo_model(image)
    for result in yolo_results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get box coordinates
            label = yolo_model.names[int(box.cls.item())]  # Get object label

            draw.rectangle([x1, y1, x2, y2], outline="blue", width=4)

            text_bbox = font.getbbox(label)
            text_bg = (x1, y1 - 15, x1 + text_bbox[2] + 4, y1)
            draw.rectangle(text_bg, fill="blue")
            draw.text((x1 + 2, y1 - 12), label, fill="white", font=font)

    colors = {
        "Upper-clothes": "green",
        "Pants": "purple",
        "Dress": "yellow",
        "Hat": "red",
        "Bag": "orange",
        "Scarf": "pink"
    }

    for item, color in colors.items():
        if item in CLOTHING_LABELS:
            label_index = CLOTHING_LABELS.index(item)
            mask = (seg_map == label_index)
            if np.any(mask):
                # Get bounding box for each unique clothing item
                y_indices, x_indices = np.where(mask)
                if len(y_indices) > 0 and len(x_indices) > 0:
                    # Define bounding box around the item
                    x1, y1, x2, y2 = x_indices.min(), y_indices.min(), x_indices.max(), y_indices.max()
                    draw.rectangle([x1, y1, x2, y2], outline=color, width=4)

                    # Add label with background for readability
                    text_bbox = font.getbbox(item)
                    text_bg = (x1, y1 - 15, x1 + text_bbox[2] + 4, y1)
                    draw.rectangle(text_bg, fill=color)
                    draw.text((x1 + 2, y1 - 12), item, fill="white", font=font)

    caption_text_bbox = font.getbbox(caption)
    caption_bg = (10, image.height - 20 - caption_text_bbox[3], 10 + caption_text_bbox[2] + 10, image.height - 10)
    draw.rectangle(caption_bg, fill="black")
    draw.text((15, image.height - 20 - caption_text_bbox[3]), caption, fill="white", font=font)

    image.save(output_path)
    print(f"Output image with highlighted objects and caption saved at: {output_path}")

image_path = "img.jpg"
image = Image.open(image_path).convert("RGB")

seg_map = segment_clothing(image)
caption = generate_caption(image)
print("Generated Caption:", caption)

detect_and_draw_boxes(image, seg_map, caption)
