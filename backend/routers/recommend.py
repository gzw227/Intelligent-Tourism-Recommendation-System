from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Attraction
from backend.services.recommend_service import recommend_service

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


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


@router.get("/personal/{user_id}")
def get_personal_recommendations(
    user_id: int,
    top_n: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        results = recommend_service.get_personal_recommendations(db, user_id, top_n)
        return {"code": 200, "message": "获取个性化推荐成功", "data": results}
    except Exception as e:
        return {"code": 500, "message": f"获取个性化推荐失败: {str(e)}", "data": None}


@router.get("/popular")
def get_popular(
    top_n: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        results = recommend_service.get_popular(db, top_n)
        return {"code": 200, "message": "获取热门景点成功", "data": results}
    except Exception as e:
        return {"code": 500, "message": f"获取热门景点失败: {str(e)}", "data": None}


@router.get("/similar/{attraction_id}")
def get_similar_attractions(
    attraction_id: int,
    top_n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        similar = recommend_service.get_similar_attractions(attraction_id, top_n)
        if not similar:
            return {"code": 200, "message": "暂无相似景点", "data": []}

        attraction_ids = [aid for aid, _ in similar]
        attractions = db.query(Attraction).filter(Attraction.id.in_(attraction_ids)).all()
        attr_map = {a.id: a for a in attractions}

        result = []
        for aid, score in similar:
            if aid in attr_map:
                result.append({"attraction": attraction_to_dict(attr_map[aid]), "score": score})

        return {"code": 200, "message": "获取相似景点成功", "data": result}
    except Exception as e:
        return {"code": 500, "message": f"获取相似景点失败: {str(e)}", "data": None}


@router.get("/seasonal")
def get_seasonal_recommendations(
    season: str = Query(..., min_length=1),
    top_n: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        results = recommend_service.get_seasonal(db, season, top_n)
        return {"code": 200, "message": "获取季节推荐成功", "data": results}
    except Exception as e:
        return {"code": 500, "message": f"获取季节推荐失败: {str(e)}", "data": None}
