from func.src.domain.models.request.model import TaxResidences
from func.src.domain.models.user_data.model import UserData


class TaxResidencesData(UserData):
    def __init__(
        self,
        unique_id: str,
        tax_residences: TaxResidences,
    ):
        self.unique_id = unique_id
        self.tax_residences = tax_residences

    def get_data_representation(self) -> dict:
        data = {
            **self.tax_residences.dict(),
            "external_exchange_requirements.us.external_fiscal_tax_confirmation": True,
        }
        return data
