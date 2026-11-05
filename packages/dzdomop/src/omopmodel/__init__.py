from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omopmodel.vocabularies_loader import VocabulariesLoader

__all__ = ["VocabulariesLoader"]


def __getattr__(name: str):
    # The loader needs the optional extras (sqlmodel, pg8000, tqdm). Import it on first
    # use, so the models work with a plain `pip install dzdomop`.
    if name == "VocabulariesLoader":
        try:
            from omopmodel.vocabularies_loader import VocabulariesLoader
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"{e}. The vocabulary loader needs extra dependencies: "
                'pip install "dzdomop[sqlmodel,pg8000,progress]"',
                name=e.name,
            ) from e
        return VocabulariesLoader
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
