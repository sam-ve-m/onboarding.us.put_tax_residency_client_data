from src.domain.models.user_data.model import UserData


class TaxResidencesData(UserData):
    def __init__(
        self,
        unique_id: str,
        tax_residences: dict,
    ):
        self.unique_id = unique_id
        self.tax_residences = tax_residences

    def get_data_representation(self) -> dict:
        data = {
            "external_exchange_requirements.us.external_fiscal_tax_confirmation": True,
            "tax_residences": self.tax_residences,
        }
        return data
