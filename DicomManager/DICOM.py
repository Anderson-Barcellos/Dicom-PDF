import pydicom
from PIL import Image, ImageEnhance
import os
from pathlib import Path
import traceback


class DICOM2JPEG:
    @classmethod
    def is_video_dicom(cls, path):
        ds = pydicom.dcmread(path)
        if "ImageType" in ds and "MOTION" in ds.ImageType:
            return True
        if "NumberOfFrames" in ds and int(ds.NumberOfFrames) > 1 or None:

            return True
        if "ConversionType" in ds and ds.ConversionType == "DV":
            return True
        return False

    def __init__(self, dcm_path, jpeg_path) -> None:
        self.dcm_path = Path(dcm_path)
        self.jpeg_path = Path(jpeg_path)

    def converter(self) -> None:
        ds = None
        image = None
        try:
            for file in os.listdir(self.dcm_path):
                if file.endswith(".dcm"):
                    file_path = os.path.join(str(self.dcm_path), file)
                    if not DICOM2JPEG.is_video_dicom(file_path):
                        ds = pydicom.dcmread(file_path)
                        if ds[(0x0028, 0x0004)].value == "YBR_FULL_422":
                            image = Image.fromarray(ds.pixel_array, mode="YCbCr")
                        elif ds[(0x0028, 0x0004)].value == "RGB":
                            image = Image.fromarray(ds.pixel_array, mode="RGB")
                        else:
                            image = Image.fromarray(ds.pixel_array, mode="L")
                        # Normalização da imagem
                        image = image.point(lambda x: x * 1)

                        # Aumento do contraste
                        enhancer = ImageEnhance.Contrast(image)
                        image = enhancer.enhance(1)
                        # Aumento do brilho
                        enhancer = ImageEnhance.Brightness(image)
                        image = enhancer.enhance(1)
                        # Aumento da nitidez
                        enhancer = ImageEnhance.Sharpness(image)
                        image = enhancer.enhance(5)

                        # Aumento do contraste
                        nfile = file.replace(".dcm", ".jpeg")
                        image.save(os.path.join(str(self.jpeg_path), nfile))

        except Exception as e:
            print(e)

    def eliminate_dcm(self):
        try:
            for file in os.listdir(self.dcm_path):
                if file.endswith(".dcm"):
                    os.remove(os.path.join(str(self.dcm_path), file))
        except Exception as e:
            print(e)

    def eliminate_jpeg(self):
        try:
            for file in os.listdir(self.jpeg_path):
                if file.endswith(".jpeg") or file.endswith(".jpg"):
                    os.remove(os.path.join(str(self.jpeg_path), file))
        except Exception as e:
            print(e)

    def eliminate_folders(self):
        try:
            self.eliminate_dcm()
            self.eliminate_jpeg()

        except Exception as e:
            print(e)
    
    def eliminate_zips(self):
        try:
            for file in os.listdir("ZIPS"):
                if file.endswith(".zip"):
                    os.remove(os.path.join("ZIPS", file))
        except Exception as e:
            print(e)


