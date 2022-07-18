from abc import ABC, abstractmethod

from src.domain.enums.terms import TermsFileType


class ITermRepository(ABC):
    @classmethod
    @abstractmethod
    async def get_term_link_by_version(cls, term: TermsFileType, version: str) -> str:
        pass

    @classmethod
    @abstractmethod
    async def _generate_term_url(
        cls, term_path: str, file_name: str, file_extension: str
    ) -> str:
        pass
