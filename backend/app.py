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
        resnet_model.load_state_dict(torch.load(resnet_path, map_location=device, weights_only=False))
        print(f"ResNet152 loaded from {resnet_path}")
    else:
        print(f"Warning: ResNet152 weights not found at {resnet_path}. Using random weights.")
    resnet_model = resnet_model.to(device)
    resnet_model.eval()

    # ViT-B/16のロード
    vit_model = build_vit_b16()
    if os.path.exists(vit_path):
        vit_model.load_state_dict(torch.load(vit_path, map_location=device, weights_only=False))
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


class EmoComponent(BaseModel):
    """エモ成分"""
    name: str
    percentage: int
    description: str


class PredictResponse(BaseModel):
    """予測結果のレスポンス"""
    emo_score: float
    model_used: str
    color_palette: list
    emo_components: list
    emo_comment: str


class BoostResponse(BaseModel):
    """画像加工結果のレスポンス"""
    image_base64: str
    filter_applied: str


def analyze_emo_components(emo_score: float, color_palette: list) -> tuple[list[dict], str]:
    """
    エモ成分を分析する
    スコアとカラーパレットから「エモさ」の内訳を生成
    """
    import random

    # 成分候補
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

    # カラーパレットの色味で成分を調整
    has_warm = any(c["rgb"][0] > c["rgb"][2] for c in color_palette[:3])
    has_cool = any(c["rgb"][2] > c["rgb"][0] for c in color_palette[:3])
    has_dark = any(sum(c["rgb"]) < 300 for c in color_palette[:3])

    # スコアに基づいて3-4個の成分を選択
    random.seed(int(emo_score * 100))
    num_components = 3 if emo_score < 50 else 4
    selected = random.sample(components_pool, num_components)

    # パーセンテージを割り当て（合計100%）
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

    # パーセンテージでソート
    components.sort(key=lambda x: x["percentage"], reverse=True)

    # コメント生成
    comments_high = [
        "この写真、めちゃくちゃエモい...。心に響く一枚です。",
        "言葉にできない感情が溢れてくる。最高にエモい。",
        "これはSNSでバズる予感。エモさ満点です。",
        "見た瞬間、心を掴まれました。素敵な一枚。",
    ]
    comments_mid = [
        "いい雰囲気出てます。もう少しでエモさ全開かも。",
        "エモさの片鱗が見える。加工でさらに引き立つかも。",
        "悪くない。フィルターを試してみて。",
        "何か惹かれるものがある一枚です。",
    ]
    comments_low = [
        "エモさは控えめ。でも加工次第で化けるかも？",
        "日常の一コマって感じ。フィルターで遊んでみよう。",
        "シンプルな写真ですね。Y2Kフィルターがおすすめ。",
        "これから伸びしろあり。加工してみて。",
    ]

    random.seed(int(emo_score * 1000) + len(color_palette))
    if emo_score >= 70:
        comment = random.choice(comments_high)
    elif emo_score >= 40:
        comment = random.choice(comments_mid)
    else:
        comment = random.choice(comments_low)

    return components, comment


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
    # ファイル形式のチェック（HEIC含む）
    allowed_types = ["image/", "application/octet-stream"]  # HEICはoctet-streamで来ることがある
    is_heic = file.filename and file.filename.lower().endswith(('.heic', '.heif'))

    if not is_heic and (not file.content_type or not any(file.content_type.startswith(t) for t in allowed_types)):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    if is_heic and not HEIC_SUPPORTED:
        raise HTTPException(status_code=400, detail="HEIC形式はサポートされていません。pillow-heifをインストールしてください。")

    try:
        # 画像データを読み込み
        image_bytes = await file.read()

        # PILで画像を開く（HEICも自動対応）
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # HEIC等の場合、image_bytesをJPEG形式に変換してからカラーパレット抽出
        if is_heic:
            jpeg_buffer = io.BytesIO()
            image.save(jpeg_buffer, format='JPEG', quality=95)
            image_bytes = jpeg_buffer.getvalue()

        # カラーパレットを抽出
        color_palette = extract_color_palette(image_bytes)
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

        # エモ成分分析
        emo_components, emo_comment = analyze_emo_components(emo_score, color_palette)

        return PredictResponse(
            emo_score=round(emo_score, 1),
            model_used=model_name,
            color_palette=color_palette,
            emo_components=emo_components,
            emo_comment=emo_comment
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
    # ファイル形式のチェック（HEIC含む）
    allowed_types = ["image/", "application/octet-stream"]
    is_heic = file.filename and file.filename.lower().endswith(('.heic', '.heif'))

    if not is_heic and (not file.content_type or not any(file.content_type.startswith(t) for t in allowed_types)):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    if is_heic and not HEIC_SUPPORTED:
        raise HTTPException(status_code=400, detail="HEIC形式はサポートされていません。pillow-heifをインストールしてください。")

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

        # HEIC形式の場合、JPEGに変換
        if is_heic:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            jpeg_buffer = io.BytesIO()
            image.save(jpeg_buffer, format='JPEG', quality=95)
            image_bytes = jpeg_buffer.getvalue()

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
