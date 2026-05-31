from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import UserBehavior, Attraction

router = APIRouter(prefix="/api/behavior", tags=["行为"])


class BehaviorRequest(BaseModel):
    user_id: int
    attraction_id: int


def attraction_to_dict(attr: Attraction) -> dict:
    return {
        "id": attr.id,
        "name": attr.name,
        "city": attr.city,
        "address": attr.address,
        "description": attr.description,
        "open_time": attr.open_time,
        "image_url": attr.image_url,
        "rating": attr.rating,
        "play_time": attr.play_time,
        "season": attr.season,
        "ticket": attr.ticket,
        "tips": attr.tips,
        "source_url": attr.source_url,
    }


@router.post("/browse")
def record_browse(req: BehaviorRequest, db: Session = Depends(get_db)):
    try:
        behavior = UserBehavior(
            user_id=req.user_id,
            attraction_id=req.attraction_id,
            behavior_type="browse",
        )
        db.add(behavior)
        db.commit()

        return {"code": 200, "message": "记录浏览行为成功", "data": None}
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"记录浏览行为失败: {str(e)}", "data": None}


@router.post("/collect")
def collect_attraction(req: BehaviorRequest, db: Session = Depends(get_db)):
    try:
        existing = db.query(UserBehavior).filter(
            UserBehavior.user_id == req.user_id,
            UserBehavior.attraction_id == req.attraction_id,
            UserBehavior.behavior_type == "collect",
        ).first()
        if existing:
            return {"code": 400, "message": "已收藏该景点", "data": None}

        behavior = UserBehavior(
            user_id=req.user_id,
            attraction_id=req.attraction_id,
            behavior_type="collect",
        )
        db.add(behavior)
        db.commit()

        return {"code": 200, "message": "收藏成功", "data": None}
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"收藏失败: {str(e)}", "data": None}


@router.delete("/collect")
def cancel_collect(req: BehaviorRequest, db: Session = Depends(get_db)):
    try:
        behavior = db.query(UserBehavior).filter(
            UserBehavior.user_id == req.user_id,
            UserBehavior.attraction_id == req.attraction_id,
            UserBehavior.behavior_type == "collect",
        ).first()
        if not behavior:
            return {"code": 404, "message": "未找到收藏记录", "data": None}

        db.delete(behavior)
        db.commit()

        return {"code": 200, "message": "取消收藏成功", "data": None}
    except Exception as e:
        db.rollback()
        return {"code": 500, "message": f"取消收藏失败: {str(e)}", "data": None}


@router.get("/collects/{user_id}")
def get_collects(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        query = (
            db.query(UserBehavior, Attraction)
            .join(Attraction, UserBehavior.attraction_id == Attraction.id)
            .filter(
                UserBehavior.user_id == user_id,
                UserBehavior.behavior_type == "collect",
            )
            .order_by(UserBehavior.created_at.desc())
        )

        total = query.count()
        results = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for behavior, attraction in results:
            items.append({
                "behavior_id": behavior.id,
                "created_at": (
                    behavior.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if behavior.created_at
                    else None
                ),
                "attraction": attraction_to_dict(attraction),
            })

        return {
            "code": 200,
            "message": "获取收藏列表成功",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items,
            },
        }
    except Exception as e:
        return {"code": 500, "message": f"获取收藏列表失败: {str(e)}", "data": None}


@router.get("/history/{user_id}")
def get_history(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        query = (
            db.query(UserBehavior, Attraction)
            .join(Attraction, UserBehavior.attraction_id == Attraction.id)
            .filter(
                UserBehavior.user_id == user_id,
                UserBehavior.behavior_type == "browse",
            )
            .order_by(UserBehavior.created_at.desc())
        )

        total = query.count()
        results = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for behavior, attraction in results:
            items.append({
                "behavior_id": behavior.id,
                "created_at": (
                    behavior.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if behavior.created_at
                    else None
                ),
                "attraction": attraction_to_dict(attraction),
            })

        return {
            "code": 200,
            "message": "获取浏览历史成功",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items,
            },
        }
    except Exception as e:
        return {"code": 500, "message": f"获取浏览历史失败: {str(e)}", "data": None}


@router.get("/is_collected")
def is_collected(
    user_id: int = Query(...),
    attraction_id: int = Query(...),
    db: Session = Depends(get_db),
):
    try:
        behavior = db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.attraction_id == attraction_id,
            UserBehavior.behavior_type == "collect",
        ).first()

        return {
            "code": 200,
            "message": "查询成功",
            "data": {"is_collected": behavior is not None},
        }
    except Exception as e:
        return {"code": 500, "message": f"查询失败: {str(e)}", "data": None}
