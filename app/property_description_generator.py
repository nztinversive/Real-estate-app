import os
import requests
from PIL import Image
import torch
from torchvision.transforms import Resize, ToTensor, Normalize
from torchvision.models import resnet50
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained models
vision_model = resnet50(pretrained=True)
vision_model.eval()

language_model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

def preprocess_image(image_path):
    image = Image.open(image_path)
    preprocess = torch.nn.Sequential(
        Resize((224, 224)),
        ToTensor(),
        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    )
    return preprocess(image).unsqueeze(0)

def extract_image_features(image_path):
    image = preprocess_image(image_path)
    with torch.no_grad():
        features = vision_model(image)
    return features

def generate_description(image_features, prompt):
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
    
    output = language_model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=150,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        temperature=0.7,
    )
    
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text

def analyze_property_photos(photo_paths):
    features = []
    for path in photo_paths:
        features.append(extract_image_features(path))
    
    # Combine features (e.g., by averaging)
    combined_features = torch.mean(torch.stack(features), dim=0)
    
    return combined_features

def generate_property_description(photo_paths):
    combined_features = analyze_property_photos(photo_paths)
    
    prompt = "This property features"
    description = generate_description(combined_features, prompt)
    
    return description