"""
Emo-Check: 画像処理モジュール
- カラーパレット抽出
- Pixel Art Mode (ドット絵化)
- Y2K Film Mode (フィルム風加工)
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
import base64
from typing import List, Tuple


def extract_color_palette(image_bytes: bytes, n_colors: int = 5) -> List[dict]:
    """
    画像からドミナントカラー（主要な色）を抽出する

    Args:
        image_bytes: 画像のバイトデータ
        n_colors: 抽出する色の数（デフォルト5）

    Returns:
        色情報のリスト [{"hex": "#FF6B6B", "rgb": [255, 107, 107], "percentage": 25.5}, ...]
    """
    # バイトデータをnumpy配列に変換
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("画像の読み込みに失敗しました")

    # BGR -> RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # リサイズして処理を高速化
    image_small = cv2.resize(image_rgb, (150, 150))

    # 2D配列に変換 (height * width, 3)
    pixels = image_small.reshape(-1, 3)

    # K-meansクラスタリングでドミナントカラーを抽出
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # 各クラスタの割合を計算
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    percentages = counts / len(kmeans.labels_) * 100

    # 結果を整形
    colors = []
    for i, (center, percentage) in enumerate(zip(kmeans.cluster_centers_, percentages)):
        r, g, b = int(center[0]), int(center[1]), int(center[2])
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append({
            "hex": hex_color,
            "rgb": [r, g, b],
            "percentage": round(percentage, 1)
        })

    # 割合の大きい順にソート
    colors.sort(key=lambda x: x["percentage"], reverse=True)

    return colors


def apply_pixel_art(image_bytes: bytes, pixel_size: int = 8, color_count: int = 16) -> bytes:
    """
    画像をドット絵風に変換する

    Args:
        image_bytes: 画像のバイトデータ
        pixel_size: ピクセルのサイズ（大きいほど粗いドット絵）
        color_count: 使用する色の数

    Returns:
        加工後の画像のバイトデータ
    """
    # バイトデータをnumpy配列に変換
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("画像の読み込みに失敗しました")

    height, width = image.shape[:2]

    # 小さくリサイズしてから拡大（ドット絵効果）
    small_width = width // pixel_size
    small_height = height // pixel_size

    # 縮小
    small = cv2.resize(image, (small_width, small_height), interpolation=cv2.INTER_LINEAR)

    # 減色処理（K-meansでパレット化）
    pixels = small.reshape(-1, 3).astype(np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(pixels, color_count, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # 各ピクセルを最も近いクラスタの色に置き換え
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized = quantized.reshape(small.shape)

    # ニアレストネイバーで拡大（シャープなドット感を維持）
    result = cv2.resize(quantized, (width, height), interpolation=cv2.INTER_NEAREST)

    # バイトデータに変換
    _, buffer = cv2.imencode('.png', result)
    return buffer.tobytes()


def apply_y2k_film(image_bytes: bytes) -> bytes:
    """
    Y2K/フィルム風の加工を適用する
    - ノイズ追加
    - 彩度調整
    - 右下にオレンジ色の日付スタンプ

    Args:
        image_bytes: 画像のバイトデータ

    Returns:
        加工後の画像のバイトデータ
    """
    # バイトデータをnumpy配列に変換
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("画像の読み込みに失敗しました")

    height, width = image.shape[:2]

    # 1. 彩度とコントラストを調整（フィルム感）
    # HSVに変換
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)

    # 彩度を上げる
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)

    # 明度を少し下げる
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.95, 0, 255)

    image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # 2. 色温度を暖かくする（オレンジ/イエロー寄り）
    # BGRチャンネルを調整
    image = image.astype(np.float32)
    image[:, :, 2] = np.clip(image[:, :, 2] * 1.1, 0, 255)  # Red up
    image[:, :, 1] = np.clip(image[:, :, 1] * 1.02, 0, 255)  # Green slightly up
    image[:, :, 0] = np.clip(image[:, :, 0] * 0.9, 0, 255)  # Blue down
    image = image.astype(np.uint8)

    # 3. フィルムグレイン（ノイズ）を追加
    noise = np.random.normal(0, 12, image.shape).astype(np.float32)
    noisy_image = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # 4. 軽いビネット効果
    rows, cols = noisy_image.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols * 0.5)
    kernel_y = cv2.getGaussianKernel(rows, rows * 0.5)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    vignette = noisy_image.copy().astype(np.float32)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * (0.4 + 0.6 * mask)
    vignette = np.clip(vignette, 0, 255).astype(np.uint8)

    # 5. OpenCVからPILに変換して日付スタンプを追加
    pil_image = Image.fromarray(cv2.cvtColor(vignette, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    # 日付テキスト（Y2K風のフォーマット）
    date_text = datetime.now().strftime("'%y %m %d")

    # フォントサイズを画像サイズに応じて調整
    font_size = max(int(min(width, height) * 0.06), 16)

    try:
        # システムフォントを試す
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            # フォールバック
            font = ImageFont.load_default()

    # テキストのバウンディングボックスを取得
    bbox = draw.textbbox((0, 0), date_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 右下に配置（マージン付き）
    margin = int(min(width, height) * 0.03)
    x = width - text_width - margin
    y = height - text_height - margin

    # オレンジ色でテキストを描画
    orange_color = (255, 140, 0)  # オレンジ
    draw.text((x, y), date_text, font=font, fill=orange_color)

    # PILからOpenCVに戻す
    result = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # バイトデータに変換
    _, buffer = cv2.imencode('.png', result)
    return buffer.tobytes()


def image_to_base64(image_bytes: bytes) -> str:
    """画像バイトデータをBase64文字列に変換"""
    return base64.b64encode(image_bytes).decode('utf-8')


def base64_to_image(base64_str: str) -> bytes:
    """Base64文字列を画像バイトデータに変換"""
    return base64.b64decode(base64_str)
