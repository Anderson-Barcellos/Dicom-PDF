try:
    import zipfile
except ImportError:
    raise SystemExit(
        "Erro: o módulo 'zipfile' não está instalado no seu sistema. Por favor, instale-o e tente novamente."
    )

import os
import shutil


class Unzipper:
    """
    ### 📂 Unzipper Class

    Classe para extrair arquivos DICOM de arquivos ZIP, organizando-os adequadamente
    para processamento posterior. Compatível com estruturas de diretório do Orthanc.

    ### 🖥️ Parameters
    - `path` (`str`): Caminho para o arquivo ZIP contendo imagens DICOM.

    ### 💡 Example

    >>> unzipper = Unzipper("ZIPS/patient.zip")
    >>> unzipper.unzipper()
    >>> print(unzipper.name)  # Nome do paciente extraído
    """

    def __init__(self, path: str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo ZIP não encontrado: {path}")

        self.zip_path = path
        self.path = zipfile.ZipFile(path)
        self.name = self.path.namelist()[0].split("/")[0]
        self.dst_dir = os.path.join(os.getcwd(), "Dicoms")

        # Criar diretório de destino se não existir
        os.makedirs(self.dst_dir, exist_ok=True)

    def unzipper(self) -> None:
        """
        ### 📦 Extrai arquivos DICOM do ZIP

        Extrai todos os arquivos DICOM do arquivo ZIP, renomeando-os adequadamente
        e organizando-os no diretório de destino.

        ### ⚠️ Raises
        - `OSError`: Se houver erro na extração ou movimentação de arquivos.
        - `zipfile.BadZipFile`: Se o arquivo ZIP estiver corrompido.
        """
        try:
            # Extrair todos os arquivos
            self.path.extractall()
            members = self.path.namelist()
            name = self.name

            print(f"Extraindo {len(members)} arquivos para {name}")

            # Processar cada arquivo
            for i, member in enumerate(members):
                if member.endswith('.dcm'):
                    # Caminho do arquivo extraído
                    src_file = os.path.join(".", member)

                    if os.path.exists(src_file):
                        # Nome do arquivo de destino
                        dst_file = os.path.join(self.dst_dir, f"{name}{i:04d}.dcm")

                        # Mover e renomear arquivo
                        shutil.move(src_file, dst_file)
                        print(f"Arquivo movido: {member} -> {dst_file}")
                    else:
                        print(f"Arquivo não encontrado: {src_file}")

            # Limpar diretório temporário
            if os.path.exists(name) and os.path.isdir(name):
                shutil.rmtree(name)
                print(f"Diretório temporário removido: {name}")

            # Fechar arquivo ZIP
            self.path.close()

            # Processar nome do paciente (remover timestamp se presente)


            print(f"Extração concluída para paciente: {self.name}")

        except Exception as e:
            print(f"Erro durante a extração: {e}")
            # Tentar limpar arquivos temporários
            try:
                self.__del__()
                if os.path.exists(self.name) and os.path.isdir(self.name):
                    shutil.rmtree(self.name)
            except:
                pass

    def __del__(self):
        """Cleanup ao destruir o objeto"""
        try:
            if hasattr(self, 'path') and self.path:
                self.path.close()
        except:
            pass

