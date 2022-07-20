from decouple import config
from persephone_client import Persephone

from src.domain.enums.persephone_queue import PersephoneQueue
from src.domain.exceptions.model import InternalServerError
from src.domain.models.request.model import TaxResidences
from src.repositories.step_validator.repository import StepValidator
from src.repositories.user.repository import UserRepository


class FiscalTaxService:
    persephone_client = Persephone

    @staticmethod
    def __model_tax_residences_data_to_persephone(
        tax_residences: dict, unique_id: str
    ) -> dict:
        data = {
            "unique_id": unique_id,
            "tax_residences": tax_residences,
        }
        return data

    @classmethod
    async def update_external_fiscal_tax_residence(
        cls, tax_residence: TaxResidences, payload: dict
    ) -> None:

        await StepValidator.validate_onboarding_step(
            x_thebes_answer=payload["x_thebes_answer"]
        )
        user_tax_residences = tax_residence.dict()
        unique_id = payload["data"]["user"]["unique_id"]

        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_TAX_RESIDENCE_CONFIRMATION_US.value,
            message=cls.__model_tax_residences_data_to_persephone(
                tax_residences=user_tax_residences,
                unique_id=unique_id,
            ),
            schema_name="user_tax_residences_us_schema",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

        was_updated = await UserRepository.update_user(
            unique_id=unique_id,
            new={
                "external_exchange_requirements.us.external_fiscal_tax_confirmation": True,
                "tax_residences": user_tax_residences,
            },
        )
        if not was_updated:
            raise InternalServerError("Error updating user data")
