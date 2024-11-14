import pydicom
from PIL import Image, ImageEnhance
import os
from pathlib import Path


class DICOM2JPEG:
    """ Classe para converter arquivos DICOM em JPEG.
        ### Parâmetros:

        - dcm_path: str
            Caminho para a pasta contendo os arquivos DICOM.
        - jpeg_path: str
            Caminho para a pasta onde os arquivos JPEG serão salvos.




    """
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
        """ Método para converter arquivos DICOM em JPEG."""
        ds = None
        image = None
        try:
            files = os.listdir(self.dcm_path)
            for file in files:
                if len(files) >=4 or len(files)<=2:
                        
                    if file.endswith(".dcm"):
                        file_path = os.path.join(str(self.dcm_path), file)
                        if not DICOM2JPEG.is_video_dicom(file_path):
                            ds = pydicom.dcmread(file_path)
                            if ds[(0x0028, 0x0004)].value == "YBR_FULL_422":
                                image = Image.fromarray(ds.pixel_array, mode="YCbCr").convert("RGB")
                               
                            else:
                                image = Image.fromarray(ds.pixel_array, mode="RGB").convert("RGB")
                            # Normalização da imagem
                            image = image.point(lambda x: x * 2)

                            # Aumento do contraste
                            enhancer = ImageEnhance.Contrast(image)
                            image = enhancer.enhance(1)
                            # Aumento do brilho
                            enhancer = ImageEnhance.Brightness(image)
                            image = enhancer.enhance(2)
                            # Aumento da nitidez
                            enhancer = ImageEnhance.Sharpness(image)
                            image = enhancer.enhance(1.7)

                            # Aumento do contraste
                            nfile = file.replace(".dcm", ".jpeg")
                            image.save(os.path.join(str(self.jpeg_path), nfile))
     
		    

        except Exception as e:
            print(e)

    def eliminate_dcm(self) -> None:
        """ Método para eliminar pasta DICOM."""
        try:
            for file in os.listdir(self.dcm_path):
                if file.endswith(".dcm"):
                    os.remove(os.path.join(str(self.dcm_path), file))
        except Exception as e:
            print(e)

    def eliminate_jpeg(self):
        """ Método para eliminar pasta Images."""
        try:
            for file in os.listdir(self.jpeg_path):
                if file.endswith(".jpeg") or file.endswith(".jpg"):
                    os.remove(os.path.join(str(self.jpeg_path), file))
        except Exception as e:
            print(e)

    def eliminate_folders(self):
        """ Método para eliminar pastas DICOM e Images."""
        try:
            self.eliminate_dcm()
            self.eliminate_jpeg()

        except Exception as e:
            print(e)

    def eliminate_zips(self):
        """ Método para eliminar arquivos da pasta ZIPS."""
        try:
            for file in os.listdir("ZIPS"):
                if file.endswith(".zip"):
                    os.remove(os.path.join("ZIPS", file))
        except Exception as e:
            print(e)
