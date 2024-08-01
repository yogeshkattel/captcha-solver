import os
import tensorflow as tf
from keras.models import load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
from mltu.tensorflow.dataProvider import DataProvider
from mltu.tensorflow.losses import CTCloss
from mltu.tensorflow.callbacks import Model2onnx, TrainLogger
from mltu.tensorflow.metrics import CWERMetric
from mltu.preprocessors import ImageReader
from mltu.transformers import ImageResizer, LabelIndexer, LabelPadding
from mltu.augmentors import RandomBrightness, RandomRotate, RandomErodeDilate
from mltu.annotations.images import CVImage
from main.model import train_model
from main.configs import ModelConfigs

# Set up GPU memory growth
try: 
    [tf.config.experimental.set_memory_growth(gpu, True) for gpu in tf.config.experimental.list_physical_devices("GPU")]
except: 
    pass

# Load pre-trained model
pretrained_model = load_model('./Models/02_captcha_to_text/203404030319/model.h5',compile=False)

# Define configs
configs = ModelConfigs()

# Prepare dataset
dataset, vocab, max_len = [], set(), 0
captcha_path = os.path.join("Datasets", "captcha_images_v2")
for file in os.listdir(captcha_path):
    file_path = os.path.join(captcha_path, file)
    label = os.path.splitext(file)[0] 
    dataset.append([file_path, label])
    vocab.update(list(label))
    max_len = max(max_len, len(label))

configs.vocab = "".join(vocab)
configs.max_text_length = max_len
configs.save()

# Create data provider
data_provider = DataProvider(
    dataset=dataset,
    skip_validation=True,
    batch_size=configs.batch_size,
    data_preprocessors=[ImageReader(CVImage)],
    transformers=[
        ImageResizer(configs.width, configs.height),
        LabelIndexer(configs.vocab),
        LabelPadding(max_word_length=configs.max_text_length, padding_value=len(configs.vocab))
        ],
)

# Split dataset
train_data_provider, val_data_provider = data_provider.split(split=0.9)
train_data_provider.augmentors = [RandomBrightness(), RandomRotate(), RandomErodeDilate()]

# Fine-tune the pre-trained model
pretrained_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=configs.learning_rate), 
    loss=CTCloss(), 
    metrics=[CWERMetric(padding_token=len(configs.vocab))],
    run_eagerly=False
)

# Define callbacks
earlystopper = EarlyStopping(monitor="val_CER", patience=50, verbose=1, mode="min")
checkpoint = ModelCheckpoint(f"{configs.model_path}/model.h5", monitor="val_CER", verbose=1, save_best_only=True, mode="min")
trainLogger = TrainLogger(configs.model_path)
tb_callback = TensorBoard(f"{configs.model_path}/logs", update_freq=1)
reduceLROnPlat = ReduceLROnPlateau(monitor="val_CER", factor=0.9, min_delta=1e-10, patience=20, verbose=1, mode="min")
model2onnx = Model2onnx(f"{configs.model_path}/model.h5")

# Fine-tune the model
pretrained_model.fit(
    train_data_provider,
    validation_data=val_data_provider,
    epochs=configs.train_epochs,
    callbacks=[earlystopper, checkpoint, trainLogger, reduceLROnPlat, tb_callback, model2onnx],
    workers=configs.train_workers
)

# Save training and validation datasets as csv files
train_data_provider.to_csv(os.path.join(configs.model_path, "train.csv"))
val_data_provider.to_csv(os.path.join(configs.model_path, "val.csv"))
