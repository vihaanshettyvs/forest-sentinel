import csv
import numpy as np
import librosa
import tensorflow as tf
import tensorflow_hub as hub


class YAMNetClassifier:
    def __init__(self):
        print("Loading YAMNet model. First run downloads it once...")
        self.model = hub.load("https://tfhub.dev/google/yamnet/1")

        class_map_path = self.model.class_map_path().numpy().decode("utf-8")

        with tf.io.gfile.GFile(class_map_path) as file:
            self.labels = [
                row["display_name"]
                for row in csv.DictReader(file)
            ]

    def classify(self, audio_path):
        waveform, _ = librosa.load(
            audio_path,
            sr=16000,
            mono=True
        )

        scores, _, _ = self.model(waveform)
        average_scores = np.mean(scores.numpy(), axis=0)

        top_indexes = average_scores.argsort()[-3:][::-1]

        top_3 = [
            {
                "label": self.labels[index],
                "confidence": round(float(average_scores[index]), 3)
            }
            for index in top_indexes
        ]

        category_scores = {
            "chainsaw": self._best_score(average_scores, ["chainsaw"]),
            "gunshot": self._best_score(average_scores, ["gunshot", "gunfire"]),
            "bird": self._best_score(average_scores, ["bird", "chirp", "tweet"]),
            "vehicle": self._best_score(
                average_scores,
                ["engine", "truck", "vehicle", "car"]
            )
        }

        label = max(category_scores, key=category_scores.get)

        return {
            "label": label,
            "confidence": round(float(category_scores[label]), 3),
            "top_3": top_3
        }

    def _best_score(self, scores, keywords):
        matches = [
            scores[index]
            for index, label in enumerate(self.labels)
            if any(word in label.lower() for word in keywords)
        ]

        return max(matches) if matches else 0