from PDFMAKER.pdfmaker import MkPDF


def Make_PDF(*args, **kwargs):
    """Wrapper to maintain backward compatibility."""
    return MkPDF(*args, **kwargs)
  


def Make_PDF(*args, **kwargs):
    """Stub function que imita a interface esperada pelos testes."""
    pass
