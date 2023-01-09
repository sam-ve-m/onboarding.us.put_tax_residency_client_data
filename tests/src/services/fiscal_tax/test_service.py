from dataclasses import dataclass
from unittest.mock import patch

import pytest
from decouple import Config
from persephone_client import Persephone

from func.src.domain.models.user_data.device_info.model import DeviceInfo

with patch.object(Config, "__call__"):
    from func.src.domain.exceptions.model import InternalServerError, InvalidStepError
    from func.src.domain.models.request.model import TaxResidences, TaxResidenceRequest
    from func.src.domain.models.user_data.onboarding_step.model import UserOnboardingStep
    from func.src.domain.models.user_data.tax_residences.model import TaxResidencesData
    from func.src.repositories.sinacor_types.repository import SinacorTypesRepository
    from func.src.repositories.user.repository import UserRepository
    from func.src.services.fiscal_tax.service import FiscalTaxService
    from func.src.transport.user_step.transport import StepChecker


@dataclass
class TaxResidenceRequestDummy:
    x_thebes_answer: str
    unique_id: str
    tax_residences: TaxResidences
    device_info: DeviceInfo


with patch.object(SinacorTypesRepository, "validate_country", return_value=True):
    tax_residence_model_dummy = TaxResidences(
        **{"tax_residences": [{"country": "USA", "tax_number": "1292-06"}]}
    )

stub_device_info = DeviceInfo({"precision": 1}, "")
tax_residences_request_dummy = TaxResidenceRequestDummy(
    x_thebes_answer="x_thebes_answer",
    unique_id="unique_id",
    tax_residences=tax_residence_model_dummy,
    device_info=stub_device_info,
)
tax_residences_data_dummy = TaxResidencesData(
    unique_id=tax_residences_request_dummy.unique_id,
    tax_residences=tax_residence_model_dummy,
)
onboarding_step_correct_stub = UserOnboardingStep(
    "finished", "external_fiscal_tax_confirmation"
)
onboarding_step_incorrect_stub = UserOnboardingStep("finished", "some_step")


def test___model_tax_residences_data_to_persephone():
    result = (
        FiscalTaxService._FiscalTaxService__model_tax_residences_data_to_persephone(
            tax_residences_data_dummy, stub_device_info
        )
    )
    expected_result = {
        "unique_id": tax_residences_data_dummy.unique_id,
        "tax_residences": tax_residences_data_dummy.tax_residences.dict()[
            "tax_residences"
        ],
        "device_info": stub_device_info.device_info,
        "device_id": stub_device_info.device_id,
    }
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_external_fiscal_tax_residence(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    result = await FiscalTaxService.update_external_fiscal_tax_residence(
        tax_residences_request_dummy
    )
    expected_result = None

    assert result == expected_result
    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_external_fiscal_tax_residence_when_user_is_in_wrong_step(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_incorrect_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    with pytest.raises(InvalidStepError):
        result = await FiscalTaxService.update_external_fiscal_tax_residence(
            tax_residences_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert not persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_external_fiscal_tax_residence_when_cant_send_to_persephone(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (False, 0)
    update_user_mock.return_value = True
    with pytest.raises(InternalServerError):
        result = await FiscalTaxService.update_external_fiscal_tax_residence(
            tax_residences_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(Config, "__call__")
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_external_fiscal_tax_residence_when_cant_update_user_register(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock, mocked_env
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = False
    with pytest.raises(InternalServerError):
        result = await FiscalTaxService.update_external_fiscal_tax_residence(
            tax_residences_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called
