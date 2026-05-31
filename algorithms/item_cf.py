import math
import pickle
from collections import defaultdict


class ItemCF:

    def __init__(self):
        self.item_similarity = {}
        self.train_data = None

    def train(self, behaviors, top_k=50):
        user_items = defaultdict(dict)
        for user_id, attraction_id, behavior_type in behaviors:
            weight = {"view": 1.0, "collect": 2.0, "rate": 3.0}.get(behavior_type, 1.0)
            user_items[user_id][attraction_id] = user_items[user_id].get(attraction_id, 0) + weight

        self.train_data = user_items

        item_users = defaultdict(dict)
        for user_id, items in user_items.items():
            for item_id, score in items.items():
                item_users[item_id][user_id] = score

        item_norms = {}
        for item_id, users in item_users.items():
            norm = math.sqrt(sum(v * v for v in users.values()))
            item_norms[item_id] = norm

        sim_matrix = defaultdict(dict)
        all_items = list(item_users.keys())
        for i in range(len(all_items)):
            for j in range(i + 1, len(all_items)):
                item_i = all_items[i]
                item_j = all_items[j]
                users_i = item_users[item_i]
                users_j = item_users[item_j]
                common_users = set(users_i.keys()) & set(users_j.keys())
                if not common_users:
                    continue
                dot = sum(users_i[u] * users_j[u] for u in common_users)
                denom = item_norms[item_i] * item_norms[item_j]
                if denom == 0:
                    continue
                sim = dot / denom
                if sim > 0:
                    sim_matrix[item_i][item_j] = sim
                    sim_matrix[item_j][item_i] = sim

        self.item_similarity = {}
        for item_id, neighbors in sim_matrix.items():
            sorted_neighbors = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:top_k]
            self.item_similarity[item_id] = dict(sorted_neighbors)

        return self

    def recommend(self, user_id, behaviors, top_n=10):
        user_items = set()
        user_item_scores = {}
        for uid, aid, btype in behaviors:
            if uid == user_id:
                user_items.add(aid)
                weight = {"view": 1.0, "collect": 2.0, "rate": 3.0}.get(btype, 1.0)
                user_item_scores[aid] = user_item_scores.get(aid, 0) + weight

        if not user_items:
            return []

        scores = defaultdict(float)
        for item_id, user_score in user_item_scores.items():
            if item_id not in self.item_similarity:
                continue
            for sim_item, sim_score in self.item_similarity[item_id].items():
                if sim_item in user_items:
                    continue
                scores[sim_item] += user_score * sim_score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return ranked

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.item_similarity, f)

    def load(self, path):
        with open(path, "rb") as f:
            self.item_similarity = pickle.load(f)
        return self
