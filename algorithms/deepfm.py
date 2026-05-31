import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


class DeepFMModel(nn.Module):

    def __init__(self, feature_sizes, embedding_dim=16, hidden_dims=None):
        super(DeepFMModel, self).__init__()
        if hidden_dims is None:
            hidden_dims = [64, 32]

        self.feature_names = list(feature_sizes.keys())
        self.embedding_dim = embedding_dim

        self.embeddings = nn.ModuleDict()
        self.first_order_linear = nn.ModuleDict()
        for name, size in feature_sizes.items():
            self.embeddings[name] = nn.Embedding(num_embeddings=size, embedding_dim=embedding_dim)
            self.first_order_linear[name] = nn.Embedding(num_embeddings=size, embedding_dim=1)

        fm_second_order_input_dim = len(feature_sizes) * embedding_dim

        deep_input_dim = len(feature_names) * embedding_dim
        deep_layers = []
        prev_dim = deep_input_dim
        for h_dim in hidden_dims:
            deep_layers.append(nn.Linear(prev_dim, h_dim))
            deep_layers.append(nn.BatchNorm1d(h_dim))
            deep_layers.append(nn.ReLU())
            deep_layers.append(nn.Dropout(0.3))
            prev_dim = h_dim
        self.deep_mlp = nn.Sequential(*deep_layers)
        self.deep_output = nn.Linear(prev_dim, 1)

        self.fm_first_order_output = nn.Linear(len(feature_names), 1)

    def forward(self, sparse_inputs):
        first_order_values = []
        embedding_values = []

        for name in self.feature_names:
            x = sparse_inputs[name]
            emb = self.embeddings[name](x)
            first_order = self.first_order_linear[name](x)
            first_order_values.append(first_order.squeeze(-1))
            embedding_values.append(emb)

        first_order_concat = torch.stack(first_order_values, dim=1)
        fm_first_order = self.fm_first_order_output(first_order_concat)

        emb_concat = torch.stack(embedding_values, dim=1)
        sum_sq = torch.sum(emb_concat, dim=1) ** 2
        sq_sum = torch.sum(emb_concat ** 2, dim=1)
        fm_second_order = 0.5 * torch.sum(sum_sq - sq_sum, dim=1, keepdim=True)

        fm_part = fm_first_order + fm_second_order

        deep_input = torch.cat(embedding_values, dim=1)
        deep_out = self.deep_mlp(deep_input)
        deep_out = self.deep_output(deep_out)

        output = torch.sigmoid(fm_part + deep_out)
        return output.squeeze(-1)


class DeepFMRecommender:

    def __init__(self, feature_sizes, embedding_dim=16):
        self.feature_sizes = feature_sizes
        self.embedding_dim = embedding_dim
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DeepFMModel(feature_sizes, embedding_dim).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.loss_fn = nn.BCELoss()

    def train_model(self, train_data, epochs=20, batch_size=256):
        self.model.train()

        feature_tensors = {}
        labels = []
        for sample in train_data:
            for name in self.feature_sizes.keys():
                if name not in feature_tensors:
                    feature_tensors[name] = []
                feature_tensors[name].append(sample[name])
            labels.append(sample["label"])

        for name in feature_tensors:
            feature_tensors[name] = torch.tensor(feature_tensors[name], dtype=torch.long).to(self.device)
        labels_tensor = torch.tensor(labels, dtype=torch.float32).to(self.device)

        dataset_size = len(labels)
        num_batches = (dataset_size + batch_size - 1) // batch_size

        for epoch in range(epochs):
            total_loss = 0.0
            indices = torch.randperm(dataset_size)

            for batch_idx in range(num_batches):
                start = batch_idx * batch_size
                end = min(start + batch_size, dataset_size)
                batch_indices = indices[start:end]

                batch_inputs = {}
                for name in self.feature_tensors_names():
                    batch_inputs[name] = feature_tensors[name][batch_indices]
                batch_labels = labels_tensor[batch_indices]

                self.optimizer.zero_grad()
                predictions = self.model(batch_inputs)
                loss = self.loss_fn(predictions, batch_labels)
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item() * (end - start)

            avg_loss = total_loss / dataset_size
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

    def feature_tensors_names(self):
        return list(self.feature_sizes.keys())

    def recommend(self, user_features, candidate_items, top_n=10):
        self.model.eval()

        all_scores = []
        with torch.no_grad():
            for item in candidate_items:
                sample = {}
                for name in self.feature_sizes.keys():
                    if name in user_features:
                        sample[name] = user_features[name]
                    elif name in item:
                        sample[name] = item[name]
                    else:
                        sample[name] = 0

                sparse_inputs = {}
                for name in self.feature_sizes.keys():
                    sparse_inputs[name] = torch.tensor([sample[name]], dtype=torch.long).to(self.device)

                score = self.model(sparse_inputs).item()
                all_scores.append((item["attraction_id"], score))

        all_scores.sort(key=lambda x: x[1], reverse=True)
        return all_scores[:top_n]

    def save(self, path):
        torch.save(self.model.state_dict(), path)

    def load(self, path):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()
        return self
