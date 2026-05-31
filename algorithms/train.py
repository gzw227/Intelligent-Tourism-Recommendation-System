import os
import sys
import random
import json
import pymysql
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.item_cf import ItemCF
from algorithms.deepfm import DeepFMRecommender

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "travel_recommend",
    "charset": "utf8mb4"
}

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
ITEM_CF_MODEL_PATH = os.path.join(MODELS_DIR, "item_cf.pkl")
DEEPFM_MODEL_PATH = os.path.join(MODELS_DIR, "deepfm.pt")


def load_behaviors(cursor):
    sql = "SELECT user_id, attraction_id, behavior_type FROM user_behaviors"
    cursor.execute(sql)
    rows = cursor.fetchall()
    behaviors = [(row[0], row[1], row[2]) for row in rows]
    print(f"Loaded {len(behaviors)} behavior records")
    return behaviors


def load_attractions(cursor):
    sql = "SELECT id, city, season, rating FROM attractions"
    cursor.execute(sql)
    rows = cursor.fetchall()
    attractions = {}
    for row in rows:
        attractions[row[0]] = {
            "attraction_id": row[0],
            "city": row[1],
            "season": row[2],
            "rating": row[3]
        }
    print(f"Loaded {len(attractions)} attractions")
    return attractions


def train_item_cf(behaviors):
    print("\n" + "=" * 50)
    print("Training ItemCF Model")
    print("=" * 50)
    model = ItemCF()
    model.train(behaviors)
    model.save(ITEM_CF_MODEL_PATH)
    print(f"ItemCF model saved to {ITEM_CF_MODEL_PATH}")
    print(f"Number of items with similarity data: {len(model.item_similarity)}")
    return model


def build_feature_index(behaviors, attractions):
    user_ids = set()
    city_set = set()
    season_set = set()

    for user_id, attraction_id, _ in behaviors:
        user_ids.add(user_id)
        if attraction_id in attractions:
            attr = attractions[attraction_id]
            if attr["city"]:
                city_set.add(attr["city"])
            if attr["season"]:
                season_set.add(attr["season"])

    user_id_map = {uid: idx for idx, uid in enumerate(sorted(user_ids))}
    city_map = {c: idx for idx, c in enumerate(sorted(city_set))}
    season_map = {s: idx for idx, s in enumerate(sorted(season_set))}

    rating_levels = 6

    attraction_id_map = {aid: idx for idx, aid in enumerate(sorted(attractions.keys()))}

    feature_sizes = {
        "user_id": len(user_id_map) + 1,
        "attraction_id": len(attraction_id_map) + 1,
        "city": len(city_map) + 1,
        "season": len(season_map) + 1,
        "rating_level": rating_levels
    }

    return user_id_map, attraction_id_map, city_map, season_map, feature_sizes


def prepare_deepfm_data(behaviors, attractions, user_id_map, attraction_id_map, city_map, season_map):
    print("\nPreparing DeepFM training data...")

    user_pos_items = {}
    for user_id, attraction_id, behavior_type in behaviors:
        if behavior_type in ("collect", "rate"):
            if user_id not in user_pos_items:
                user_pos_items[user_id] = set()
            user_pos_items[user_id].add(attraction_id)

    train_data = []
    all_attraction_ids = list(attractions.keys())

    for user_id, pos_items in user_pos_items.items():
        for attraction_id in pos_items:
            attr = attractions.get(attraction_id, {})
            rating = attr.get("rating", 0)
            if rating is not None and rating >= 4:
                rating_level = 5
            elif rating is not None and rating >= 3:
                rating_level = 4
            elif rating is not None and rating >= 2:
                rating_level = 3
            elif rating is not None and rating >= 1:
                rating_level = 2
            elif rating is not None and rating > 0:
                rating_level = 1
            else:
                rating_level = 0

            sample = {
                "user_id": user_id_map.get(user_id, 0),
                "attraction_id": attraction_id_map.get(attraction_id, 0),
                "city": city_map.get(attr.get("city", ""), 0),
                "season": season_map.get(attr.get("season", ""), 0),
                "rating_level": rating_level,
                "label": 1.0
            }
            train_data.append(sample)

        num_neg = min(len(pos_items) * 2, len(all_attraction_ids) - len(pos_items))
        neg_items = random.sample(
            [aid for aid in all_attraction_ids if aid not in pos_items],
            min(num_neg, len(all_attraction_ids) - len(pos_items))
        )
        for attraction_id in neg_items:
            attr = attractions.get(attraction_id, {})
            rating = attr.get("rating", 0)
            if rating is not None and rating >= 4:
                rating_level = 5
            elif rating is not None and rating >= 3:
                rating_level = 4
            elif rating is not None and rating >= 2:
                rating_level = 3
            elif rating is not None and rating >= 1:
                rating_level = 2
            elif rating is not None and rating > 0:
                rating_level = 1
            else:
                rating_level = 0

            sample = {
                "user_id": user_id_map.get(user_id, 0),
                "attraction_id": attraction_id_map.get(attraction_id, 0),
                "city": city_map.get(attr.get("city", ""), 0),
                "season": season_map.get(attr.get("season", ""), 0),
                "rating_level": rating_level,
                "label": 0.0
            }
            train_data.append(sample)

    random.shuffle(train_data)
    print(f"DeepFM training samples: {len(train_data)} (positive + negative)")
    return train_data


def train_deepfm(train_data, feature_sizes):
    print("\n" + "=" * 50)
    print("Training DeepFM Model")
    print("=" * 50)
    recommender = DeepFMRecommender(feature_sizes, embedding_dim=16)
    recommender.train_model(train_data, epochs=20, batch_size=256)
    recommender.save(DEEPFM_MODEL_PATH)
    print(f"DeepFM model saved to {DEEPFM_MODEL_PATH}")
    return recommender


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("Connecting to database...")
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        behaviors = load_behaviors(cursor)
        attractions = load_attractions(cursor)

        if not behaviors:
            print("No behavior data found. Exiting.")
            return

        item_cf_model = train_item_cf(behaviors)

        user_id_map, attraction_id_map, city_map, season_map, feature_sizes = build_feature_index(
            behaviors, attractions
        )
        print(f"\nFeature sizes: {feature_sizes}")

        deepfm_train_data = prepare_deepfm_data(
            behaviors, attractions, user_id_map, attraction_id_map, city_map, season_map
        )

        if not deepfm_train_data:
            print("No DeepFM training data. Skipping DeepFM training.")
        else:
            deepfm_model = train_deepfm(deepfm_train_data, feature_sizes)

        reverse_attraction_id_map = {str(idx): int(aid) for aid, idx in attraction_id_map.items()}
        mappings = {
            "user_id_map": {str(k): v for k, v in user_id_map.items()},
            "attraction_id_map": {str(k): v for k, v in attraction_id_map.items()},
            "reverse_attraction_id_map": reverse_attraction_id_map,
            "city_map": city_map,
            "season_map": season_map,
            "feature_sizes": feature_sizes,
        }
        mappings_path = os.path.join(MODELS_DIR, "feature_mappings.json")
        with open(mappings_path, "w", encoding="utf-8") as f:
            json.dump(mappings, f, ensure_ascii=False, indent=2)
        print(f"Feature mappings saved to {mappings_path}")

        print("\n" + "=" * 50)
        print("All models trained and saved successfully!")
        print("=" * 50)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
