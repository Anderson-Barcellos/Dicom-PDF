from PDFMAKER.pdfmaker import MkPDF


def Make_PDF(*args, **kwargs):
    """Wrapper to maintain backward compatibility."""
    return MkPDF(*args, **kwargs)
