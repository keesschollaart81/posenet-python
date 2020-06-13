from posenet.base_model import BaseModel
import numpy as np
import cv2


class ResNet(BaseModel):

    def __init__(self, model_function, output_tensor_names, output_stride):
        super().__init__(model_function, output_tensor_names, output_stride)
        self.image_net_mean = [-123.15, -115.90, -103.06]

    def preprocess_input(self, image):
        target_width, target_height = self.valid_resolution(image.shape[1], image.shape[0])
        # the padding to keep the aspect ratio:
        target_aspect = target_width / target_height
        aspect = image.shape[1] / image.shape[0]
        if aspect < target_aspect:
            padding = np.array([0, round(0.5 * (target_aspect * image.shape[0] - image.shape[1]))])
        else:
            padding = np.array([round(0.5 * ((1.0 / target_aspect) * image.shape[1] - image.shape[0])), 0])
        image = cv2.copyMakeBorder(image, padding[0], padding[0], padding[1], padding[1],
             cv2.BORDER_CONSTANT, value=[0,0,0])
             
        # the scale that can get us back to the original width and height:
        scale = np.array([image.shape[0] / target_height, image.shape[1] / target_width])
        input_img = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB).astype(np.float32)  # to RGB colors
        # todo: test a variant that adds black bars to the image to match it to a valid resolution

        # See: https://github.com/tensorflow/tfjs-models/blob/master/body-pix/src/resnet.ts
        input_img = input_img + self.image_net_mean
        input_img = input_img.reshape(1, target_height, target_width, 3)  # HWC to NHWC
        return input_img, scale, padding
