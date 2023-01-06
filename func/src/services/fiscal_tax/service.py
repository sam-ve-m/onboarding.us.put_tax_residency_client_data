from decouple import config
from persephone_client import Persephone

from func.src.domain.enums.persephone_queue import PersephoneQueue
from func.src.domain.exceptions.model import InternalServerError, InvalidStepError
from func.src.domain.models.request.model import TaxResidenceRequest
from func.src.domain.models.user_data.device_info.model import DeviceInfo
from func.src.domain.models.user_data.tax_residences.model import TaxResidencesData
from func.src.repositories.user.repository import UserRepository
from func.src.transport.user_step.transport import StepChecker


class FiscalTaxService:
    persephone_client = Persephone

    @classmethod
    async def update_external_fiscal_tax_residence(
        cls, tax_residence_request: TaxResidenceRequest
    ):
        tax_residences_data = TaxResidencesData(
            unique_id=tax_residence_request.unique_id,
            tax_residences=tax_residence_request.tax_residences,
        )
        await cls.__validate_onboarding_step(
            x_thebes_answer=tax_residence_request.x_thebes_answer
        )
        await cls.__send_to_persephone(
            tax_residences_data=tax_residences_data,
            device_info=tax_residence_request.device_info,
        )
        await cls.__update_user(tax_residences_data=tax_residences_data)

    @staticmethod
    async def __validate_onboarding_step(x_thebes_answer: str):
        user_step = await StepChecker.get_onboarding_step(
            x_thebes_answer=x_thebes_answer
        )
        if not user_step.is_in_correct_step():
            raise InvalidStepError(
                f"Step BR: {user_step.step_br} | Step US: {user_step.step_us}"
            )

    @classmethod
    async def __send_to_persephone(
        cls, tax_residences_data: TaxResidencesData, device_info: DeviceInfo
    ):
        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_TAX_RESIDENCE_CONFIRMATION_US.value,
            message=cls.__model_tax_residences_data_to_persephone(
                tax_residences_data, device_info
            ),
            schema_name="user_tax_residences_us_schema",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

    @staticmethod
    async def __update_user(tax_residences_data: TaxResidencesData):
        user_has_been_updated = await UserRepository.update_user(
            user_data=tax_residences_data
        )
        if not user_has_been_updated:
            raise InternalServerError("Error updating user data")

    @staticmethod
    def __model_tax_residences_data_to_persephone(
        tax_residences_data: TaxResidencesData, device_info: DeviceInfo
    ) -> dict:
        data = {
            "unique_id": tax_residences_data.unique_id,
            **tax_residences_data.tax_residences.dict(),
            "device_info": device_info.device_info,
            "device_id": device_info.device_id,
        }
        return data
