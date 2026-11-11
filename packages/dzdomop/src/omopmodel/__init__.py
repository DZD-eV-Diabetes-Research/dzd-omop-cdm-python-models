from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omopmodel.vocab import VocabulariesLoader

__all__ = ["VocabulariesLoader"]


def __getattr__(name: str):
    # Imported on first use, so `import omopmodel` stays cheap.
    if name == "VocabulariesLoader":
        from omopmodel.vocab import VocabulariesLoader

        return VocabulariesLoader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
