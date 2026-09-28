# Dicom-PDF

Automatiza o download de exames DICOM de um servidor Orthanc, a extração dos arquivos, a conversão das imagens para JPEG e a geração de PDFs com as imagens dos exames.

## Visão geral

O projeto foi criado para facilitar o processamento de exames médicos armazenados em um servidor Orthanc. O fluxo principal é:

1. Conectar ao servidor Orthanc.
2. Baixar os arquivos ZIP dos pacientes.
3. Extrair os arquivos DICOM.
4. Converter as imagens DICOM para JPEG.
5. Gerar um PDF com as imagens convertidas.
6. Remover pastas temporárias usadas durante o processamento.

O script principal é `main.py`. Ao ser executado, ele chama `Change()` e, em seguida, `PDF_Process()`.

## Funcionalidades

- **Download de todos os pacientes:** consulta os pacientes disponíveis no Orthanc e baixa o arquivo ZIP de cada um.
- **Download de um paciente:** disponibiliza a função `Down_One(id)` para baixar o arquivo ZIP de um paciente específico.
- **Extração e conversão:** extrai o conteúdo do ZIP, converte os arquivos DICOM para JPEG e inicia a geração do PDF.
- **Geração de PDFs:** delega a criação do PDF ao módulo `PDFMAKER.pdfmaker`.
- **Mesclagem de PDFs:** inclui funções para unir PDFs em um único arquivo.

## Estrutura esperada

O `main.py` espera encontrar ou utilizar as seguintes pastas:

```text
.
├── main.py
├── DicomManager/
│   ├── unzip.py
│   └── DICOM.py
├── PDFMAKER/
│   └── pdfmaker.py
├── ZIPS/
├── Dicoms/
└── Images/
```

- **`ZIPS/`**: arquivos ZIP baixados do Orthanc e processados pelo script.
- **`Dicoms/`**: arquivos DICOM extraídos dos ZIPs.
- **`Images/`**: imagens JPEG geradas a partir dos DICOMs.
- **`DicomManager/`** e **`PDFMAKER/`**: módulos do projeto responsáveis pela extração, conversão e criação de PDFs.

A função `check_folder()` cria `Dicoms/` e `Images/` quando necessário, mas não cria `ZIPS/`. Além disso, ela não é chamada automaticamente no fluxo principal. Crie `ZIPS/` antes de executar o script e confirme que os módulos auxiliares criam ou organizam as demais pastas conforme esperado.

## Requisitos

O projeto utiliza Python e depende, pelo menos, dos seguintes pacotes:

- `pyorthanc` — comunicação com o Orthanc.
- `PyPDF2` — leitura e escrita de arquivos PDF.

Também depende dos módulos locais `DicomManager` e `PDFMAKER`.

Instale as dependências externas no ambiente Python utilizado para executar o projeto. Se o repositório tiver um arquivo `requirements.txt`, use-o para instalar as versões especificadas:

```bash
pip install -r requirements.txt
```

Caso não exista um arquivo de dependências, verifique quais versões são compatíveis com os módulos do projeto antes de instalá-las.

## Configuração do Orthanc

O script define diretamente no código o endereço do servidor Orthanc e as credenciais de acesso. Antes de executar o projeto:

1. Configure o endereço correto do seu servidor.
2. Use credenciais autorizadas e com o menor nível de acesso necessário.
3. Evite armazenar credenciais no código, no histórico do Git ou em arquivos públicos.
4. Prefira carregar endereço e credenciais por variáveis de ambiente ou por um arquivo de configuração local que não seja versionado.

**Importante:** este projeto processa dados médicos. Use-o somente em ambientes autorizados e implemente controles adequados de acesso, armazenamento e retenção dos arquivos.

## Como executar

1. Clone o repositório e entre na pasta do projeto.
2. Instale as dependências.
3. Configure o acesso ao Orthanc de forma segura.
4. Crie a pasta `ZIPS/`, caso ainda não exista.
5. Execute:

```bash
python main.py
```

No fluxo atual, o script consulta os pacientes e baixa os arquivos ZIP por meio de `Change()`. Depois, `PDF_Process()` percorre os arquivos da pasta `ZIPS/` e processa os que terminam em `.zip`.

## Fluxo de processamento

Para cada arquivo ZIP encontrado em `ZIPS/`, a função `Extract_Convert_Img()`:

1. Extrai o arquivo para `Dicoms/`.
2. Obtém o nome associado ao arquivo extraído.
3. Converte os arquivos DICOM encontrados em `Dicoms/` para JPEG em `Images/`.
4. Chama `MkPDF(name)` para gerar o PDF.
5. Chama `eliminate_folders()` para remover pastas usadas no processo de conversão.
6. Exibe uma mensagem informando a conclusão da extração e conversão.

O formato, o local de saída e a organização final dos PDFs dependem da implementação de `MkPDF()` no módulo `PDFMAKER.pdfmaker`.

## Funções disponíveis em `main.py`

| Função | Descrição |
|---|---|
| `Down_All()` | Baixa os arquivos ZIP de todos os pacientes listados no Orthanc e os grava em `ZIPS/`. |
| `Down_One(id)` | Baixa o arquivo ZIP do paciente indicado pelo identificador `id`. |
| `Change()` | Consulta os pacientes e inicia o download de todos eles. Apesar do nome, atualmente não compara alterações: o trecho relacionado ao controle de mudanças está comentado. |
| `PDF_Process()` | Percorre `ZIPS/` e processa os arquivos com extensão `.zip`. |
| `Extract_Convert_Img(file)` | Extrai um ZIP, converte DICOM para JPEG e solicita a criação do PDF. |
| `PDFMerger(output_filename)` | Une os PDFs encontrados no diretório atual em um arquivo de saída. |
| `MergePDF(file1, file2)` | Une dois PDFs e grava o resultado sobre o caminho de `file1`. |

## Mesclagem de PDFs

A função `PDFMerger()` procura arquivos `.pdf` no diretório atual, ordena seus nomes e os reúne em `merged_document.pdf` por padrão:

```python
PDFMerger("exames_unidos.pdf")
```

A função `MergePDF(file1, file2)` une dois arquivos e grava o resultado no caminho de `file1`. Verifique se o arquivo original pode ser sobrescrito antes de usá-la.

As funções de mesclagem não são chamadas pelo fluxo principal atual. A compatibilidade de `MergePDF()` também deve ser conferida com a versão instalada do `PyPDF2`, pois ela utiliza nomes de métodos da API antiga.

## Observações e limitações

- `main.py` executa downloads e processamento automaticamente quando iniciado.
- `Change()` baixa novamente os arquivos de todos os pacientes; o mecanismo de detecção de alterações está comentado.
- A pasta `ZIPS/` precisa existir antes do download, pois o script não a cria.
- O tratamento de erros em `PDF_Process()` imprime a exceção, mas não registra detalhes em um log persistente.
- O comportamento em caso de ZIP corrompido, arquivos DICOM inválidos ou falha na conexão depende, em parte, das implementações dos módulos auxiliares.
- Antes de processar grandes volumes, teste o fluxo com dados de teste e confirme os locais de entrada e saída dos arquivos.
- Avalie se os arquivos temporários e PDFs gerados precisam ser apagados após o processamento, de acordo com as políticas da sua organização.

## Segurança e privacidade

Arquivos DICOM e PDFs de exames podem conter informações pessoais e dados de saúde. Portanto:

- Não publique arquivos de pacientes ou credenciais em repositórios, issues ou logs.
- Restrinja o acesso às pastas `ZIPS/`, `Dicoms/`, `Images/` e aos PDFs gerados.
- Use conexões e servidores protegidos conforme as políticas da sua organização.
- Defina procedimentos de retenção e exclusão segura para arquivos temporários e resultados.
- Execute o projeto somente com autorização para acessar e processar os exames.

## Licença

Consulte o arquivo de licença do repositório. Se não houver um, entre em contato com os responsáveis pelo projeto antes de redistribuir ou utilizar o código em outros contextos.
