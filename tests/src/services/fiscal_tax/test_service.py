import pytest
from persephone_client import Persephone
from unittest.mock import patch

from src.domain.exceptions.model import InternalServerError
from src.repositories.sinacor_types.repository import SinacorTypesRepository
from src.repositories.step_validator.repository import StepValidator
from src.repositories.user.repository import UserRepository
from src.services.fiscal_tax.service import FiscalTaxService
from src.domain.models.request.model import TaxResidences

with patch.object(SinacorTypesRepository, "validate_country", return_value=True):
    tax_residence_model_dummy = TaxResidences(
        **{"tax_residences": [{"country": "USA", "tax_number": "1292-06"}]}
    )

payload_dummy = {
    "x_thebes_answer": "x_thebes_answer",
    "data": {"user": {"unique_id": "unique_id"}},
}


def test___model_tax_residences_data_to_persephone():
    tax_residences = {"tax": "residence"}
    unique_id = "unique_id"
    result = (
        FiscalTaxService._FiscalTaxService__model_tax_residences_data_to_persephone(
            tax_residences, unique_id
        )
    )
    expected_result = {
        "unique_id": unique_id,
        "tax_residences": tax_residences,
    }
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_external_fiscal_tax_residence(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    result = await FiscalTaxService.update_external_fiscal_tax_residence(
        tax_residence_model_dummy, payload_dummy
    )
    expected_result = None

    assert result == expected_result
    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_external_fiscal_tax_residence_when_cant_send_to_persephone(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (False, 0)
    update_user_mock.return_value = True
    with pytest.raises(InternalServerError):
        result = await FiscalTaxService.update_external_fiscal_tax_residence(
            tax_residence_model_dummy, payload_dummy
        )

    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_external_fiscal_tax_residence_when_cant_update_user_register(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = False
    with pytest.raises(InternalServerError):
        result = await FiscalTaxService.update_external_fiscal_tax_residence(
            tax_residence_model_dummy, payload_dummy
        )

    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called
