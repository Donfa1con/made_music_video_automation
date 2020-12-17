import collections
import heapq

import numpy as np

from common.openvino import OpenVinoModelWrapper
from common.utils import resize_image_with_ratio


class Video2GifModel:
    def __init__(self, path_to_openvino_model, path_to_snipplet):
        self.video2gif = OpenVinoModelWrapper(path_to_openvino_model)
        self.snipplet_mean = np.load(path_to_snipplet)
        self._reset_state()
        self.deep = 16

    def _reset_state(self):
        self.video_scores = collections.defaultdict(list)
        self.image_scores = {}

    def preprocess(self, image):  # bgr image
        image = resize_image_with_ratio(image[..., ::-1], 171, 128)
        return image

    def predict_image(self, image, image_name):
        clip = []
        for _ in range(self.deep):
            clip.append(image)
        self.image_scores[image_name] = np.mean(self.predict_clip(clip))
        return self.image_scores[image_name]

    def predict_clip(self, clips, video_name=None):
        batch = np.array(clips).transpose((3, 0, 1, 2)).astype(np.float64)
        batch -= self.snipplet_mean
        batch = batch[:, :, 8:120, 29:141]
        batch = np.stack((batch, batch[..., ::-1]), axis=0)
        score = np.mean(self.video2gif.predict(batch.transpose((0, 2, 3, 4, 1))))
        if video_name:
            self.video_scores[video_name].append(score)
        return score

    def _eval_scores(self):
        for key, scores in self.video_scores.items():
            new_scores = []
            for i in range(len(scores)):
                if i == 0 or i == len(scores) - 1:
                    for _ in range(self.deep // 2):
                        new_scores.append(scores[i])
                else:
                    for _ in range(self.deep // 2):
                        new_scores.append(np.mean(scores[i:i + 2]))
            self.video_scores[key] = np.array(new_scores)

    def get_best_scores(self, length=30 * 30, image_time=30):  # sec * fps, fps
        self._eval_scores()
        all_scores = []
        for key, scores in self.video_scores.items():
            for idx, score in enumerate(scores):
                heapq.heappush(all_scores, (-score, idx, key))
        for key, score in self.image_scores.items():
            heapq.heappush(all_scores, (-score, -1, key))
        total_time = 0
        total_video_params = collections.defaultdict(list)
        while all_scores and total_time < length:
            score = heapq.heappop(all_scores)
            total_video_params[score[2]].append(score[1])
            if score[1] == -1:
                total_time += image_time
            else:
                total_time += 1
        for key, val in total_video_params.items():
            total_video_params[key] = val
        self._reset_state()
        return total_video_params
