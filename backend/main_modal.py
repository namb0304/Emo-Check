import sys
import modal

# アプリ名を指定
app = modal.App("emo-check-gpu")

# コンテナイメージの定義
image = (
    modal.Image.debian_slim()
    .apt_install("libgl1-mesa-glx", "libglib2.0-0")
    .pip_install(
        "fastapi",
        "uvicorn",
        "python-multipart",
        "Pillow",
        "torch",
        "torchvision",
        "numpy",
        "scikit-learn",
        "pillow-heif"
    )
    .add_local_dir("./backend", remote_path="/root/backend")
)

# FastAPIアプリをラップする関数
@app.function(
    image=image,
    gpu="T4",     # GPUを指定
    timeout=600,  # タイムアウト10分
)
@modal.asgi_app()
def fastapi_app():
    # パスを通す
    sys.path.append("/root")
    # backendフォルダの中のapp.pyからappオブジェクトをインポート
    from backend.app import app
    return app
