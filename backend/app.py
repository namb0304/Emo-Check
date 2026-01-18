"""
Emo-Check: FastAPI バックエンド
- /predict: 画像のエモ度を判定
- /boost: 画像にフィルターを適用
"""

import os
import io
import base64
from typing import Optional
from contextlib import asynccontextmanager

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from image_processing import (
    extract_color_palette,
    apply_pixel_art,
    apply_y2k_film,
    image_to_base64
)

# グローバル変数でモデルを保持
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


def load_models():
    """モデルをロード"""
    global resnet_model, vit_model, device

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # モデルファイルのパス
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    resnet_path = os.path.join(models_dir, 'resnet152.pth')
    vit_path = os.path.join(models_dir, 'vit_b16.pth')

    # ResNet152のロード
    resnet_model = build_resnet152()
    if os.path.exists(resnet_path):
        resnet_model.load_state_dict(torch.load(resnet_path, map_location=device))
        print(f"ResNet152 loaded from {resnet_path}")
    else:
        print(f"Warning: ResNet152 weights not found at {resnet_path}. Using random weights.")
    resnet_model = resnet_model.to(device)
    resnet_model.eval()

    # ViT-B/16のロード
    vit_model = build_vit_b16()
    if os.path.exists(vit_path):
        vit_model.load_state_dict(torch.load(vit_path, map_location=device))
        print(f"ViT-B/16 loaded from {vit_path}")
    else:
        print(f"Warning: ViT-B/16 weights not found at {vit_path}. Using random weights.")
    vit_model = vit_model.to(device)
    vit_model.eval()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時にモデルをロード
    load_models()
    yield
    # シャットダウン時の処理（必要に応じて）


# FastAPIアプリケーションの作成
app = FastAPI(
    title="Emo-Check API",
    description="画像のエモ度を判定し、エモく加工するAPI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンに制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 画像の前処理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class PredictResponse(BaseModel):
    """予測結果のレスポンス"""
    emo_score: float
    model_used: str
    color_palette: list


class BoostResponse(BaseModel):
    """画像加工結果のレスポンス"""
    image_base64: str
    filter_applied: str


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "Emo-Check API is running", "status": "ok"}


@app.get("/health")
async def health_check():
    """詳細なヘルスチェック"""
    return {
        "status": "healthy",
        "models": {
            "resnet152": resnet_model is not None,
            "vit_b16": vit_model is not None
        },
        "device": str(device)
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(
    file: UploadFile = File(...),
    model_type: str = Form(default="resnet")
):
    """
    画像のエモ度を判定する

    Args:
        file: アップロードされた画像ファイル
        model_type: 使用するモデル ("resnet" or "vit")

    Returns:
        emo_score: エモ度スコア (0-100%)
        model_used: 使用したモデル名
        color_palette: 抽出したカラーパレット
    """
    # ファイル形式のチェック
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    try:
        # 画像データを読み込み
        image_bytes = await file.read()

        # カラーパレットを抽出
        color_palette = extract_color_palette(image_bytes)

        # PILで画像を開く
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = transform(image).unsqueeze(0).to(device)

        # モデル選択と推論
        if model_type.lower() == "vit":
            model = vit_model
            model_name = "ViT-B/16"
        else:
            model = resnet_model
            model_name = "ResNet152"

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            emo_score = probabilities[0][1].item() * 100  # class_1 (Emo) の確率

        return PredictResponse(
            emo_score=round(emo_score, 1),
            model_used=model_name,
            color_palette=color_palette
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測処理中にエラーが発生しました: {str(e)}")


@app.post("/boost", response_model=BoostResponse)
async def boost(
    file: UploadFile = File(...),
    filter_type: str = Form(...)
):
    """
    画像にフィルターを適用してエモく加工する

    Args:
        file: アップロードされた画像ファイル
        filter_type: フィルタータイプ ("pixel" or "y2k")

    Returns:
        image_base64: Base64エンコードされた加工後画像
        filter_applied: 適用されたフィルター名
    """
    # ファイル形式のチェック
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    # フィルタータイプのチェック
    valid_filters = ["pixel", "y2k"]
    if filter_type.lower() not in valid_filters:
        raise HTTPException(
            status_code=400,
            detail=f"無効なフィルタータイプです。使用可能: {', '.join(valid_filters)}"
        )

    try:
        # 画像データを読み込み
        image_bytes = await file.read()

        # フィルター適用
        if filter_type.lower() == "pixel":
            processed_bytes = apply_pixel_art(image_bytes)
            filter_name = "Pixel Art Mode"
        else:  # y2k
            processed_bytes = apply_y2k_film(image_bytes)
            filter_name = "Y2K Film Mode"

        # Base64エンコード
        image_base64 = image_to_base64(processed_bytes)

        return BoostResponse(
            image_base64=image_base64,
            filter_applied=filter_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像加工中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
