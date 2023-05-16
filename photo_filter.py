import io
import logging
import asyncio

from PIL import Image
from ultralytics import YOLO

logging.basicConfig(format='%(levelname)s | %(message)s', level='INFO')


class PhotoFilter(object):

    def __init__(self, model, photo_threshold, detect_classes):
        self.model = YOLO(model)
        self.photo_threshold = photo_threshold
        self.detect_classes = detect_classes
        self.logger = logging.getLogger()

    def is_photo_valid(self, img_raw):
        is_valid = False
        img = Image.open(io.BytesIO(img_raw))
        results = self.model.predict(source=img,
                                     classes=self.detect_classes,
                                     conf=self.photo_threshold)
        if len(results[0]) > 0:
            self.logger.info('Found needed objects!')
            is_valid = True
        return is_valid

    async def is_photo_valid_async(self, img_raw):
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None, self.is_photo_valid, img_raw)
        return res
