import os
import json
from typing import List, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from backend.models import Attraction, UserBehavior
from algorithms.item_cf import ItemCF
from algorithms.deepfm import DeepFMRecommender
from algorithms.hybrid_recommender import HybridRecommender


class RecommendService:

    def __init__(self):
        self.item_cf: Optional[ItemCF] = None
        self.deepfm: Optional[DeepFMRecommender] = None
        self.hybrid: Optional[HybridRecommender] = None
        self.models_loaded = False
        self.feature_mappings: Optional[Dict] = None

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(base_dir, "algorithms", "models")
        self.item_cf_path = os.path.join(self.models_dir, "item_cf.pkl")
        self.deepfm_path = os.path.join(self.models_dir, "deepfm.pt")
        self.mappings_path = os.path.join(self.models_dir, "feature_mappings.json")

    def load_models(self, db: Session = None):
        try:
            if os.path.exists(self.item_cf_path):
                self.item_cf = ItemCF()
                self.item_cf.load(self.item_cf_path)

            if os.path.exists(self.deepfm_path):
                if not os.path.exists(self.mappings_path) and db:
                    self.save_feature_mappings(db)

                if os.path.exists(self.mappings_path):
                    with open(self.mappings_path, "r", encoding="utf-8") as f:
                        self.feature_mappings = json.load(f)
                    feature_sizes = self.feature_mappings.get("feature_sizes", {})
                    if feature_sizes:
                        self.deepfm = DeepFMRecommender(feature_sizes)
                        self.deepfm.load(self.deepfm_path)

            if self.item_cf and self.deepfm:
                self.hybrid = HybridRecommender(self.item_cf, self.deepfm)

            self.models_loaded = True
        except Exception as e:
            print(f"Error loading models: {e}")
            self.models_loaded = False

    def save_feature_mappings(self, db: Session):
        behaviors = db.query(UserBehavior).all()
        attractions = db.query(Attraction).all()

        user_ids = sorted(set(b.user_id for b in behaviors))
        attraction_ids = sorted(a.id for a in attractions)
        cities = sorted(set(a.city for a in attractions if a.city))
        seasons = sorted(set(a.season for a in attractions if a.season))

        user_id_map = {str(uid): idx for idx, uid in enumerate(user_ids)}
        attraction_id_map = {str(aid): idx for idx, aid in enumerate(attraction_ids)}
        city_map = {c: idx for idx, c in enumerate(cities)}
        season_map = {s: idx for idx, s in enumerate(seasons)}
        reverse_attraction_id_map = {str(idx): int(aid) for aid, idx in attraction_id_map.items()}

        feature_sizes = {
            "user_id": len(user_id_map) + 1,
            "attraction_id": len(attraction_id_map) + 1,
            "city": len(city_map) + 1,
            "season": len(season_map) + 1,
            "rating_level": 6,
        }

        mappings = {
            "user_id_map": user_id_map,
            "attraction_id_map": attraction_id_map,
            "reverse_attraction_id_map": reverse_attraction_id_map,
            "city_map": city_map,
            "season_map": season_map,
            "feature_sizes": feature_sizes,
        }

        os.makedirs(self.models_dir, exist_ok=True)
        with open(self.mappings_path, "w", encoding="utf-8") as f:
            json.dump(mappings, f, ensure_ascii=False, indent=2)

    def _get_user_behaviors(self, db: Session, user_id: int) -> List[Tuple]:
        behaviors = db.query(UserBehavior).filter(UserBehavior.user_id == user_id).all()
        return [(b.user_id, b.attraction_id, b.behavior_type) for b in behaviors]

    def _get_all_behaviors(self, db: Session) -> List[Tuple]:
        behaviors = db.query(UserBehavior).all()
        return [(b.user_id, b.attraction_id, b.behavior_type) for b in behaviors]

    def _build_user_features(self, user_id: int) -> Dict:
        if not self.feature_mappings:
            return {}
        user_id_map = self.feature_mappings.get("user_id_map", {})
        return {"user_id": user_id_map.get(str(user_id), 0)}

    def _build_candidate_items(self, db: Session, user_id: int) -> List[Dict]:
        if not self.feature_mappings:
            return []

        attraction_id_map = self.feature_mappings.get("attraction_id_map", {})
        city_map = self.feature_mappings.get("city_map", {})
        season_map = self.feature_mappings.get("season_map", {})

        user_behavior_attraction_ids = [
            b.attraction_id
            for b in db.query(UserBehavior).filter(UserBehavior.user_id == user_id).all()
        ]

        query = db.query(Attraction)
        if user_behavior_attraction_ids:
            query = query.filter(~Attraction.id.in_(user_behavior_attraction_ids))
        attractions = query.all()

        candidates = []
        for attr in attractions:
            rating = attr.rating or 0
            if rating >= 4:
                rating_level = 5
            elif rating >= 3:
                rating_level = 4
            elif rating >= 2:
                rating_level = 3
            elif rating >= 1:
                rating_level = 2
            elif rating > 0:
                rating_level = 1
            else:
                rating_level = 0

            candidates.append({
                "attraction_id": attraction_id_map.get(str(attr.id), 0),
                "city": city_map.get(attr.city or "", 0),
                "season": season_map.get(attr.season or "", 0),
                "rating_level": rating_level,
                "_actual_id": attr.id,
            })

        return candidates

    def _attraction_to_dict(self, attr: Attraction) -> Dict:
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

    def get_personal_recommendations(self, db: Session, user_id: int, top_n: int = 12):
        behaviors = self._get_user_behaviors(db, user_id)
        if not behaviors:
            return self.get_popular(db, top_n)

        all_behaviors = self._get_all_behaviors(db)

        cf_results = {}
        if self.item_cf:
            cf_raw = self.item_cf.recommend(user_id, all_behaviors, top_n=top_n * 3)
            cf_results = {item_id: score for item_id, score in cf_raw}

        deepfm_results = {}
        if self.deepfm and self.feature_mappings:
            user_features = self._build_user_features(user_id)
            candidate_items = self._build_candidate_items(db, user_id)
            if candidate_items:
                idx_to_actual = {item["attraction_id"]: item["_actual_id"] for item in candidate_items}
                deepfm_raw = self.deepfm.recommend(user_features, candidate_items, top_n=top_n * 3)
                for aid_idx, score in deepfm_raw:
                    actual_id = idx_to_actual.get(aid_idx)
                    if actual_id is not None:
                        deepfm_results[actual_id] = score

        if not cf_results and not deepfm_results:
            return self.get_popular(db, top_n)

        all_items = set(cf_results.keys()) | set(deepfm_results.keys())
        cf_weight = 0.4
        deepfm_weight = 0.6
        combined = {}
        for item_id in all_items:
            combined[item_id] = (
                cf_weight * cf_results.get(item_id, 0)
                + deepfm_weight * deepfm_results.get(item_id, 0)
            )

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_n]

        attraction_ids = [aid for aid, _ in ranked]
        attractions = db.query(Attraction).filter(Attraction.id.in_(attraction_ids)).all()
        attr_map = {a.id: a for a in attractions}

        result = []
        for aid, score in ranked:
            if aid in attr_map:
                result.append({"attraction": self._attraction_to_dict(attr_map[aid]), "score": score})

        return result

    def get_similar_attractions(self, attraction_id: int, top_n: int = 10):
        if not self.item_cf or attraction_id not in self.item_cf.item_similarity:
            return []
        similar = self.item_cf.item_similarity[attraction_id]
        sorted_similar = sorted(similar.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return sorted_similar

    def get_popular(self, db: Session, top_n: int = 12):
        attractions = db.query(Attraction).order_by(Attraction.rating.desc()).limit(top_n).all()
        return [{"attraction": self._attraction_to_dict(a), "score": a.rating or 0} for a in attractions]

    def get_seasonal(self, db: Session, season: str, top_n: int = 12):
        attractions = (
            db.query(Attraction)
            .filter(Attraction.season.like(f"%{season}%"))
            .order_by(Attraction.rating.desc())
            .limit(top_n)
            .all()
        )
        return [{"attraction": self._attraction_to_dict(a), "score": a.rating or 0} for a in attractions]


recommend_service = RecommendService()
