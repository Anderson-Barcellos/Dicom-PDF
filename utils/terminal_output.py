#!/usr/bin/env python3
"""
🖥️ Terminal Output Customization Module

Este módulo fornece funcionalidades avançadas para formatação de output do terminal,
incluindo traceback customizado, logging colorido e banners para melhor organização
e identificação de erros durante a execução de scripts médicos.
"""

import sys
import traceback
import inspect
import os
from typing import Optional, Any, Callable
from functools import wraps
from datetime import datetime
from enum import Enum

#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# CONFIGURAÇÕES DE CORES E ESTILOS
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

class Colors:
    """🎨 Cores ANSI para terminal"""
    # Cores de texto
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'

    # Cores de fundo
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_MAGENTA = '\033[105m'
    BG_CYAN = '\033[106m'
    BG_WHITE = '\033[107m'

    # Estilos
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'

    # Reset
    RESET = '\033[0m'

    @classmethod
    def disable_colors(cls):
        """Desabilita todas as cores (útil para logs em arquivo)"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable_colors':
                setattr(cls, attr, '')


class LogLevel(Enum):
    """📊 Níveis de logging personalizados"""
    DEBUG = ("🔍", Colors.BLUE)
    INFO = ("ℹ️", Colors.GREEN)
    WARNING = ("⚠️", Colors.YELLOW)
    ERROR = ("❌", Colors.RED)
    CRITICAL = ("🚨", Colors.BG_RED + Colors.WHITE)
    SUCCESS = ("✅", Colors.GREEN)
    PROCESSING = ("🔄", Colors.CYAN)
    BANNER = ("🔥", Colors.MAGENTA)


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# SISTEMA DE LOGGING CUSTOMIZADO
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

class CustomLogger:
    """
    ### 📝 CustomLogger
    Sistema de logging avançado com formatação colorida e identificação precisa de origem.
    Fornece diferentes níveis de log com cores e emojis para melhor identificação visual.

    ### 🖥️ Parameters
        - `name` (`str`): Nome do logger (geralmente o nome do módulo).
        - `enable_colors` (`bool`, optional): Habilita cores no output. Defaults to True.
        - `show_timestamp` (`bool`, optional): Mostra timestamp nas mensagens. Defaults to True.
        - `show_location` (`bool`, optional): Mostra arquivo e linha de origem. Defaults to True.

    ### 🔄 Returns
        - `CustomLogger`: Instância do logger customizado.

    ### 💡 Example

    >>> logger = CustomLogger("DicomProcessor")
    >>> logger.info("Processando arquivo DICOM")
    >>> logger.error("Erro ao converter imagem")

    ### 📚 Notes
    - Suporta todos os níveis padrão de logging
    - Adiciona níveis customizados: SUCCESS e PROCESSING
    - Identifica automaticamente arquivo e linha de origem
    """

    def __init__(self, name: str, enable_colors: bool = True,
                 show_timestamp: bool = True, show_location: bool = True):
        self.name = name
        self.enable_colors = enable_colors
        self.show_timestamp = show_timestamp
        self.show_location = show_location

        if not enable_colors:
            Colors.disable_colors()

    def _get_caller_info(self) -> tuple[str, int, str]:
        """🔍 Obtém informações do chamador (arquivo, linha, função)"""
        frame = inspect.currentframe()
        try:
            # Subir na stack até encontrar o chamador real (fora deste módulo)
            caller_frame = frame.f_back.f_back
            filename = os.path.basename(caller_frame.f_code.co_filename)
            line_number = caller_frame.f_lineno
            function_name = caller_frame.f_code.co_name
            return filename, line_number, function_name
        finally:
            del frame

    def _format_message(self, level: LogLevel, message: str) -> str:
        """🎨 Formata a mensagem com cores e informações de contexto"""
        emoji, color = level.value

        # Timestamp
        timestamp = ""
        if self.show_timestamp:
            timestamp = f"{Colors.DIM}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET} "

        # Informações de localização
        location = ""
        if self.show_location:
            filename, line_number, function_name = self._get_caller_info()
            location = f"{Colors.DIM}[{filename}:{line_number}:{function_name}]{Colors.RESET} "

        # Formatar mensagem principal
        if self.enable_colors:
            formatted_message = f"{timestamp}{location}{color}{Colors.BOLD}{emoji} [{self.name}]{Colors.RESET} {color}{message}{Colors.RESET}"
        else:
            formatted_message = f"{timestamp}{location}{emoji} [{self.name}] {message}"

        return formatted_message

    def debug(self, message: str) -> None:
        """🔍 Log de debug com detalhes técnicos"""
        print(self._format_message(LogLevel.DEBUG, message))

    def info(self, message: str) -> None:
        """ℹ️ Log informativo padrão"""
        print(self._format_message(LogLevel.INFO, message))

    def warning(self, message: str) -> None:
        """⚠️ Log de aviso"""
        print(self._format_message(LogLevel.WARNING, message))

    def error(self, message: str) -> None:
        """❌ Log de erro"""
        print(self._format_message(LogLevel.ERROR, message))

    def critical(self, message: str) -> None:
        """🚨 Log crítico com destaque máximo"""
        print(self._format_message(LogLevel.CRITICAL, message))

    def success(self, message: str) -> None:
        """✅ Log de sucesso"""
        print(self._format_message(LogLevel.SUCCESS, message))

    def processing(self, message: str) -> None:
        """🔄 Log de processamento em andamento"""
        print(self._format_message(LogLevel.PROCESSING, message))


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# SISTEMA DE TRACEBACK CUSTOMIZADO
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

class CustomTracebackHandler:
    """
    ### 🐛 CustomTracebackHandler
    Sistema avançado de tratamento de traceback com formatação visual aprimorada.
    Destaca a linha problemática, mostra contexto do código e fornece sugestões.

    ### 🖥️ Parameters
        - `context_lines` (`int`, optional): Número de linhas de contexto ao redor do erro. Defaults to 3.
        - `show_locals` (`bool`, optional): Mostra variáveis locais no momento do erro. Defaults to False.
        - `color_output` (`bool`, optional): Habilita saída colorida. Defaults to True.

    ### 🔄 Returns
        - `CustomTracebackHandler`: Instância do handler de traceback.

    ### ⚠️ Raises
        - Não levanta exceções, apenas as formata para exibição.

    ### 💡 Example

    >>> handler = CustomTracebackHandler()
    >>> try:
    ...     risky_operation()
    ... except Exception as e:
    ...     handler.format_exception(e)

    ### 📚 Notes
    - Automaticamente instala como handler global se solicitado
    - Suporta diferentes níveis de verbosidade
    - Compatível com todos os tipos de exceção Python
    """

    def __init__(self, context_lines: int = 3, show_locals: bool = False, color_output: bool = True):
        self.context_lines = context_lines
        self.show_locals = show_locals
        self.color_output = color_output

        if not color_output:
            Colors.disable_colors()

    def _read_source_lines(self, filename: str, line_number: int) -> list[str]:
        """📖 Lê linhas do código fonte ao redor do erro"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start = max(0, line_number - self.context_lines - 1)
            end = min(len(lines), line_number + self.context_lines)

            return lines[start:end], start + 1
        except (FileNotFoundError, OSError, UnicodeDecodeError):
            return [], 0

    def _format_source_context(self, filename: str, error_line: int) -> str:
        """🎨 Formata o contexto do código fonte com destaque na linha de erro"""
        lines, start_line = self._read_source_lines(filename, error_line)

        if not lines:
            return f"{Colors.DIM}[Código fonte não disponível]{Colors.RESET}\n"

        result = []
        result.append(f"\n{Colors.BOLD}{Colors.BLUE}📄 Contexto do código ({os.path.basename(filename)}):{Colors.RESET}\n")
        result.append(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")

        for i, line in enumerate(lines):
            current_line = start_line + i
            line_content = line.rstrip()

            if current_line == error_line:
                # Linha com erro - destaque especial
                result.append(f"{Colors.BG_RED}{Colors.WHITE} {current_line:4d} ► {line_content} {Colors.RESET} {Colors.RED}← ERRO AQUI{Colors.RESET}")
            else:
                # Linhas normais de contexto
                result.append(f"{Colors.DIM} {current_line:4d}   {Colors.RESET}{line_content}")

        result.append(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")
        return '\n'.join(result)

    def _format_variables(self, frame) -> str:
        """📊 Formata variáveis locais do frame de erro"""
        if not self.show_locals:
            return ""

        result = []
        result.append(f"\n{Colors.BOLD}{Colors.YELLOW}📊 Variáveis locais:{Colors.RESET}")
        result.append(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")

        try:
            local_vars = frame.f_locals
            for name, value in local_vars.items():
                if not name.startswith('__'):
                    try:
                        str_value = str(value)
                        if len(str_value) > 50:
                            str_value = str_value[:47] + "..."
                        result.append(f"{Colors.CYAN}{name}{Colors.RESET} = {Colors.WHITE}{str_value}{Colors.RESET}")
                    except:
                        result.append(f"{Colors.CYAN}{name}{Colors.RESET} = {Colors.DIM}<não representável>{Colors.RESET}")
        except:
            result.append(f"{Colors.DIM}[Erro ao acessar variáveis locais]{Colors.RESET}")

        result.append(f"{Colors.DIM}{'─' * 40}{Colors.RESET}\n")
        return '\n'.join(result)

    def format_exception(self, exc_type=None, exc_value=None, exc_traceback=None,
                        show_suggestions: bool = True) -> str:
        """
        ### 🐛 format_exception
        Formata uma exceção com contexto visual aprimorado e sugestões de correção.

        ### 🖥️ Parameters
            - `exc_type` (`type`, optional): Tipo da exceção. Se None, usa sys.exc_info().
            - `exc_value` (`Exception`, optional): Valor da exceção. Se None, usa sys.exc_info().
            - `exc_traceback` (`traceback`, optional): Traceback da exceção. Se None, usa sys.exc_info().
            - `show_suggestions` (`bool`, optional): Mostra sugestões de correção. Defaults to True.

        ### 🔄 Returns
            - `str`: Traceback formatado com cores e contexto.
        """
        if exc_type is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()

        if exc_traceback is None:
            return f"{Colors.RED}❌ Nenhuma exceção ativa encontrada{Colors.RESET}"

        result = []

        # Cabeçalho do erro
        result.append(f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD} 🚨 ERRO DETECTADO 🚨 {Colors.RESET}")
        result.append(f"{Colors.RED}{Colors.BOLD}Tipo: {exc_type.__name__}{Colors.RESET}")
        result.append(f"{Colors.RED}Mensagem: {str(exc_value)}{Colors.RESET}")
        result.append(f"{Colors.DIM}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

        # Traceback detalhado
        result.append(f"{Colors.BOLD}{Colors.MAGENTA}🔍 Rastreamento da pilha de chamadas:{Colors.RESET}")
        result.append(f"{Colors.DIM}{'═' * 80}{Colors.RESET}")

        tb_list = traceback.extract_tb(exc_traceback)

        for i, frame_summary in enumerate(tb_list):
            filename = frame_summary.filename
            line_number = frame_summary.lineno
            function_name = frame_summary.name
            line_content = frame_summary.line or '<linha não disponível>'

            # Informações do frame
            result.append(f"\n{Colors.YELLOW}📁 Arquivo: {Colors.RESET}{os.path.basename(filename)}")
            result.append(f"{Colors.YELLOW}🔢 Linha: {Colors.RESET}{line_number}")
            result.append(f"{Colors.YELLOW}⚙️ Função: {Colors.RESET}{function_name}")

            # Se for o último frame (onde ocorreu o erro), mostrar contexto
            if i == len(tb_list) - 1:
                context = self._format_source_context(filename, line_number)
                result.append(context)

                # Mostrar variáveis se solicitado
                try:
                    frame = exc_traceback
                    while frame.tb_next:
                        frame = frame.tb_next
                    variables = self._format_variables(frame.tb_frame)
                    if variables:
                        result.append(variables)
                except:
                    pass
            else:
                result.append(f"{Colors.DIM}   {line_content.strip()}{Colors.RESET}")

        result.append(f"{Colors.DIM}{'═' * 80}{Colors.RESET}")

        # Sugestões de correção
        if show_suggestions:
            suggestions = self._get_error_suggestions(exc_type, str(exc_value))
            if suggestions:
                result.append(f"\n{Colors.BOLD}{Colors.GREEN}💡 Sugestões de correção:{Colors.RESET}")
                result.append(f"{Colors.DIM}{'─' * 50}{Colors.RESET}")
                for suggestion in suggestions:
                    result.append(f"{Colors.GREEN}• {suggestion}{Colors.RESET}")
                result.append("")

        return '\n'.join(result)

    def _get_error_suggestions(self, exc_type: type, message: str) -> list[str]:
        """💡 Gera sugestões baseadas no tipo de erro"""
        suggestions = []

        if exc_type == FileNotFoundError:
            suggestions.extend([
                "Verifique se o caminho do arquivo está correto",
                "Confirme se o arquivo existe no local especificado",
                "Use os.path.exists() para verificar a existência antes de abrir"
            ])

        elif exc_type == PermissionError:
            suggestions.extend([
                "Verifique as permissões do arquivo/diretório",
                "Execute o script como administrador se necessário",
                "Feche o arquivo se estiver aberto em outro programa"
            ])

        elif exc_type == KeyError:
            suggestions.extend([
                "Verifique se a chave existe no dicionário",
                "Use dict.get() com valor padrão para evitar erros",
                "Imprima as chaves disponíveis para debug: print(dict.keys())"
            ])

        elif exc_type == IndexError:
            suggestions.extend([
                "Verifique o tamanho da lista/array antes de acessar",
                "Use len() para verificar limites",
                "Considere usar try/except para índices opcionais"
            ])

        elif exc_type == AttributeError:
            suggestions.extend([
                "Verifique se o objeto possui o atributo/método",
                "Use hasattr() para verificar antes de acessar",
                "Confirme se o objeto foi inicializado corretamente"
            ])

        elif exc_type == ImportError or exc_type == ModuleNotFoundError:
            suggestions.extend([
                "Instale o módulo necessário: pip install <módulo>",
                "Verifique se o nome do módulo está correto",
                "Confirme se está no ambiente virtual correto"
            ])

        elif exc_type == TypeError:
            if "unsupported operand type" in message:
                suggestions.append("Verifique os tipos das variáveis na operação")
            elif "argument" in message:
                suggestions.append("Verifique os argumentos passados para a função")
            suggestions.extend([
                "Use type() ou isinstance() para verificar tipos",
                "Converta os tipos conforme necessário"
            ])

        elif exc_type == ValueError:
            suggestions.extend([
                "Verifique se o valor está no formato esperado",
                "Use validação de entrada antes do processamento",
                "Considere usar try/except para conversões"
            ])

        # Sugestões gerais sempre aplicáveis
        suggestions.extend([
            "Adicione print() statements para debug",
            "Use um debugger para analisar o estado das variáveis",
            "Consulte a documentação da função/biblioteca"
        ])

        return suggestions[:5]  # Limitar a 5 sugestões para não poluir

    def install_as_global_handler(self):
        """🔧 Instala como handler global de exceções não capturadas"""
        def exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Não interceptar Ctrl+C
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            formatted_error = self.format_exception(exc_type, exc_value, exc_traceback)
            print(formatted_error)

        sys.excepthook = exception_handler
        print(f"{Colors.GREEN}✅ Handler de traceback customizado instalado globalmente{Colors.RESET}")


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# SISTEMA DE BANNERS E SEPARADORES
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

def print_banner(title: str, width: int = 80, style: str = "■", color: str = Colors.MAGENTA) -> None:
    """
    ### 🎨 print_banner
    Imprime um banner colorido para separar seções do código.

    ### 🖥️ Parameters
        - `title` (`str`): Título do banner.
        - `width` (`int`, optional): Largura total do banner. Defaults to 80.
        - `style` (`str`, optional): Caractere usado para desenhar o banner. Defaults to "■".
        - `color` (`str`, optional): Cor do banner. Defaults to Colors.MAGENTA.

    ### 🔄 Returns
        - `None`: A função não retorna valor, apenas imprime.

    ### 💡 Example

    >>> print_banner("DATA PROCESSING")
    >>> print_banner("VALIDATION", width=60, style="=", color=Colors.BLUE)

    ### 📚 Notes
    - Automaticamente centraliza o título no banner
    - Suporta diferentes estilos visuais
    - Compatível com o sistema de cores do módulo
    """
    # Calcular espaçamento
    title_with_spaces = f" {title.upper()} "
    remaining_width = width - len(title_with_spaces)
    left_padding = remaining_width // 2
    right_padding = remaining_width - left_padding

    # Construir banner
    banner_line = style * width
    title_line = style * left_padding + title_with_spaces + style * right_padding

    # Imprimir com cor
    print(f"\n{color}{Colors.BOLD}")
    print(f"#{banner_line}")
    print(f"#{title_line}")
    print(f"#{banner_line}")
    print(f"{Colors.RESET}")


def print_section_separator(title: str = "", char: str = "─", width: int = 60) -> None:
    """
    ### ➖ print_section_separator
    Imprime um separador de seção mais discreto.

    ### 🖥️ Parameters
        - `title` (`str`, optional): Título opcional para o separador. Defaults to "".
        - `char` (`str`, optional): Caractere usado no separador. Defaults to "─".
        - `width` (`int`, optional): Largura do separador. Defaults to 60.

    ### 💡 Example

    >>> print_section_separator("Iniciando processamento")
    >>> print_section_separator()  # Apenas linha
    """
    if title:
        title_formatted = f" {title} "
        remaining = width - len(title_formatted)
        left_chars = remaining // 2
        right_chars = remaining - left_chars
        line = char * left_chars + title_formatted + char * right_chars
    else:
        line = char * width

    print(f"{Colors.DIM}{line}{Colors.RESET}")


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# DECORADORES PARA TRATAMENTO AUTOMÁTICO DE ERRO
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

def enhanced_error_handler(
    show_traceback: bool = True,
    show_suggestions: bool = True,
    log_errors: bool = False,
    return_none_on_error: bool = True
):
    """
    ### 🛡️ enhanced_error_handler
    Decorador que adiciona tratamento avançado de erros a qualquer função.

    ### 🖥️ Parameters
        - `show_traceback` (`bool`, optional): Mostra traceback detalhado. Defaults to True.
        - `show_suggestions` (`bool`, optional): Mostra sugestões de correção. Defaults to True.
        - `log_errors` (`bool`, optional): Salva erros em arquivo de log. Defaults to False.
        - `return_none_on_error` (`bool`, optional): Retorna None em caso de erro. Defaults to True.

    ### 🔄 Returns
        - `Callable`: Função decorada com tratamento de erro.

    ### 💡 Example

    >>> @enhanced_error_handler(show_suggestions=True)
    ... def risky_function():
    ...     return 10 / 0
    >>>
    >>> result = risky_function()  # Mostra erro formatado e retorna None

    ### 📚 Notes
    - Preserva assinatura e docstring da função original
    - Compatível com funções síncronas e assíncronas
    - Pode ser configurado por função individualmente
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if show_traceback:
                    handler = CustomTracebackHandler()
                    formatted_error = handler.format_exception(show_suggestions=show_suggestions)
                    print(formatted_error)
                else:
                    print(f"{Colors.RED}❌ Erro em {func.__name__}: {e}{Colors.RESET}")

                if log_errors:
                    # TODO: Implementar logging em arquivo
                    pass

                if return_none_on_error:
                    return None
                else:
                    raise

        return wrapper
    return decorator


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# FUNÇÕES DE CONVENIÊNCIA
#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

def setup_enhanced_terminal(
    enable_colors: bool = True,
    install_global_handler: bool = True,
    logger_name: str = "DicomPDF"
) -> tuple[CustomLogger, CustomTracebackHandler]:
    """
    ### ⚙️ setup_enhanced_terminal
    Configuração rápida do sistema completo de output aprimorado.

    ### 🖥️ Parameters
        - `enable_colors` (`bool`, optional): Habilita cores no terminal. Defaults to True.
        - `install_global_handler` (`bool`, optional): Instala handler global de erros. Defaults to True.
        - `logger_name` (`str`, optional): Nome do logger principal. Defaults to "DicomPDF".

    ### 🔄 Returns
        - `tuple[CustomLogger, CustomTracebackHandler]`: Logger e handler configurados.

    ### 💡 Example

    >>> logger, tb_handler = setup_enhanced_terminal()
    >>> logger.info("Sistema inicializado")
    >>> # Todos os erros não capturados serão formatados automaticamente

    ### 📚 Notes
    - Configuração única para todo o projeto
    - Handler global captura todas as exceções não tratadas
    - Logger pode ser usado em qualquer módulo
    """
    # Configurar logger
    logger = CustomLogger(
        name=logger_name,
        enable_colors=enable_colors,
        show_timestamp=True,
        show_location=True
    )

    # Configurar handler de traceback
    tb_handler = CustomTracebackHandler(
        context_lines=3,
        show_locals=False,
        color_output=enable_colors
    )

    # Instalar handler global se solicitado
    if install_global_handler:
        tb_handler.install_as_global_handler()

    # Banner de inicialização
    print_banner("SISTEMA DE OUTPUT APRIMORADO ATIVO", color=Colors.GREEN)
    logger.success("Sistema de terminal customizado inicializado")
    logger.info(f"Logger: {logger_name}")
    logger.info(f"Cores: {'Habilitadas' if enable_colors else 'Desabilitadas'}")
    logger.info(f"Handler global: {'Instalado' if install_global_handler else 'Não instalado'}")
    print_section_separator()

    return logger, tb_handler


# Instância global para uso direto
if __name__ != "__main__":
    # Configuração automática quando o módulo é importado
    global_logger, global_tb_handler = setup_enhanced_terminal()

    # Aliases para facilitar o uso
    log = global_logger
    banner = print_banner
    separator = print_section_separator
    error_handler = enhanced_error_handler


if __name__ == "__main__":
    # Demonstração do módulo
    print_banner("DEMONSTRAÇÃO DO MÓDULO TERMINAL OUTPUT", color=Colors.CYAN)

    logger = CustomLogger("Demo")

    logger.debug("Esta é uma mensagem de debug")
    logger.info("Esta é uma mensagem informativa")
    logger.warning("Esta é uma mensagem de aviso")
    logger.error("Esta é uma mensagem de erro")
    logger.success("Esta é uma mensagem de sucesso")
    logger.processing("Processando dados...")

    print_section_separator("Demonstração de Traceback")

    tb_handler = CustomTracebackHandler(show_locals=True)

    try:
        # Simular um erro para demonstração
        x = 10
        y = 0
        result = x / y
    except Exception as e:
        formatted = tb_handler.format_exception()
        print(formatted)

    print_section_separator("Demonstração Completa")
    logger.success("Demonstração concluída com sucesso!")
