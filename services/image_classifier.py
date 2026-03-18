from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

CATEGORIES: list[str] = [
    "Electronics",
    "Clothing & Fashion",
    "Beauty & Personal Care",
    "Home & Kitchen",
    "Sports & Outdoors",
    "Books & Media",
    "Toys & Games",
    "Automotive",
]

N_CLASSES: int = len(CATEGORIES)
DEVICE: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CHECKPOINT_PATH: Path = Path(__file__).parent / "product_classifier.pth"

image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def _build_model() -> nn.Module:
    backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

    for param in backbone.parameters():
        param.requires_grad = False

    in_features: int = backbone.fc.in_features
    backbone.fc = nn.Sequential(
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(256, N_CLASSES),
    )

    return backbone.to(DEVICE)


_model: nn.Module = _build_model()

if CHECKPOINT_PATH.exists():
    state = torch.load(str(CHECKPOINT_PATH), map_location=DEVICE)
    _model.load_state_dict(state)

_model.eval()


def classify_image(image_bytes: bytes) -> dict[str, Any]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = image_transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = _model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze()

    probs_list = probs.cpu().tolist()
    top_idx = int(probs.argmax().item())

    return {
        "predicted_category": CATEGORIES[top_idx],
        "confidence": round(float(probs_list[top_idx]), 4),
        "all_scores": {
            cat: round(float(probs_list[i]), 4)
            for i, cat in enumerate(CATEGORIES)
        },
    }
