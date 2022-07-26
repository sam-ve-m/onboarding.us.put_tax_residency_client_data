from decouple import config
from persephone_client import Persephone

from src.domain.enums.persephone_queue import PersephoneQueue
from src.domain.exceptions.model import InternalServerError, InvalidStepError
from src.domain.models.request.model import TaxResidenceRequest
from src.domain.models.user_data.tax_residences.model import TaxResidencesData
from src.repositories.user.repository import UserRepository
from src.transport.user_step.transport import StepChecker


class FiscalTaxService:
    persephone_client = Persephone

    @staticmethod
    def __model_tax_residences_data_to_persephone(
        tax_residences_data: TaxResidencesData
    ) -> dict:
        data = {
            "unique_id": tax_residences_data.unique_id,
            "tax_residences": tax_residences_data.tax_residences,
        }
        return data

    @classmethod
    async def update_external_fiscal_tax_residence(
        cls, tax_residence_request: TaxResidenceRequest
    ) -> None:

        user_step = await StepChecker.get_onboarding_step(
            x_thebes_answer=tax_residence_request.x_thebes_answer
        )
        if not user_step.is_in_correct_step():
            raise InvalidStepError(
                f"Step BR: {user_step.step_br} | Step US: {user_step.step_us}"
            )

        tax_residences_data = TaxResidencesData(
            unique_id=tax_residence_request.unique_id,
            tax_residences=tax_residence_request.tax_residences.dict()
        )

        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_TAX_RESIDENCE_CONFIRMATION_US.value,
            message=cls.__model_tax_residences_data_to_persephone(
                tax_residences_data
            ),
            schema_name="user_tax_residences_us_schema",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

        user_has_been_updated = await UserRepository.update_user(user_data=tax_residences_data)
        if not user_has_been_updated:
            raise InternalServerError("Error updating user data")
