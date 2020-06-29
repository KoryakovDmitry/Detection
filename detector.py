import torch
import cv2

from torchvision.models.detection.faster_rcnn import fasterrcnn_resnet50_fpn
from torchvision.transforms import ToTensor

CATEGORY_MAP = {
    1: 'person',
    2: 'bicycle',
    3: 'car',
    4: 'motorcycle',
    5: 'airplane',
    6: 'bus',
    7: 'train',
    8: 'truck',
    9: 'boat',
    10: 'traffic light',
    11: 'fire hydrant',
    13: 'stop sign',
    14: 'parking meter',
    15: 'bench',
    16: 'bird',
    17: 'cat',
    18: 'dog',
    19: 'horse',
    20: 'sheep',
    21: 'cow',
    22: 'elephant',
    23: 'bear',
    24: 'zebra',
    25: 'giraffe',
    27: 'backpack',
    28: 'umbrella',
    31: 'handbag',
    32: 'tie',
    33: 'suitcase',
    34: 'frisbee',
    35: 'skis',
    36: 'snowboard',
    37: 'sports ball',
    38: 'kite',
    39: 'baseball bat',
    40: 'baseball glove',
    41: 'skateboard',
    42: 'surfboard',
    43: 'tennis racket',
    44: 'bottle',
    46: 'wine glass',
    47: 'cup',
    48: 'fork',
    49: 'knife',
    50: 'spoon',
    51: 'bowl',
    52: 'banana',
    53: 'apple',
    54: 'sandwich',
    55: 'orange',
    56: 'broccoli',
    57: 'carrot',
    58: 'hot dog',
    59: 'pizza',
    60: 'donut',
    61: 'cake',
    62: 'chair',
    63: 'couch',
    64: 'potted plant',
    65: 'bed',
    67: 'dining table',
    70: 'toilet',
    72: 'tv',
    73: 'laptop',
    74: 'mouse',
    75: 'remote',
    76: 'keyboard',
    77: 'cell phone',
    78: 'microwave',
    79: 'oven',
    80: 'toaster',
    81: 'sink',
    82: 'refrigerator',
    84: 'book',
    85: 'clock',
    86: 'vase',
    87: 'scissors',
    88: 'teddy bear',
    89: 'hair drier',
    90: 'toothbrush'
}
# WEIGHTS = "./weights/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth"


class Detector(object):
    def __init__(self, threshold=0.7, category_map=None, weights=None):
        if weights is None:
            self.pytorch_model = fasterrcnn_resnet50_fpn(pretrained=True, pretrained_backbone=True)
        else:
            self.pytorch_model = fasterrcnn_resnet50_fpn(pretrained=False, pretrained_backbone=False)
            self.pytorch_model.load_state_dict(torch.load(weights))            
        if category_map is None:
            category_map = CATEGORY_MAP
        self.category_map = category_map
        self.threshold = threshold
        self.img_numpy = None
        self.img_tensor = None
        self.img_out = None
        self.filter_objs = dict()

    def run(self, path_in, path_out):
        self.pytorch_model.eval()
        self.img_numpy = cv2.imread(path_in)[:, :, ::-1]
        self.img_tensor = ToTensor()(self.img_numpy.copy())[None, :, :, :]
        predictions = self.pytorch_model(self.img_tensor)

        self.filter_objs['boxes'] = predictions[0]['boxes'][predictions[0]['scores'] > self.threshold].detach().numpy()
        self.filter_objs['labels'] = list(map(int, predictions[0]['labels'][predictions[0]['scores'] > self.threshold]))
        self.filter_objs['probability'] = [int(score.item() * 100) for score in
                                           predictions[0]['scores'][predictions[0]['scores'] > self.threshold]]

        self.img_out = self._create_out_img()
        cv2.imwrite(path_out, img=self.img_out[:, :, ::-1])

    def _create_out_img(self):
        img_out = self.img_numpy
        flag = False
        for box, lbl, prob in zip(*self.filter_objs.values()):
            img_out = cv2.rectangle(
                img=img_out,
                pt1=(box[0], box[1]),
                pt2=(box[2], box[3]),
                color=225,
                thickness=1,
            )
            img_out = cv2.rectangle(img_out, (int(box[2]), int(box[1] - 10)), (int(box[2] + 80), int(box[1] + 10)),
                                    (0, 0, 0), -1)
            img_out = cv2.rectangle(img_out, (int(box[2]), int(box[3] - 10)), (int(box[2] + 40), int(box[3] + 10)),
                                    (0, 0, 0), -1)
            img_out = cv2.putText(img_out, self.category_map[lbl], (box[2], box[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                  (225, 225, 255))
            img_out = cv2.putText(img_out, str(prob) + ' %', (box[2], box[3]), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                  (0, 255, 255))
            flag = True
        return img_out.get() if flag else img_out
