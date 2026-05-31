class HybridRecommender:

    def __init__(self, item_cf, deepfm, item_cf_weight=0.4, deepfm_weight=0.6):
        self.item_cf = item_cf
        self.deepfm = deepfm
        self.item_cf_weight = item_cf_weight
        self.deepfm_weight = deepfm_weight

    def recommend(self, user_id, behaviors, user_features, candidate_items, top_n=10):
        cf_results = self.item_cf.recommend(user_id, behaviors, top_n=top_n * 3)
        cf_scores = {item_id: score for item_id, score in cf_results}

        deepfm_results = self.deepfm.recommend(user_features, candidate_items, top_n=top_n * 3)
        deepfm_scores = {item_id: score for item_id, score in deepfm_results}

        all_items = set(cf_scores.keys()) | set(deepfm_scores.keys())

        combined = {}
        for item_id in all_items:
            cf_score = cf_scores.get(item_id, 0.0)
            deepfm_score = deepfm_scores.get(item_id, 0.0)
            combined[item_id] = self.item_cf_weight * cf_score + self.deepfm_weight * deepfm_score

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return ranked
