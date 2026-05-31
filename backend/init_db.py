# -*- coding: utf-8 -*-
import os
import csv
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal, Base
from backend.models import Attraction

CSV_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "china-city-attraction-details",
    "citydata",
)


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


def parse_rating(value):
    if not value or value == "" or value == "nan":
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def clean_text(value):
    if not value or str(value).strip() == "" or str(value).strip().lower() == "nan":
        return None
    return str(value).strip()


def load_csv_files():
    if not os.path.isdir(CSV_DIR):
        print(f"CSV directory not found: {CSV_DIR}")
        return

    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    print(f"Found {len(csv_files)} CSV files.")

    all_attractions = []
    seen_keys = set()

    for idx, filename in enumerate(csv_files, 1):
        city_name = os.path.splitext(filename)[0]
        filepath = os.path.join(CSV_DIR, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    name = clean_text(row.get("名字", ""))
                    if not name:
                        continue
                    key = (name, city_name)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    attraction = Attraction(
                        name=name,
                        city=city_name,
                        address=clean_text(row.get("地址", "")),
                        description=clean_text(row.get("介绍", "")),
                        open_time=clean_text(row.get("开放时间", "")),
                        image_url=clean_text(row.get("图片链接", "")),
                        rating=parse_rating(row.get("评分", "")),
                        play_time=clean_text(row.get("建议游玩时间", "")),
                        season=clean_text(row.get("建议季节", "")),
                        ticket=clean_text(row.get("门票", "")),
                        tips=clean_text(row.get("小贴士", "")),
                        source_url=clean_text(row.get("链接", "")),
                    )
                    all_attractions.append(attraction)
                    count += 1

                if idx % 50 == 0 or idx == len(csv_files):
                    print(f"[{idx}/{len(csv_files)}] Parsed {len(all_attractions)} attractions so far...")

        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print(f"\nTotal parsed: {len(all_attractions)} attractions from {len(csv_files)} cities")

    db = SessionLocal()
    try:
        print("Inserting into database (this may take a moment)...")
        batch_size = 500
        for i in range(0, len(all_attractions), batch_size):
            batch = all_attractions[i:i + batch_size]
            db.add_all(batch)
            db.commit()
            print(f"  Inserted batch {i // batch_size + 1}: {len(batch)} records")
        print(f"\nDone! Total inserted: {len(all_attractions)}")
    except Exception as e:
        db.rollback()
        print(f"Error inserting: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    load_csv_files()
