import albumentations as A
import cv2
import torch
import torch.nn as nn
from torch.nn import functional as F

from common.openvino import OpenVinoModelWrapper


class TargetNet(nn.Module):
    """
    Target network for quality prediction.
    """

    def __init__(self, paras):
        super(TargetNet, self).__init__()
        paras = dict(zip(['target_in_vec', 'target_fc1w', 'target_fc1b', 'target_fc2w', 'target_fc2b', 'target_fc3w',
                          'target_fc3b', 'target_fc4w', 'target_fc4b', 'target_fc5w', 'target_fc5b'], paras))
        self.l1 = nn.Sequential(
            TargetFC(paras['target_fc1w'], paras['target_fc1b']),
            nn.Sigmoid(),
        )
        self.l2 = nn.Sequential(
            TargetFC(paras['target_fc2w'], paras['target_fc2b']),
            nn.Sigmoid(),
        )

        self.l3 = nn.Sequential(
            TargetFC(paras['target_fc3w'], paras['target_fc3b']),
            nn.Sigmoid(),
        )

        self.l4 = nn.Sequential(
            TargetFC(paras['target_fc4w'], paras['target_fc4b']),
            nn.Sigmoid(),
            TargetFC(paras['target_fc5w'], paras['target_fc5b']),
        )

    def forward(self, x):
        q = self.l1(x)
        q = self.l2(q)
        q = self.l3(q)
        q = self.l4(q).squeeze()
        return q


class TargetFC(nn.Module):
    """
    Fully connection operations for target net

    Note:
        Weights & biases are different for different images in a batch,
        thus here we use group convolution for calculating images in a batch with individual weights & biases.
    """

    def __init__(self, weight, bias):
        super(TargetFC, self).__init__()
        self.weight_shape_0 = weight.shape[0]
        self.weight_shape_1 = weight.shape[1]
        self.weight = weight.view(weight.shape[0] * weight.shape[1],
                                  weight.shape[2], weight.shape[3], weight.shape[4])
        self.bias = bias.view(bias.shape[0] * bias.shape[1])

    def forward(self, input_):
        input_re = input_.view(-1, input_.shape[0] * input_.shape[1], input_.shape[2], input_.shape[3])
        out = F.conv2d(input=input_re, weight=self.weight, bias=self.bias, groups=self.weight_shape_0)
        return out.view(input_.shape[0], self.weight_shape_1, input_.shape[2], input_.shape[3])


class QualityModel:
    def __init__(self, path_to_openvino_model):
        self.hyper_net = OpenVinoModelWrapper(path_to_openvino_model)
        self.transforms = A.Compose([
            A.CenterCrop(224, 224),
            A.Normalize()
        ])

    def predict(self, image):  # bgr image
        image = image[..., ::-1]
        scale = max(300 / image.shape[1], 300 / image.shape[0])
        resized = cv2.resize(image, None, fx=scale, fy=scale)
        resized = self.transforms(image=resized)['image'].transpose(2, 0, 1)
        params = self.hyper_net.predict(resized[None])
        params = [torch.tensor(x) for x in params]
        target_net = TargetNet(params)
        with torch.no_grad():
            score = float(target_net(params[0]).item())
        return score
