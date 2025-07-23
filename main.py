
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
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# SISTEMA DE OUTPUT CUSTOMIZADO E TRACEBACK
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

import os
import time
import json
from pyorthanc import Orthanc
from DicomManager import Unzipper, DICOM2JPEG
from utils import (
    setup_enhanced_terminal,
    print_banner,
    print_section_separator,
    enhanced_error_handler
)
from PDFMAKER import MkPDF
from OCR import process_patient_with_ai, markdown_to_pdf

# Configurar sistema de terminal aprimorado
logger, tb_handler = setup_enhanced_terminal(
    enable_colors=True,
    install_global_handler=True,
    logger_name="DicomPDF-Main"
)

users = json.load(open("Users/users.json"))
user_dir = os.path.join(os.getcwd(), "Users")

def sorting_patients(user, orthanc):
    patients = users[user]["patients"]
    new_patients = []
    patients_uids = [patient for patient in orthanc.get_patients()]
    for patient in patients_uids:
        if orthanc.get_patients_id_shared_tags(patient)["0008,0080"]["Value"] == users[user]["AET"] and patient not in patients:
            patients.append(patient)
            new_patients.append(patient)
            users[user]["patients_names"].append((orthanc.get_patients_id_shared_tags(patient)["0010,0010"]["Value"], orthanc.get_patients_id_shared_tags(patient)["0020,000d"]["Value"]))
    users[user]["patients"] = patients
    json.dump(users, open("Users/users.json", "w"))
    return new_patients


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

users = json.load(open("Users/users.json"))

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


#def imprimir_arquivo(path_arquivo, nome_impressora="EPSON L3250 Series"):
 #   """
 #   🖨️ Função de Impressão de Arquivo
#
 #   Função para enviar um arquivo para impressão em uma impressora específica no Windows.
#
 #   📥 Parâmetros:
 #   :param path_arquivo: 📄 Caminho do arquivo a ser impresso.
 #   :type path_arquivo: str
 #   :param nome_impressora: 🖨️ Nome da impressora a ser utilizada. Se None, utiliza a impressora padrão.
 #   :type nome_impressora: str, optional
##   License: MIT                                                              #
#
 #   :return: None
#
 #   :raises FileNotFoundError: ❌ Se o arquivo especificado não for encontrado.
 #   :raises Exception: ⚠️ Se ocorrer um erro ao enviar o arquivo para a impressora.
#
 #   🧑‍💻 Exemplo:
 #   ```python
#
 #       imprimir_arquivo("relatorio.pdf")
 #       imprimir_arquivo("imagem.jpg", nome_impressora="Minha Impressora")
 #   ```
#
 #   """
 #   if not os.path.exists(path_arquivo):
 #       print(f"Arquivo não encontrado: {path_arquivo}")
 #       return

    # Check if Windows printing is available
    #if not WINDOWS_PRINTING_AVAILABLE:
    #    print(f"⚠️ Impressão não disponível nesta plataforma. Arquivo: {path_arquivo}")
    #    print("💡 A funcionalidade de impressão está disponível apenas no Windows.")
    #    return

    # Get the default printer if no printer is specified
    #if nome_impressora is None:
    #    nome_impressora = win32print.GetDefaultPrinter()
#
    ## Send the file to the printer
    #try:
    #    win32api.ShellExecute(
    #        0,
    #        "print",
    #        path_arquivo,
    #        f'"{nome_impressora}"',
    #        ".",
    #        0
    #    )
    #    print(
    #        f"Arquivo {path_arquivo} enviado para a impressora {nome_impressora}.")
    #except Exception as e:
    #    print(f"Erro ao imprimir o arquivo: {e}")


@enhanced_error_handler(show_suggestions=True, return_none_on_error=True)
def Extract_Convert_Img(file: str, user: str):
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
    'Users/Anders/Patients/PATIENT_NAME/Report/PATIENT_NAME.pdf'
    """
    print_banner("PROCESSAMENTO DE PACIENTE INICIADO")
    logger.processing(f"Processando arquivo: {file}")

    # Extract the file
    unzipper = None
    try:
        unzipper = Unzipper(f"ZIPS/{file}")
        # Unzip the file
        unzipper.unzipper()
        # Get the name of the patient (remove timestamp if present)
        name = unzipper.name
        name = name[15:]
        logger.info(f"Paciente identificado: {name}")

    except Exception as e:
        logger.error(f"Erro na extração: {e}")
        return None
    finally:
        # Garantir que o arquivo ZIP seja fechado
        if unzipper and hasattr(unzipper, 'path'):
            try:
                unzipper.path.close()
            except:
                pass

    # Create patient folders
    base_dir = os.path.join(os.getcwd(), "Users", user, "Patients")
    patient_dir = os.path.join(base_dir, name)
    os.makedirs(patient_dir, exist_ok=True)
    images_dir = os.path.join(patient_dir, "Images")
    reports_dir = os.path.join(patient_dir, "Report")
    dcm_dir = os.path.join(".", "Dicoms")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # CONVERSÃO DE IMAGENS DICOM
    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    try:
        logger.processing("Convertendo imagens DICOM para JPEG...")
        dicom2jpeg = DICOM2JPEG(dcm_dir, images_dir)
        conversion_success = dicom2jpeg.converter()

        if not conversion_success:
            logger.warning(f"Nenhuma imagem foi convertida para {name}")
        else:
            logger.success("Conversão DICOM→JPEG concluída")

    except Exception as e:
        logger.error(f"Erro na conversão DICOM→JPEG: {e}")

    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # GERAÇÃO DE PDF
    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    try:
        logger.processing(f"Gerando PDF para {name}...")
        MkPDF(user, name)
        logger.success("PDF gerado com sucesso")
    except Exception as e:
        logger.error(f"Erro na geração do PDF: {e}")

    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # LIMPEZA DE ARQUIVOS TEMPORÁRIOS
    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    try:
        dicom2jpeg.eliminate_dcm()
        logger.info("Arquivos DICOM temporários removidos")
    except Exception as e:
        logger.warning(f"Erro ao limpar arquivos DICOM: {e}")

    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    # GERAÇÃO DE LAUDO COM IA
    #■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    if OPENAI_API_KEY:
        try:
            logger.processing(f"Gerando laudo com IA para {name}...")
            process_patient_with_ai(
                patient_name=name,
                api_key=OPENAI_API_KEY,
            )

            # Convert markdown to PDF
            md_path = os.path.join(reports_dir, f"{name}.md")
            pdf_path = os.path.join(reports_dir, f"{name}_laudo.pdf")

            if os.path.exists(md_path):
                markdown_to_pdf(md_path, pdf_path)
                logger.success(f"Laudo IA gerado: {name}_laudo.pdf")
            else:
                logger.warning(f"Arquivo markdown não encontrado: {md_path}")

        except Exception as e:
            logger.error(f"Erro ao gerar laudo com IA: {e}")
    else:
        logger.info("Chave da API OpenAI não configurada. Pulando geração de laudo com IA.")

    final_pdf_path = os.path.join(reports_dir, f"{name}.pdf")

    print_section_separator("PROCESSAMENTO CONCLUÍDO")
    logger.success(f"Processamento concluído para paciente: {name}")
    logger.info(f"PDF final salvo em: {final_pdf_path}")

    return final_pdf_path





# ORTHANC

@enhanced_error_handler(show_suggestions=True, return_none_on_error=False)
def orthanc():
    """
    ### 🏥 Função Principal do Orthanc PACS

    Conecta ao servidor Orthanc PACS e monitora continuamente por novos pacientes.
    Quando encontra novos pacientes, baixa os arquivos ZIP e processa automaticamente.

    ### 🔄 Fluxo de Trabalho
    1. Conecta ao servidor Orthanc
    2. Compara pacientes locais (ZIPS) com pacientes no servidor
    3. Baixa novos pacientes como arquivos ZIP
    4. Processa cada novo paciente (extração, conversão, PDF)
    5. Aguarda intervalo antes de verificar novamente

    ### ⚠️ Raises
    - `ConnectionError`: Se não conseguir conectar ao servidor Orthanc
    - `Exception`: Para outros erros durante o processamento
    """
    print_banner("MONITORAMENTO ORTHANC PACS INICIADO")
    logger.info("Iniciando monitoramento do Orthanc PACS...")
    logger.info("Servidor: http://ultrassom.ai:8042")

    try:
        orthanc = Orthanc("http://ultrassom.ai:8042", "admin", "admin")
        logger.success("Conexão estabelecida com sucesso")
    except Exception as e:
        logger.critical(f"Erro ao conectar ao Orthanc: {e}")
        return

    # Garantir que o diretório ZIPS existe
    os.makedirs("ZIPS", exist_ok=True)

    consecutive_errors = 0
    max_consecutive_errors = 5



    def main_loop():
            while True:
                try:
                    #Sorting patients
                    for user in users.keys():

                        logger.processing(f"Buscando pacientes para {user}...")
                        new_patients = sorting_patients(user, orthanc)

                        if  new_patients == []:
                            logger.info(f"Nenhum novo paciente encontrado para {user}")
                            consecutive_errors = 0  # Reset error counter on success
                        else:
                            print_section_separator(f"PROCESSANDO {len(new_patients)} NOVOS PACIENTES")
                            logger.success(f"Encontrados {len(new_patients)} novos pacientes para processamento")

                            for i, patient in enumerate(new_patients, 1):
                                try:
                                    logger.processing(f"[{i}/{len(new_patients)}] Baixando paciente: {patient}")

                                    # Download patient archive
                                    response = orthanc.get_patients_id_archive(str(patient))
                                    zip_path = f"ZIPS/{patient}.zip"

                                    with open(zip_path, "wb") as f:
                                        f.write(response)

                                    file_size = os.path.getsize(zip_path) / 1024  # KB
                                    logger.success(f"Arquivo baixado: {zip_path} ({file_size:.1f} KB)")

                                    # Process patient
                                    time.sleep(1)  # Small delay to ensure file is fully written
                                    result = Extract_Convert_Img(f"{patient}.zip", user)

                                    if result:
                                        logger.success(f"Paciente {patient} processado com sucesso")
                                        time.sleep(10)
                                    else:
                                        logger.warning(f"Falha no processamento do paciente {patient}")

                                except Exception as e:
                                    logger.error(f"Erro ao processar paciente {patient}: {e}")
                                    continue

                            print_section_separator("CICLO DE PROCESSAMENTO CONCLUÍDO")
                            logger.success(f"Processamento concluído para {len(new_patients)} pacientes")
                            consecutive_errors = 0  # Reset error counter on success

                        # Wait before checking again
                        sleep_with_while(10)

                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Erro no ciclo de monitoramento (tentativa {consecutive_errors}/{max_consecutive_errors}): {e}")

                    if consecutive_errors >= max_consecutive_errors:
                        logger.critical(f"Muitos erros consecutivos ({consecutive_errors}). Encerrando monitoramento.")
                        break

                    logger.warning("Aguardando antes de tentar novamente...")
                    sleep_with_while(30)  # Wait longer after error

                except KeyboardInterrupt:
                    print_section_separator("INTERROMPIDO PELO USUÁRIO")
                    logger.warning("Monitoramento interrompido pelo usuário")
                finally:
                     print_section_separator("ENCERRANDO MONITORAMENTO")
                     logger.info("Encerrando monitoramento do Orthanc PACS")

    # Inicia o loop principal de monitoramento
    main_loop()

if __name__ == "__main__":
    orthanc()