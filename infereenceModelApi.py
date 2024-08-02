import cv2
import typing
import numpy as np
import os
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer
script_dir = os.path.dirname(__file__)
relative_path = "Models/02_captcha_to_text/202408021931"
absolute_path = os.path.join(script_dir, relative_path)
if not os.path.exists(absolute_path):
    raise FileNotFoundError(f"Model path '{absolute_path}' does not exist")
class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        image = cv2.resize(image, self.input_shapes[0][1:3][::-1])

        image_pred = np.expand_dims(image, axis=0).astype(np.float32)

        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text


async def predict(image):
    print('i am called')
    import pandas as pd
    from tqdm import tqdm
    from mltu.configs import BaseModelConfigs
    current_dir = os.getcwd()
    configPath =  f"{absolute_path}/configs.yaml"
    valpath = f"{absolute_path}/val.csv"
    print(configPath)
    configs = BaseModelConfigs.load(configPath)
    modelPath = f'{absolute_path}'
    model = ImageToWordModel(model_path=modelPath, char_list=configs.vocab)
    print("I am here too")
    df = pd.read_csv(valpath).values.tolist()

    accum_cer = []

    
    # Load validation data
    df = pd.read_csv(valpath).values.tolist()

    # Convert image data to OpenCV format
    image_data = image.getvalue()
    nparr = np.frombuffer(image_data, np.uint8)
    image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    print("I am here too")
    prediction_text = model.predict(image_cv2)

    print(f" Prediction: {prediction_text}")




    return prediction_text

