"""
Emo-Check: FastAPI バックエンド
- /predict: 画像のエモ度を判定
- /boost: 画像にフィルターを適用
"""

import os
import io
import glob
import base64
from typing import Optional
# lifespanは削除します（起動時間を短縮するため）

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException

# HEIC対応
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from image_processing import (
    extract_color_palette,
    apply_pixel_art,
    apply_y2k_film,
    image_to_base64
)

# グローバル変数でモデルを保持（最初はNoneにしておく）
resnet_model = None
vit_model = None
device = None


def build_resnet152(num_classes: int = 2):
    """ResNet152モデルを構築"""
    model = models.resnet152(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes)
    )
    return model


def build_vit_b16(num_classes: int = 2):
    """ViT-B/16モデルを構築"""
    model = models.vit_b_16(weights=None)
    num_features = model.heads.head.in_features
    model.heads.head = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(num_features, 256),
        nn.GELU(),
        nn.Dropout(p=0.3),
        nn.Linear(256, num_classes)
    )
    return model


def ensure_model_file(model_path):
    """分割されたモデルファイルがあれば結合して復元する"""
    if os.path.exists(model_path) and os.path.getsize(model_path) > 1024 * 1024:
        return

    print(f"Reconstructing {model_path} from parts...")
    base_name = os.path.basename(model_path)
    dir_name = os.path.dirname(model_path)
    pattern = os.path.join(dir_name, base_name + ".*")
    parts = sorted([p for p in glob.glob(pattern) if not p.endswith('.pth')])

    if not parts:
        print(f"No split parts found for {model_path}")
        return

    try:
        with open(model_path, 'wb') as outfile:
            for part in parts:
                with open(part, 'rb') as infile:
                    outfile.write(infile.read())
        print(f"Successfully reconstructed {model_path}")
    except Exception as e:
        print(f"Error reconstructing model: {e}")
        if os.path.exists(model_path):
            os.remove(model_path)


def get_models():
    """
    モデルを取得する（未ロードの場合はここでロードする）
    これぞ「遅延読み込み」！
    """
    global resnet_model, vit_model, device

    # すでにロード済みならそれを返す（2回目以降は爆速）
    if resnet_model is not None and vit_model is not None:
        return resnet_model, vit_model, device

    print("Loading models for the first time...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    resnet_path = os.path.join(models_dir, 'resnet152.pth')
    vit_path = os.path.join(models_dir, 'vit_b16.pth')

    # ファイル結合
    ensure_model_file(resnet_path)
    ensure_model_file(vit_path)

    # ResNetロード
    resnet_model = build_resnet152()
    if os.path.exists(resnet_path):
        resnet_model.load_state_dict(torch.load(resnet_path, map_location=device, weights_only=False))
        print("ResNet152 loaded")
    else:
        print("Warning: ResNet152 weights not found.")
    resnet_model = resnet_model.to(device)
    resnet_model.eval()

    # ViTロード
    vit_model = build_vit_b16()
    if os.path.exists(vit_path):
        vit_model.load_state_dict(torch.load(vit_path, map_location=device, weights_only=False))
        print("ViT-B/16 loaded")
    else:
        print("Warning: ViT-B/16 weights not found.")
    vit_model = vit_model.to(device)
    vit_model.eval()

    return resnet_model, vit_model, device


# FastAPIアプリケーションの作成（lifespanは削除）
app = FastAPI(
    title="Emo-Check API",
    description="画像のエモ度を判定し、エモく加工するAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# --- Pydantic Models ---
class EmoComponent(BaseModel):
    name: str
    percentage: int
    description: str

class PredictResponse(BaseModel):
    emo_score: float
    model_used: str
    color_palette: list
    emo_components: list
    emo_comment: str

class BoostResponse(BaseModel):
    image_base64: str
    filter_applied: str

# --- Helper Functions ---
def analyze_emo_components(emo_score: float, color_palette: list) -> tuple[list[dict], str]:
    import random
    components_pool = [
        {"name": "ノスタルジー", "description": "過去への憧れや懐かしさ"},
        {"name": "儚さ", "description": "消えゆく美しさへの感傷"},
        {"name": "青春", "description": "若さと輝きの記憶"},
        {"name": "メランコリー", "description": "甘い憂鬱と物思い"},
        {"name": "夕暮れ感", "description": "一日の終わりの切なさ"},
        {"name": "孤独", "description": "静かな一人の時間"},
        {"name": "希望", "description": "未来への淡い期待"},
        {"name": "哀愁", "description": "心に染みる寂しさ"},
    ]
    random.seed(int(emo_score * 100))
    num_components = 3 if emo_score < 50 else 4
    selected = random.sample(components_pool, num_components)
    remaining = 100
    components = []
    for i, comp in enumerate(selected):
        if i == len(selected) - 1:
            pct = remaining
        else:
            pct = random.randint(15, min(45, remaining - 10 * (len(selected) - i - 1)))
            remaining -= pct
        components.append({
            "name": comp["name"],
            "percentage": pct,
            "description": comp["description"]
        })
    components.sort(key=lambda x: x["percentage"], reverse=True)
    
    comments_high = ["この写真、めちゃくちゃエモい...。", "言葉にできない感情が溢れてくる。", "これはSNSでバズる予感。", "見た瞬間、心を掴まれました。"]
    comments_mid = ["いい雰囲気出てます。", "エモさの片鱗が見える。", "悪くない。フィルターを試してみて。", "何か惹かれるものがある一枚です。"]
    comments_low = ["エモさは控えめ。", "日常の一コマって感じ。", "シンプルな写真ですね。", "これから伸びしろあり。"]

    random.seed(int(emo_score * 1000) + len(color_palette))
    if emo_score >= 70: comment = random.choice(comments_high)
    elif emo_score >= 40: comment = random.choice(comments_mid)
    else: comment = random.choice(comments_low)
    return components, comment


# --- Endpoints ---

@app.get("/")
async def root():
    """ヘルスチェック：ここは即座に返す！"""
    return {"message": "Emo-Check API is running", "status": "ok"}


@app.get("/health")
async def health_check():
    """詳細なヘルスチェック"""
    # ここでモデルの状態を確認するが、ロードはしない
    return {
        "status": "healthy",
        "models_loaded": resnet_model is not None,
        "device": str(device) if device else "not_initialized"
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(
    file: UploadFile = File(...),
    model_type: str = Form(default="resnet")
):
    """画像のエモ度を判定する"""
    
    # ★重要：ここで初めてモデルをロードする！
    # アプリ起動時ではなく、誰かが「診断」ボタンを押したときに準備する
    current_resnet, current_vit, current_device = get_models()

    allowed_types = ["image/", "application/octet-stream"]
    is_heic = file.filename and file.filename.lower().endswith(('.heic', '.heif'))

    if not is_heic and (not file.content_type or not any(file.content_type.startswith(t) for t in allowed_types)):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")
    if is_heic and not HEIC_SUPPORTED:
        raise HTTPException(status_code=400, detail="HEIC形式はサポートされていません。")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if is_heic:
            jpeg_buffer = io.BytesIO()
            image.save(jpeg_buffer, format='JPEG', quality=95)
            image_bytes = jpeg_buffer.getvalue()

        color_palette = extract_color_palette(image_bytes)
        image_tensor = transform(image).unsqueeze(0).to(current_device)

        if model_type.lower() == "vit":
            model = current_vit
            model_name = "ViT-B/16"
        else:
            model = current_resnet
            model_name = "ResNet152"

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            emo_score = probabilities[0][1].item() * 100

        emo_components, emo_comment = analyze_emo_components(emo_score, color_palette)

        return PredictResponse(
            emo_score=round(emo_score, 1),
            model_used=model_name,
            color_palette=color_palette,
            emo_components=emo_components,
            emo_comment=emo_comment
        )

    except Exception as e:
        print(f"Error in predict: {e}")
        raise HTTPException(status_code=500, detail=f"予測処理中にエラーが発生しました: {str(e)}")


@app.post("/boost", response_model=BoostResponse)
async def boost(
    file: UploadFile = File(...),
    filter_type: str = Form(...)
):
    """画像にフィルターを適用してエモく加工する"""
    allowed_types = ["image/", "application/octet-stream"]
    is_heic = file.filename and file.filename.lower().endswith(('.heic', '.heif'))

    if not is_heic and (not file.content_type or not any(file.content_type.startswith(t) for t in allowed_types)):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")
    if is_heic and not HEIC_SUPPORTED:
        raise HTTPException(status_code=400, detail="HEIC形式はサポートされていません。")

    valid_filters = ["pixel", "y2k"]
    if filter_type.lower() not in valid_filters:
        raise HTTPException(status_code=400, detail=f"無効なフィルタータイプです。")

    try:
        image_bytes = await file.read()
        if is_heic:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            jpeg_buffer = io.BytesIO()
            image.save(jpeg_buffer, format='JPEG', quality=95)
            image_bytes = jpeg_buffer.getvalue()

        if filter_type.lower() == "pixel":
            processed_bytes = apply_pixel_art(image_bytes)
            filter_name = "Pixel Art Mode"
        else:
            processed_bytes = apply_y2k_film(image_bytes)
            filter_name = "Y2K Film Mode"

        image_base64 = image_to_base64(processed_bytes)

        return BoostResponse(
            image_base64=image_base64,
            filter_applied=filter_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像加工中にエラーが発生しました: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """サーバー起動後にモデルをロード"""
    print("Pre-loading models at startup...")
    get_models()
    print("Models ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)