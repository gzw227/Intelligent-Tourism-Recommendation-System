import os
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.recommend_service import recommend_service

router = APIRouter(prefix="/api/model", tags=["模型"])


@router.post("/train")
def train_models(db: Session = Depends(get_db)):
    try:
        from algorithms.train import main as train_main

        train_main()
        recommend_service.save_feature_mappings(db)
        recommend_service.load_models(db)
        return {"code": 200, "message": "训练完成", "data": None}
    except Exception as e:
        return {"code": 500, "message": f"训练失败: {str(e)}", "data": None}


@router.get("/status")
def get_model_status():
    try:
        status = {
            "models_loaded": recommend_service.models_loaded,
            "item_cf": {
                "loaded": recommend_service.item_cf is not None,
                "file_exists": os.path.exists(recommend_service.item_cf_path),
            },
            "deepfm": {
                "loaded": recommend_service.deepfm is not None,
                "file_exists": os.path.exists(recommend_service.deepfm_path),
            },
        }

        for model_key, path_attr in [("item_cf", "item_cf_path"), ("deepfm", "deepfm_path")]:
            path = getattr(recommend_service, path_attr)
            if os.path.exists(path):
                stat = os.stat(path)
                status[model_key]["file_size"] = stat.st_size
                status[model_key]["last_modified"] = datetime.fromtimestamp(
                    stat.st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")

        return {"code": 200, "message": "获取模型状态成功", "data": status}
    except Exception as e:
        return {"code": 500, "message": f"获取模型状态失败: {str(e)}", "data": None}


@router.post("/reload")
def reload_models(db: Session = Depends(get_db)):
    try:
        recommend_service.load_models(db)
        return {"code": 200, "message": "模型重新加载成功", "data": None}
    except Exception as e:
        return {"code": 500, "message": f"模型重新加载失败: {str(e)}", "data": None}
