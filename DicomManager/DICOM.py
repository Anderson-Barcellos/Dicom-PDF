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
        dcm_path: str,
        jpeg_path: str,
        black_gamma: float = 0.75,
        enhancements: dict | None = None,
        jpeg_quality: int = 99,
    ):
        self.dcm_path = dcm_path
        self.jpeg_path = jpeg_path
        self.black_gamma = black_gamma
        self.enhancements = enhancements or {
            'brightness': 1.2,
            'color': 1.0,
            'contrast': 1.5,
            'sharpness': 1.5,
        }
        self.jpeg_quality = jpeg_quality



    @staticmethod
    def is_video_dicom(path: Union[str, Path]) -> bool:
        """
        ### 🎥 Detecta DICOM de vídeo/multiframe

        Verifica se um arquivo DICOM contém dados de vídeo ou múltiplos frames,
        que devem ser pulados na conversão para JPEG estático.

        ### 🖥️ Parameters
        - `path` (`Union[str, Path]`): Caminho para o arquivo DICOM.

        ### 🔄 Returns
        - `bool`: True se for vídeo/multiframe, False caso contrário.

        ### 💡 Example
        >>> is_video = DICOM2JPEG.is_video_dicom("video.dcm")
        >>> print(f"É vídeo: {is_video}")
        """
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)

            # Verificar ImageType para indicação de MOTION
            if hasattr(ds, 'ImageType') and ds.ImageType:
                if isinstance(ds.ImageType, (list, tuple)):
                    if any('MOTION' in str(img_type).upper() for img_type in ds.ImageType):
                        return True
                elif 'MOTION' in str(ds.ImageType).upper():
                    return True

            # Verificar número de frames
            if hasattr(ds, 'NumberOfFrames'):
                try:
                    num_frames = int(ds.NumberOfFrames)
                    if num_frames > 1:
                        return True
                except (ValueError, TypeError):
                    pass

            # Verificar tipo de conversão
            if hasattr(ds, 'ConversionType') and ds.ConversionType == 'DV':
                return True

            # Verificar SOP Class UID para classes de vídeo
            if hasattr(ds, 'SOPClassUID'):
                video_sop_classes = [
                    '1.2.840.10008.5.1.4.1.1.77.1.1.1',  # Video Endoscopic Image Storage
                    '1.2.840.10008.5.1.4.1.1.77.1.2.1',  # Video Microscopic Image Storage
                    '1.2.840.10008.5.1.4.1.1.77.1.4.1',  # Video Photographic Image Storage
                ]
                if ds.SOPClassUID in video_sop_classes:
                    return True

            return False

        except Exception as e:
            print(f"[AVISO] Erro ao verificar se é vídeo DICOM {path}: {e}")
            # Em caso de erro, assumir que não é vídeo para tentar processar
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

    def converter(self) -> bool:
        """
        ### 🔄 Converte arquivos DICOM para JPEG

        Percorre a pasta DICOM e converte cada arquivo para JPEG mantendo resolução.
        Aplica realces e correções de gamma conforme configurado.

        ### 🔄 Returns
        - `bool`: True se pelo menos um arquivo foi convertido com sucesso, False caso contrário.

        ### 💡 Example
        >>> conv = DICOM2JPEG('dicoms', 'images')
        >>> success = conv.converter()
        >>> print(f"Conversão {'bem-sucedida' if success else 'falhou'}")
        """

        # Verificar se os diretórios existem
        if not os.path.exists(self.dcm_path):
            print(f"[ERRO] Diretório DICOM não encontrado: {self.dcm_path}")
            return False

        os.makedirs(self.jpeg_path, exist_ok=True)

        files_processed = 0
        files_converted = 0

        for file in os.listdir(self.dcm_path):
            if not file.lower().endswith('.dcm'):
                continue

            path = os.path.join(self.dcm_path, file)
            files_processed += 1

            try:
                # Verificar se é vídeo/multiframe
                if self.is_video_dicom(path):
                    print(f"[SKIP] Arquivo de vídeo/multiframe: {file}")
                    continue

                # Pular arquivos SR (Structured Report)
                if file.startswith('SR'):
                    print(f"[SKIP] Structured Report: {file}")
                    continue

                # Carregar dataset DICOM
                ds = pydicom.dcmread(path)

                # Converter para PIL Image
                img = self._dicom_to_pil(ds)

                # Aplicar realces opcionais
                if self.enhancements.get('brightness', 1.0) != 1.0:
                    img = ImageEnhance.Brightness(img).enhance(self.enhancements['brightness'])
                if self.enhancements.get('color', 1.0) != 1.0:
                    img = ImageEnhance.Color(img).enhance(self.enhancements['color'])
                if self.enhancements.get('contrast', 1.0) != 1.0:
                    img = ImageEnhance.Contrast(img).enhance(self.enhancements['contrast'])
                if self.enhancements.get('sharpness', 1.0) != 1.0:
                    img = ImageEnhance.Sharpness(img).enhance(self.enhancements['sharpness'])

                # Correção de gamma para nível de preto mais claro
                if self.black_gamma != 1.0:
                    img = self.gamma_correction(img, self.black_gamma)

                # Salvar como JPEG
                output = file.replace('.dcm', '.jpeg')
                output_path = os.path.join(self.jpeg_path, output)
                img.save(output_path, 'JPEG', quality=self.jpeg_quality)

                files_converted += 1
                print(f"[OK] Convertido: {file} -> {output}")

            except Exception as e:
                print(f'[ERRO] {file}: {e}')
                continue

        print(f"Conversão concluída: {files_converted}/{files_processed} arquivos convertidos")
        return files_converted > 0


    @classmethod
    def eliminate_dcm(cls) -> None:
        """
        ### 🧹 Remove arquivos DICOM temporários

        Apaga todos os arquivos .dcm da pasta Dicoms de forma segura,
        com tratamento de erros para arquivos em uso.

        ### 💡 Example
        >>> DICOM2JPEG.eliminate_dcm()
        """
        dcm_dir = "Dicoms"
        if not os.path.exists(dcm_dir):
            print(f"[INFO] Diretório {dcm_dir} não existe")
            return

        files_removed = 0
        files_failed = 0

        for filename in os.listdir(dcm_dir):
            if filename.lower().endswith('.dcm'):
                file_path = os.path.join(dcm_dir, filename)
                try:
                    # Tentar remover o arquivo
                    os.remove(file_path)
                    files_removed += 1
                except PermissionError:
                    print(f'[AVISO] Arquivo em uso, tentando novamente: {filename}')
                    # Tentar novamente após pequena pausa
                    import time
                    time.sleep(0.5)
                    try:
                        os.remove(file_path)
                        files_removed += 1
                    except Exception as e:
                        print(f'[ERRO] Não foi possível remover {filename}: {e}')
                        files_failed += 1
                except Exception as e:
                    print(f'[ERRO] Erro ao remover {filename}: {e}')
                    files_failed += 1

        print(f"[INFO] Limpeza DICOM: {files_removed} removidos, {files_failed} falharam")

    @classmethod
    def eliminate_jpeg(cls) -> None:
        """
        ### 🧹 Remove arquivos JPEG temporários

        Apaga todos os arquivos .jpeg/.jpg da pasta Images de forma segura,
        com tratamento de erros para arquivos em uso.

        ### 💡 Example
        >>> DICOM2JPEG.eliminate_jpeg()
        """
        images_dir = "Images"
        if not os.path.exists(images_dir):
            print(f"[INFO] Diretório {images_dir} não existe")
            return

        files_removed = 0
        files_failed = 0

        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.jpeg', '.jpg')):
                file_path = os.path.join(images_dir, filename)
                try:
                    os.remove(file_path)
                    files_removed += 1
                except PermissionError:
                    print(f'[AVISO] Arquivo em uso, tentando novamente: {filename}')
                    # Tentar novamente após pequena pausa
                    import time
                    time.sleep(0.5)
                    try:
                        os.remove(file_path)
                        files_removed += 1
                    except Exception as e:
                        print(f'[ERRO] Não foi possível remover {filename}: {e}')
                        files_failed += 1
                except Exception as e:
                    print(f'[ERRO] Erro ao remover {filename}: {e}')
                    files_failed += 1

        print(f"[INFO] Limpeza JPEG: {files_removed} removidos, {files_failed} falharam")

    @classmethod
    def eliminate_all(cls) -> None:
        """
        ### 🧹 Remove todos os arquivos temporários

        Apaga DICOMs e JPEGs nas pastas configuradas de forma segura.

        ### 💡 Example
        >>> DICOM2JPEG.eliminate_all()
        """
        print("[INFO] Iniciando limpeza completa...")
        cls.eliminate_dcm()
        cls.eliminate_jpeg()
        print("[INFO] Limpeza completa finalizada")

    @staticmethod
    def _dicom_to_pil(ds: pydicom.Dataset) -> Image.Image:
        """
        ### 🖼️ Converte Dataset DICOM em PIL.Image RGB de 8 bits

        Converte um dataset DICOM para uma imagem PIL RGB de 8 bits,
        mantendo a resolução original e tratando diferentes espaços de cor.
        Compatível com pydicom 3.0+ que já faz conversão automática YBR→RGB.

        ### 🖥️ Parameters
        - `ds` (`pydicom.Dataset`): Dataset DICOM com pixel data válido.

        ### 🔄 Returns
        - `Image.Image`: Imagem PIL no modo RGB, 8 bits por canal.

        ### 💡 Example
        >>> ds = pydicom.dcmread('image.dcm')
        >>> img = DICOM2JPEG._dicom_to_pil(ds)
        >>> img.save('output.jpg')
        """

        # Obter pixel array (pydicom 3.0+ já converte YBR→RGB automaticamente)
        try:
            pixel_array = ds.pixel_array
        except Exception as e:
            raise ValueError(f"Erro ao obter pixel data: {e}")

        # Verificar se há dados de pixel
        if pixel_array is None or pixel_array.size == 0:
            raise ValueError("Pixel data está vazio ou não disponível")

        photo = ds.get('PhotometricInterpretation', '').upper()
        samples_per_pixel = ds.get('SamplesPerPixel', 1)

        # Tratar imagens coloridas (3 canais)
        if samples_per_pixel == 3:
            # Com pydicom 3.0+, pixel_array já retorna RGB para YBR_*
            # Apenas verificar se está no formato correto
            if pixel_array.shape[-1] == 3:  # (H, W, 3)
                # Garantir que está em 8 bits
                if pixel_array.dtype != np.uint8:
                    # Normalizar para 8 bits
                    pixel_array = ((pixel_array - pixel_array.min()) /
                                  (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)

                return Image.fromarray(pixel_array, mode='RGB')
            else:
                raise ValueError(f"Formato de pixel array inesperado para imagem colorida: {pixel_array.shape}")

        # Tratar imagens monocromáticas (1 canal)
        elif samples_per_pixel == 1:
            # Aplicar LUTs se disponíveis
            if hasattr(ds, 'RescaleSlope') or hasattr(ds, 'RescaleIntercept'):
                pixel_array = apply_modality_lut(pixel_array, ds)

            # Aplicar VOI LUT ou windowing se disponível
            if (hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth')) or hasattr(ds, 'VOILUTSequence'):
                pixel_array = apply_voi_lut(pixel_array, ds)

            # Tratar MONOCHROME1 (inverter: preto→branco, branco→preto)
            if photo == 'MONOCHROME1':
                pixel_array = np.max(pixel_array) - pixel_array

            # Normalizar para 8 bits
            if pixel_array.dtype != np.uint8:
                pixel_min, pixel_max = pixel_array.min(), pixel_array.max()
                if pixel_max > pixel_min:
                    pixel_array = ((pixel_array - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
                else:
                    pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)

            # Converter para RGB (replicar canal cinza em 3 canais)
            pixel_array_rgb = np.stack([pixel_array, pixel_array, pixel_array], axis=-1)
            return Image.fromarray(pixel_array_rgb, mode='RGB')

        else:
            raise ValueError(f"Número de samples per pixel não suportado: {samples_per_pixel}")


# Exemplo de uso:
# if __name__ == '__main__':
#     conv = DICOM2JPEG('dicoms', 'imagens', black_gamma=0.8)
#     conv.converter()
