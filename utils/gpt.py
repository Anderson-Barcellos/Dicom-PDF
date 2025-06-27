from typing import Protocol, Callable

class ClientProtocol(Protocol):
    def complete(self, prompt: str) -> str:
        ...

def replace_text_with_gpt(text: str, client: ClientProtocol) -> str:
    """Use a GPT-like client to transform text."""
    if client is None:
        raise ValueError("client must be provided")
    return client.complete(text)
