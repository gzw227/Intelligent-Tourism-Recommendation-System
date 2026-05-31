from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Attraction

router = APIRouter(prefix="/api/attractions", tags=["景点"])


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


@router.get("/list")
def get_attraction_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    city: Optional[str] = None,
    keyword: Optional[str] = None,
    min_rating: Optional[float] = None,
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Attraction)

        if city:
            query = query.filter(Attraction.city == city)
        if keyword:
            query = query.filter(
                (Attraction.name.like(f"%{keyword}%"))
                | (Attraction.description.like(f"%{keyword}%"))
            )
        if min_rating is not None:
            query = query.filter(Attraction.rating >= min_rating)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "code": 200,
            "message": "获取景点列表成功",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [attraction_to_dict(a) for a in items],
            },
        }
    except Exception as e:
        return {"code": 500, "message": f"获取景点列表失败: {str(e)}", "data": None}


@router.get("/detail/{attraction_id}")
def get_attraction_detail(attraction_id: int, db: Session = Depends(get_db)):
    try:
        attr = db.query(Attraction).filter(Attraction.id == attraction_id).first()
        if not attr:
            return {"code": 404, "message": "景点不存在", "data": None}

        return {"code": 200, "message": "获取景点详情成功", "data": attraction_to_dict(attr)}
    except Exception as e:
        return {"code": 500, "message": f"获取景点详情失败: {str(e)}", "data": None}


@router.get("/cities")
def get_cities(db: Session = Depends(get_db)):
    try:
        cities = db.query(Attraction.city).distinct().all()
        city_list = [c[0] for c in cities if c[0]]

        return {"code": 200, "message": "获取城市列表成功", "data": city_list}
    except Exception as e:
        return {"code": 500, "message": f"获取城市列表失败: {str(e)}", "data": None}


@router.get("/search")
def search_attractions(
    keyword: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Attraction).filter(
            (Attraction.name.like(f"%{keyword}%"))
            | (Attraction.description.like(f"%{keyword}%"))
        )

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "code": 200,
            "message": "搜索景点成功",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [attraction_to_dict(a) for a in items],
            },
        }
    except Exception as e:
        return {"code": 500, "message": f"搜索景点失败: {str(e)}", "data": None}
