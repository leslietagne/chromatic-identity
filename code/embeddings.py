import torch
import numpy as np
from pathlib import Path
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import json

DEVICE = "cpu"
DATA_DIR = Path("data")
OUT_DIR = Path("figures")
OUT_DIR.mkdir(exist_ok=True)

print(f"Device : {DEVICE}")


def load_model():
    print("Chargement de CLIP...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.eval()
    print("CLIP chargé.")
    return model, processor


def embed_image(img_path, model, processor):
    img = Image.open(img_path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    return features.squeeze().cpu().numpy()


def run():
    model, processor = load_model()
    results = []
    images = sorted(DATA_DIR.rglob("*.jpg"))
    print(f"{len(images)} images trouvées")

    for i, img_path in enumerate(images):
        parts = img_path.parts
        brand = parts[1]
        collection = parts[2]
        try:
            vec = embed_image(img_path, model, processor)
            results.append({
                "path": str(img_path),
                "brand": brand,
                "collection": collection,
                "embedding": vec.tolist()
            })
            print(f"[{i+1}/{len(images)}] ✓ {collection}/{img_path.name}", end="\r")
        except Exception as e:
            print(f"\n✗ erreur {img_path}: {e}")

        # Sauvegarde intermédiaire toutes les 500 images
        if (i + 1) % 500 == 0:
            checkpoint = OUT_DIR / "embeddings_checkpoint.json"
            with open(checkpoint, "w") as f:
                json.dump(results, f)
            print(f"\n[Checkpoint] {len(results)} embeddings sauvegardés")

    out = OUT_DIR / "embeddings.json"
    with open(out, "w") as f:
        json.dump(results, f)
    print(f"\nDone — {len(results)} embeddings → {out}")


try:
    run()
except Exception as e:
    import traceback
    traceback.print_exc()