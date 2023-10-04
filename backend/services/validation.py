import os
from fastapi import UploadFile
import tensorflow as tf
from keras import layers
from keras.applications import MobileNetV2

IMG_SHAPE = (256, 256, 3)


class RevisitResNet50Inference(tf.keras.Model):
    def __init__(self, name="revisit_resnet50", **kwargs):
        super(RevisitResNet50Inference, self).__init__()
        self.backbone = MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
        self.b2 = layers.Conv2D(1280, 2, strides=(1, 1), padding="same", activation='relu', input_shape=IMG_SHAPE[1:])
        self.avgpool_8 = layers.AveragePooling2D(pool_size=(1, 1), strides=1, padding='valid', data_format=None)
        self.theta_8 = layers.Conv2D(1, (1, 1), activation='sigmoid')
        self.avgpool_4 = layers.AveragePooling2D(pool_size=(2, 2), strides=2, padding='valid', data_format=None)
        self.theta_4 = layers.Conv2D(1, (1, 1), activation='sigmoid')
        self.avgpool_2 = layers.AveragePooling2D(pool_size=(4, 4), strides=4, padding='valid', data_format=None)
        self.theta_2 = layers.Conv2D(1, (1, 1), activation='sigmoid')
        self.avgpool_1 = layers.AveragePooling2D(pool_size=(8, 8), strides=8, padding='valid', data_format=None)
        self.theta_1 = layers.Conv2D(1, (1, 1), activation='sigmoid')
        self.fc = layers.Dense(1, activation='sigmoid')

    def call(self, input_img):
        F = self.backbone(input_img)
        F = self.b2(F)

        x = self.avgpool_8(F)
        M8 = self.theta_8(x)

        x = self.avgpool_4(F)
        M4 = self.theta_4(x)

        x = self.avgpool_2(F)
        M2 = self.theta_2(x)

        x = self.avgpool_1(F)
        M1 = self.theta_1(x)

        x = layers.Concatenate(axis=1)(
            [layers.Flatten()(M8), layers.Flatten()(M4), layers.Flatten()(M2), layers.Flatten()(M1)])
        y_pred = self.fc(x)

        return y_pred


# Создаём экземпляр модели RevisitResNet50
inference_model = RevisitResNet50Inference()

# Загружаем веса из файлов cp.ckpt.index и cp.ckpt.data-00000-of-00001
checkpoint_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'mobilenetv2/cp.ckpt.index'
)
ckpt = tf.train.Checkpoint(model=inference_model)
ckpt.restore(checkpoint_path).expect_partial()


# Функция для инференса на бинарных данных изображения
def infer_image(image):
    image = tf.image.decode_image(image)
    image = tf.image.resize(image, IMG_SHAPE[:2])
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = tf.expand_dims(image, axis=0)

    predictions = inference_model.call(image)

    return predictions.numpy()[0][0]


async def validate_photo(image: bytes) -> bool:
    predictions = infer_image(image)
    if predictions > 0.5:
        return True
    return False
