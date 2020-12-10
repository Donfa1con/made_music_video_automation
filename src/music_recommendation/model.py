import albumentations as A
import numpy as np

from common.openvino import OpenVinoModelWrapper
from common.utils import resize_image_with_ratio


class MusicModel:
    def __init__(self, path_to_openvino_model, path_to_labels):
        self.model_3d = OpenVinoModelWrapper(path_to_openvino_model)
        with open(path_to_labels, 'r') as f:
            self.class_names = f.read().split('\n')
        self.transforms = A.Compose([
            A.CenterCrop(112, 112),
            A.Normalize(mean=[0.43216, 0.394666, 0.37645], std=[0.22803, 0.22145, 0.216989])
        ])
        self.logits = []
        self.deep = 16

    def preprocess(self, image):  # bgr image
        image = resize_image_with_ratio(image[..., ::-1], 171, 128)
        image = self.transforms(image=image)['image']
        return image

    def predict(self, clips):
        batch = np.array(clips)[None]
        batch = np.transpose(batch, (0, 4, 1, 2, 3))
        self.logits.append(self.model_3d.predict(batch)[0])
        return self.logits[-1]

    def get_label(self):
        if self.logits:
            label = self.class_names[np.argmax(np.mean(self.logits, axis=0))]
        else:
            label = 'None'
        self.logits = []
        return label
