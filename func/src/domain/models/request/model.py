from typing import List

from pydantic import BaseModel, constr

from src.repositories.sinacor_types.repository import SinacorTypesRepository


class Country(BaseModel):
    country: constr(min_length=3, max_length=3)


class TaxResidence(Country):
    tax_number: str


class TaxResidencesModel(BaseModel):
    tax_residences: List[TaxResidence]

    async def validate_country(self):
        country = self.tax_residences[0].country
        if not await SinacorTypesRepository.validate_country(value=country):
            raise ValueError
