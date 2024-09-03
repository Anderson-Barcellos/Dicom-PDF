try:
    import zipfile
except ImportError:
    raise SystemExit(
        "Erro: o módulo 'modulo_especifico' não está instalado no seu sistema. Por favor, instale-o e tente novamente."
    )

import os


class Unzipper(object):
    """Class to intanciate an object to unzip files with dicom images.

    Parameters
    ----------
    - path: str
        Path to the zip file.
    - folder: str
        Folder to extract the files.

    """

    internal_path = f"/Unknown Study/US/"

    def __init__(self, path: str, folder: str) -> None:
        self.path = zipfile.ZipFile(f"ZIPS/{path}")
        self.folder = folder
        self.name = self.path.namelist()[0].split("/")[0]

    def unzipper(self) -> None:
        """Extracts files from zip file.
        Parameters
        ----------
        - path: str
            Path to the zip file.
        - folder: str
            Folder to extract the files.
        """
        import shutil

        self.path.extractall()
        members = self.path.namelist()
        print("Members: ", members)
        name = self.name
        print("Name: ", name)

        # Caminho do diretório atual

        # Caminho do diretório de destino
        dst_dir = self.folder
        # Lista todos os arquivos no diretório atual
        i = 0
        for i in range(0, len(members)):
            src_dir = f"./{members[i]}"[0:-12]
            print("Src_dir: ", src_dir)
            # Caminho completo do arquivo
            file = f"./{members[i].split(sep='/')[-1]}"
            src_file = os.path.join(src_dir, file)
            shutil.move(src_file, dst_dir)
            os.rename(f"{dst_dir}/{file}", f"{dst_dir}/{name}{i}.dcm")
            i += 1
        shutil.rmtree(name)


