from __future__ import annotations

import os
from pathlib import Path
from typing import Union

import numpy as np
import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
from PIL import Image, ImageEnhance


class DICOM2JPEG:
    """
    Converte todos os arquivos DICOM (*.dcm) de uma pasta para JPEG,
    mantendo resolução original e ajustando o nível de preto para não ficar muito intenso.

    Parâmetros
    ----------
    dcm_path     : str | Path
        Pasta de entrada com os arquivos DICOM.
    jpeg_path    : str | Path
        Pasta de saída para os arquivos JPEG.
    black_gamma  : float
        Fator de correção de gamma (< 1 clareia tons escuros; > 1 escurece).
        Ajusta o nível de preto para ficar menos intenso.
    enhancements : dict
        Fatores para realces opcionais: brilho, cor, contraste e nitidez.
        Exemplo: {'brightness': 1.2, 'color': 1.0, 'contrast': 1.8, 'sharpness': 1.5}
    jpeg_quality : int
        Qualidade do JPEG (0-100).
    """

    def __init__(
        self,
        dcm_path: Union[str, Path],
        jpeg_path: Union[str, Path],
        black_gamma: float = 0.8,
        enhancements: dict | None = None,
        jpeg_quality: int = 99,
    ):
        self.dcm_path = Path(dcm_path)
        self.jpeg_path = Path(jpeg_path)
        self.black_gamma = black_gamma
        self.enhancements = enhancements or {
            'brightness': 1.2,
            'color': 1.0,
            'contrast': 1.8,
            'sharpness': 1.5,
        }
        self.jpeg_quality = jpeg_quality

        # Garante que a pasta de saída exista
        self.jpeg_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_video_dicom(path: Union[str, Path]) -> bool:
        """Detecta DICOM de vídeo/multiframe e pula a conversão."""
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        if 'ImageType' in ds and 'MOTION' in ds.ImageType:
            return True
        if 'NumberOfFrames' in ds and int(ds.NumberOfFrames) > 1:
            return True
        if ds.get('ConversionType', '') == 'DV':
            return True
        return False

    @staticmethod
    def gamma_correction(img: Image.Image, gamma: float) -> Image.Image:
        """
        Aplica correção de gamma usando look-up table.
        gamma < 1 clareia tons escuros; gamma > 1 escurece.
        """
        inv = 1.0 / gamma if gamma != 0 else 1.0
        lut = [round((i / 255) ** inv * 255) for i in range(256)]
        if img.mode in ('RGB', 'YCbCr'):
            lut *= len(img.getbands())
        return img.point(lut)

    def converter(self) -> None:
        """Percorre a pasta DICOM e converte cada arquivo para JPEG mantendo resolução."""
        for file in os.listdir(self.dcm_path):
            if not file.lower().endswith('.dcm'):
                continue
            if file.startswith('SR'):
                continue

            path = self.dcm_path / file
            if self.is_video_dicom(path):
                continue

            try:
                ds = pydicom.dcmread(path)
                img = self._dicom_to_pil(ds)

                # Realces opcionais
                img = ImageEnhance.Brightness(img).enhance(
                    self.enhancements['brightness'])
                img = ImageEnhance.Color(img).enhance(
                    self.enhancements['color'])
                img = ImageEnhance.Contrast(img).enhance(
                    self.enhancements['contrast'])
                img = ImageEnhance.Sharpness(img).enhance(
                    self.enhancements['sharpness'])

                # Correção de gamma para nivel de preto mais claro
                img = self.gamma_correction(img, self.black_gamma)

                output = file.replace('.dcm', '.jpeg')
                img.save(self.jpeg_path / output, 'JPEG',
                         quality=self.jpeg_quality)

            except Exception as e:
                print(f'[ERRO] {file}: {e}')

    def eliminate_dcm(self) -> None:
        """Apaga todos os .dcm da pasta de entrada."""
        for f in self.dcm_path.glob('*.dcm'):
            try:
                f.unlink()
            except Exception as e:
                print(f'[ERRO] deletando {f}: {e}')

    def eliminate_jpeg(self) -> None:
        """Apaga todos os .jpeg/.jpg da pasta de saída."""
        for ext in ('*.jpeg', '*.jpg'):
            for f in self.jpeg_path.glob(ext):
                try:
                    f.unlink()
                except Exception as e:
                    print(f'[ERRO] deletando {f}: {e}')

    def eliminate_all(self) -> None:
        """Apaga DICOMs e JPEGs nas pastas configuradas."""
        self.eliminate_dcm()
        self.eliminate_jpeg()

    @staticmethod
    def _dicom_to_pil(ds: pydicom.Dataset) -> Image.Image:
        """
        Converte Dataset DICOM em PIL.Image RGB de 8 bits, sem alterar resolução.
        """
        photo = ds.get('PhotometricInterpretation', '').upper()

        # Imagens coloridas
        if photo in ('RGB',):
            return Image.fromarray(ds.pixel_array, mode='RGB')
        if photo in ('YBR_FULL_422', 'YBR_FULL'):
            return Image.fromarray(ds.pixel_array, mode='YCbCr').convert('RGB')

        # Monocromáticas
        arr = apply_modality_lut(ds.pixel_array, ds)
        arr = apply_voi_lut(arr, ds)
        if photo == 'MONOCHROME1':
            arr = np.max(arr) - arr
        arr = arr.astype(np.float32)
        arr -= arr.min()
        if arr.max() > 0:
            arr /= arr.max()
        arr = (arr * 255).astype(np.uint8)
        return Image.fromarray(arr, mode='L').convert('RGB')
