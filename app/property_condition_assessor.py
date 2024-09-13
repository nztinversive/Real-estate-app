import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image

# Load pre-trained model
model = fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Define classes for property issues
CLASSES = [
    'roof_damage', 'wall_cracks', 'water_damage', 'mold', 'broken_window',
    'peeling_paint', 'foundation_issues', 'electrical_hazard', 'plumbing_issues'
]

def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = F.to_tensor(image)
    return image_tensor

def detect_issues(image_tensor):
    with torch.no_grad():
        prediction = model([image_tensor])
    
    return prediction[0]

def analyze_property_condition(photo_paths):
    issues = []
    for path in photo_paths:
        image_tensor = preprocess_image(path)
        prediction = detect_issues(image_tensor)
        
        boxes = prediction['boxes']
        labels = prediction['labels']
        scores = prediction['scores']
        
        for box, label, score in zip(boxes, labels, scores):
            if score > 0.5:  # Confidence threshold
                issue = {
                    'type': CLASSES[label],
                    'confidence': float(score),
                    'location': box.tolist()
                }
                issues.append(issue)
    
    return issues

def estimate_repair_costs(issues):
    # This is a simplified cost estimation. In a real-world scenario,
    # you would need a more comprehensive database of repair costs.
    cost_estimates = {
        'roof_damage': 5000,
        'wall_cracks': 1000,
        'water_damage': 2500,
        'mold': 1500,
        'broken_window': 500,
        'peeling_paint': 1000,
        'foundation_issues': 10000,
        'electrical_hazard': 2000,
        'plumbing_issues': 1500
    }
    
    total_cost = sum(cost_estimates.get(issue['type'], 0) for issue in issues)
    return total_cost

def generate_maintenance_tasks(issues):
    tasks = []
    for issue in issues:
        task = f"Address {issue['type']} - Confidence: {issue['confidence']:.2f}"
        tasks.append(task)
    return tasks