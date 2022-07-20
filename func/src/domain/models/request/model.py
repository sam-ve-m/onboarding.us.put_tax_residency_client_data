import asyncio
from typing import List

from pydantic import BaseModel, constr

from src.repositories.sinacor_types.repository import SinacorTypesRepository


class Country(BaseModel):
    country: constr(min_length=3, max_length=3)


class TaxResidence(Country):
    tax_number: str


class TaxResidences(BaseModel):
    tax_residences: List[TaxResidence]


class TaxResidencesMaker(BaseModel):
    @classmethod
    async def create(cls, **data) -> TaxResidences:
        model_object = TaxResidences(**data)
        await cls.__validate_country(model_object)
        return model_object

    @staticmethod
    async def __validate_country(tax_residences_object: TaxResidences):
        validations = []
        for tax_residence in tax_residences_object.tax_residences:
            validations.append(SinacorTypesRepository.validate_country(tax_residence.country))

        are_countries_valid = all(await asyncio.gather(*validations))

        if not are_countries_valid:
            raise ValueError
