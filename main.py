
"""
📄 Dicom-PDF Main Module
Este módulo automatiza o processo de extração, conversão e geração de relatórios de imagens DICOM a partir de arquivos ZIP. Ele integra-se ao PACS Orthanc para gerenciamento de pacientes, converte imagens DICOM para o formato JPEG e gera relatórios em PDF. Além disso, inclui funcionalidade específica para impressão no Windows.
📥 Funções Principais:
- `sleep_with_while(seconds)`: Exibe uma contagem regressiva enquanto aguarda o tempo especificado.
- `imprimir_arquivo(path_arquivo, nome_impressora)`: Envia um arquivo para impressão em uma impressora específica no Windows.
- `Extract_Convert_Img(file)`: Extrai imagens DICOM de um arquivo ZIP, converte-as para JPEG e gera um relatório em PDF.
- `orthanc()`: Integra-se ao Orthanc PACS para monitorar e processar novos pacientes.
- Este módulo utiliza parâmetros internos e funções auxiliares para realizar suas operações. Consulte as docstrings individuais para detalhes.
📤 Retornos:
- O módulo retorna caminhos de arquivos gerados, como PDFs, e mensagens de status para o usuário.
⚠️ Exceções:
- `FileNotFoundError`: Se arquivos especificados não forem encontrados.
- `OSError`: Se ocorrerem erros durante a extração ou conversão.
- `Exception`: Para erros gerais, como falhas na integração com Orthanc ou na impressão.
"""

import os
import time
from pyorthanc import Orthanc
from DicomManager.unzip import Unzipper
from DicomManager.DICOM import DICOM2JPEG
from PDFMAKER.pdfmaker import MkPDF


###############################################################################
#                         WINDOWS-SPECIFIC IMPORTS                            #
#                     (Only available on Windows OS)                          #
###############################################################################

#try:
#    import win32print
#    import win32api
#    WINDOWS_PRINTING_AVAILABLE = True
#except ImportError:
#    # Not on Windows or pywin32 not installed
#    WINDOWS_PRINTING_AVAILABLE = False

###############################################################################
#                                                                             #
#   Dicom-PDF Main Script                                                     #
#                                                                             #
#   This script automates the extraction, conversion, and reporting of DICOM   #
#   images from ZIP archives. It integrates with Orthanc PACS for patient      #
#   management, converts DICOM images to JPEG, and generates PDF reports.      #
#   Windows-specific printing functionality is included for report output.     #
#                                                                             #
#   Author: Anders                                                            #
#   Repository: https://github.com/AndersDeveloper/Dicom-PDF                  #
#                                                                             #
###############################################################################

def sleep_with_while(seconds):
    """
    ### ⏳ Timer Function with While Loop
    Function to create a timer that displays the remaining time every second using a `while` loop.
    #### 📥 Parameters:
        seconds: int
    ### 🕒 Returns:    
        None
    
    #### Example:
    
    ```python
sleep_with_while(10)
    ```
    """ 
    start_time = time.time()  # Tempo inicial
    while time.time() - start_time < seconds:
        elapsed_time = time.time() - start_time
        remaining_time = seconds - elapsed_time
        print(f"Faltam {int(remaining_time)} segundos...")
        time.sleep(1)  # Aguardar um segundo entre cada iteração
    print("Tempo finalizado!")


def imprimir_arquivo(path_arquivo, nome_impressora="EPSON L3250 Series"):
    """
    🖨️ Função de Impressão de Arquivo

    Função para enviar um arquivo para impressão em uma impressora específica no Windows.

    📥 Parâmetros:
    :param path_arquivo: 📄 Caminho do arquivo a ser impresso.
    :type path_arquivo: str
    :param nome_impressora: 🖨️ Nome da impressora a ser utilizada. Se None, utiliza a impressora padrão.
    :type nome_impressora: str, optional
#   License: MIT                                                              #

    :return: None

    :raises FileNotFoundError: ❌ Se o arquivo especificado não for encontrado.
    :raises Exception: ⚠️ Se ocorrer um erro ao enviar o arquivo para a impressora.

    🧑‍💻 Exemplo:
    ```python

        imprimir_arquivo("relatorio.pdf")
        imprimir_arquivo("imagem.jpg", nome_impressora="Minha Impressora")
    ```

    """
    if not os.path.exists(path_arquivo):
        print(f"Arquivo não encontrado: {path_arquivo}")
        return

    # Check if Windows printing is available
    if not WINDOWS_PRINTING_AVAILABLE:
        print(f"⚠️ Impressão não disponível nesta plataforma. Arquivo: {path_arquivo}")
        print("💡 A funcionalidade de impressão está disponível apenas no Windows.")
        return

    # Get the default printer if no printer is specified
    if nome_impressora is None:
        nome_impressora = win32print.GetDefaultPrinter()

    # Send the file to the printer
    try:
        win32api.ShellExecute(
            0,
            "print",
            path_arquivo,
            f'"{nome_impressora}"',
            ".",
            0
        )
        print(
            f"Arquivo {path_arquivo} enviado para a impressora {nome_impressora}.")
    except Exception as e:
        print(f"Erro ao imprimir o arquivo: {e}")


def Extract_Convert_Img(file: str):
    """
    🖼️ Extract_Convert_Img
    Extracts DICOM images from a ZIP file, converts them to JPEG format, and generates a PDF report. This function is part of a medical imaging workflow, facilitating the conversion and compilation of DICOM images for further analysis and reporting.

    ### 🖥️ Parameters
    - `file` (`str`): The name of the ZIP file containing DICOM images. The file should be located in the current working directory.

    ### 🔄 Returns
    - `str`: The path to the created PDF file. After its generation, an OCR process can be executed to create the corresponding text file.

    ### ⚠️ Raises
    - `FileNotFoundError`: If the specified ZIP file does not exist.
    - `OSError`: If there is an error during the extraction or conversion process.

    ### 💡 Example

    >>> Extract_Convert_Img("patient_data.zip")
    'Pacientes/Anders/Report/Anders.pdf'
    """
    # Extract the file
    unzipper = Unzipper(f"{file}", "Dicoms")
    # Unzip the file
    unzipper.unzipper()
    # Get the name of the patient
    name = unzipper.name[15:]
    print(name)

    # Create patient folders
    base_dir = os.path.join("Patients", name)
    images_dir = os.path.join(base_dir, "Images")
    reports_dir = os.path.join(base_dir, "Report")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    dicom2jpeg = DICOM2JPEG("./Dicoms", images_dir)
    dicom2jpeg.converter()

    # Generate the PDF
    MkPDF(name)
    dicom2jpeg.eliminate_dcm()

    return os.path.join(reports_dir, f"{name}.pdf")

    



# ORTHANC

def orthanc():
    orthanc = Orthanc("https://ultrassom.ai", "anders", "andi110386")
    try:
        while True:
            # Load pacientes with ZIPS folder
            oldest_patients = [patient[:-4] for patient in os.listdir("ZIPS")]
            print(oldest_patients)


            # Update patients
            latest_patients = orthanc.get_patients()
            if oldest_patients == latest_patients:
                print("Nenhum novo paciente encontrado, Anders.... Procurando")
                sleep_with_while(20)
            else:
                new_patients = [p for p in latest_patients if p not in oldest_patients]

                # Process for each new patient
                for patient in new_patients:
                    response = orthanc.get_patients_id_archive(str(patient))
                    with open(f"ZIPS/{patient}.zip", "wb") as f:
                        f.write(response)
                    Extract_Convert_Img(f"{patient}.zip")

                # Update patients            # Wait a moment (seconds) before checking again
                sleep_with_while(10)
    except Exception as e:
        print(e)
orthanc()
