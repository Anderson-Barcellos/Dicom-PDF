import os
import sys
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.gpt import replace_text_with_gpt


def test_gpt_replacement_called():
    fake_client = mock.Mock()
    fake_client.complete.return_value = "novo texto"
    result = replace_text_with_gpt("texto", client=fake_client)
    fake_client.complete.assert_called_once_with("texto")
    assert result == "novo texto"
