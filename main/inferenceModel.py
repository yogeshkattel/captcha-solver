import cv2
import typing
import numpy as np
from tensorflow.keras.models import load_model

from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer

class ImageToWordModel:
    def __init__(self, model_path: str, char_list: typing.Union[str, list]):
        self.model = load_model(model_path)
        self.char_list = char_list
        self.input_shape = self.model.input_shape[1:3]

    def predict(self, image: np.ndarray):
        image = cv2.resize(image, self.input_shape[::-1])
        image = np.expand_dims(image, axis=0).astype(np.float32)

        preds = self.model.predict(image)
        text = ctc_decoder(preds, self.char_list)[0]

        return text

def predict(image):
    import pandas as pd
    from tqdm import tqdm
    from mltu.configs import BaseModelConfigs

    configs = BaseModelConfigs.load("Models/02_captcha_to_text/202407290357/configs.yaml")

    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    df = pd.read_csv("Models/02_captcha_to_text/202404031719/val.csv").values.tolist()

    accum_cer = []

    image = cv2.imread(image)

    prediction_text = model.predict(image)

    print(f" Prediction: {prediction_text}")




    return prediction_text
