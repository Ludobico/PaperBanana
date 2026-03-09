import os
import sys
import yaml
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).parent.parent

def create_env_from_yaml():
    env_path = ROOT / ".env"
    if env_path.exists():
        print("[setup] .env already exists, skipping")
        return

    configs_dir = ROOT / "configs"
    config_path = configs_dir / "model_config.yaml"
    template_path = configs_dir / "model_config.template.yaml"

    # template에서 yaml 복사 (demo.py와 동일한 로직)
    if not config_path.exists() and template_path.exists():
        print(f"[setup] {config_path.name} not found. Auto-generating from template")
        shutil.copy2(template_path, config_path)

    if not config_path.exists():
        print("[setup] WARNING: No config yaml found, skipping .env creation")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    
    mapping = {
        "GOOGLE_API_KEY":    ("api_keys",  "google_api_key"),
        "ANTHROPIC_API_KEY": ("api_keys",  "anthropic_api_key"),
        "OPENAI_API_KEY":    ("api_keys",  "openai_api_key"),
        "MODEL_NAME":        ("defaults",  "model_name"),
        "IMAGE_MODEL_NAME":  ("defaults",  "image_model_name"),
    }

    lines = []
    for env_var, (section, key) in mapping.items():
        val = cfg.get(section, {}).get(key, "")
        lines.append(f'{env_var}={val or ""}')

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[setup] .env created from {config_path.name}")

def download_dataset():
    data_dir = ROOT / "data" / "PaperBananaBench"
    sentinel = data_dir / "diagram" / "test.json"

    if sentinel.exists():
        print("[setup] Dataset already present, skipping download")
        return

    print("[setup] Downloading PaperBananaBench from HuggingFace...")
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="dwzhu/PaperBananaBench",
            repo_type="dataset",
            local_dir=str(data_dir),
        )
        print(f"[setup] Dataset downloaded to {data_dir}")
    except Exception as e:
        print(f"[setup] WARNING: Dataset download failed: {e}")
        return
    
    zip_path = data_dir / "PaperBananaBench.zip"
    if not zip_path.exists():
        print("[setup] WARNING: PaperBananaBench.zip not found, skipping extraction")
        return

    tmp_extract = data_dir / "_tmp_extract"
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_extract)

        # 3) 중첩 폴더 해소: _tmp_extract/PaperBananaBench/* → data/PaperBananaBench/*
        nested_dir = tmp_extract / "PaperBananaBench"
        if nested_dir.is_dir():
            for item in nested_dir.iterdir():
                dest = data_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))

        # 4) 임시 폴더 & zip 정리
        shutil.rmtree(tmp_extract)
        zip_path.unlink()
        print("[setup] Extraction complete, zip removed")

    except Exception as e:
        print(f"[setup] WARNING: Extraction failed: {e}")
        if tmp_extract.exists():
            shutil.rmtree(tmp_extract)



if __name__ == "__main__":
    print("=== PaperBanana Setup ===")
    create_env_from_yaml()
    download_dataset()
    print("=== Setup Complete ===")