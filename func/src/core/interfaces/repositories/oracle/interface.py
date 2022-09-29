from abc import ABC, abstractmethod


class IOracle(ABC):
    pool = None

    @abstractmethod
    def query(self, sql) -> list:
        pass

    @abstractmethod
    def execute(self, sql, values) -> None:
        pass
