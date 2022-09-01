from unittest.mock import patch

from etria_logger import Gladsheim
from flask import Flask
from heimdall_client.bifrost import Heimdall, HeimdallStatusResponses
from pytest import mark
from werkzeug.test import Headers
from decouple import Config

with patch.object(Config, "__call__"):
    from main import update_external_fiscal_tax
from src.domain.exceptions.model import (
    InvalidStepError,
    InternalServerError,
)
from src.repositories.sinacor_types.repository import SinacorTypesRepository
from src.services.fiscal_tax.service import FiscalTaxService

request_ok = {"tax_residences": [{"country": "USA", "tax_number": "1292-06"}]}
requests_invalid = [
    {"tax_residencs": [{"country": "USA", "tax_number": "1292-06"}]},
    {"tax_residences": [{"country": "", "tax_number": "1292-06"}]},
    {"tax_residences": [{"country": "USA", "tax_number": None}]},
]

decoded_jwt_ok = {
    "is_payload_decoded": True,
    "decoded_jwt": {"user": {"unique_id": "test"}},
    "message": "Jwt decoded",
}
decoded_jwt_invalid = {
    "is_payload_decoded": False,
    "decoded_jwt": {"user": {"unique_id": "test_error"}},
    "message": "Jwt decoded",
}


@mark.asyncio
@patch.object(SinacorTypesRepository, "validate_country", return_value=True)
@patch.object(Heimdall, "decode_payload")
@patch.object(FiscalTaxService, "update_external_fiscal_tax_residence")
async def test_update_external_fiscal_tax_when_request_is_ok(
    update_external_fiscal_tax_residence_mock,
    decode_payload_mock,
    validate_country_mock,
):
    update_external_fiscal_tax_residence_mock.return_value = None
    decode_payload_mock.return_value = (decoded_jwt_ok, HeimdallStatusResponses.SUCCESS)

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_external_fiscal_tax(request)

        assert (
            result.data
            == b'{"result": null, "message": "Register Updated.", "success": true, "code": 0}'
        )
        assert update_external_fiscal_tax_residence_mock.called


@mark.asyncio
@patch.object(SinacorTypesRepository, "validate_country", return_value=True)
@patch.object(Gladsheim, "error")
@patch.object(Heimdall, "decode_payload")
@patch.object(FiscalTaxService, "update_external_fiscal_tax_residence")
async def test_update_external_fiscal_tax_when_jwt_is_invalid(
    update_external_fiscal_tax_residence_mock,
    decode_payload_mock,
    etria_mock,
    validate_country_mock,
):
    update_external_fiscal_tax_residence_mock.return_value = None
    decode_payload_mock.return_value = (
        decoded_jwt_invalid,
        HeimdallStatusResponses.INVALID_TOKEN,
    )

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_external_fiscal_tax(request)

        assert (
            result.data
            == b'{"result": null, "message": "JWT invalid or not supplied", "success": false, "code": 30}'
        )
        assert not update_external_fiscal_tax_residence_mock.called
        assert etria_mock.called


@mark.asyncio
@mark.parametrize("requests", requests_invalid)
@patch.object(SinacorTypesRepository, "validate_country", return_value=True)
@patch.object(Heimdall, "decode_payload")
@patch.object(Gladsheim, "error")
@patch.object(FiscalTaxService, "update_external_fiscal_tax_residence")
async def test_update_external_fiscal_tax_when_request_is_invalid(
    update_external_fiscal_tax_residence_mock,
    etria_mock,
    decode_payload_mock,
    validate_country_mock,
    requests,
):
    update_external_fiscal_tax_residence_mock.return_value = None
    decode_payload_mock.return_value = (decoded_jwt_ok, HeimdallStatusResponses.SUCCESS)

    app = Flask(__name__)
    with app.test_request_context(
        json=requests,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_external_fiscal_tax(request)

        assert (
            result.data
            == b'{"result": null, "message": "Invalid parameters", "success": false, "code": 10}'
        )
        assert not update_external_fiscal_tax_residence_mock.called
        etria_mock.assert_called()


@mark.asyncio
@patch.object(SinacorTypesRepository, "validate_country", return_value=True)
@patch.object(Gladsheim, "error")
@patch.object(Heimdall, "decode_payload")
@patch.object(FiscalTaxService, "update_external_fiscal_tax_residence")
async def test_update_external_fiscal_tax_when_user_is_in_invalid_oboarding_step(
    update_external_fiscal_tax_residence_mock,
    decode_payload_mock,
    etria_mock,
    validate_country_mock,
):
    update_external_fiscal_tax_residence_mock.side_effect = InvalidStepError("errooou")
    decode_payload_mock.return_value = (
        decoded_jwt_ok,
        HeimdallStatusResponses.SUCCESS,
    )

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_external_fiscal_tax(request)

        assert (
            result.data
            == b'{"result": null, "message": "User in invalid onboarding step", "success": false, "code": 10}'
        )
        assert update_external_fiscal_tax_residence_mock.called
        assert etria_mock.called


@mark.asyncio
@patch.object(SinacorTypesRepository, "validate_country", return_value=True)
@patch.object(Gladsheim, "error")
@patch.object(Heimdall, "decode_payload")
@patch.object(FiscalTaxService, "update_external_fiscal_tax_residence")
async def test_update_external_fiscal_tax_when_internal_server_error_occurs(
    update_external_fiscal_tax_residence_mock,
    decode_payload_mock,
    etria_mock,
    validate_country_mock,
):
    update_external_fiscal_tax_residence_mock.side_effect = InternalServerError(
        "errooou"
    )
    decode_payload_mock.return_value = (
        decoded_jwt_ok,
        HeimdallStatusResponses.SUCCESS,
    )

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_external_fiscal_tax(request)

        assert (
            result.data
            == b'{"result": null, "message": "Failed to update register", "success": false, "code": 100}'
        )
        assert update_external_fiscal_tax_residence_mock.called
        assert etria_mock.called


@mark.asyncio
@patch.object(SinacorTypesRepository, "validate_country", return_value=True)
@patch.object(Heimdall, "decode_payload")
@patch.object(Gladsheim, "error")
@patch.object(FiscalTaxService, "update_external_fiscal_tax_residence")
async def test_update_external_fiscal_tax_when_generic_exception_happens(
    update_external_fiscal_tax_residence_mock,
    etria_mock,
    decode_payload_mock,
    validate_country_mock,
):
    update_external_fiscal_tax_residence_mock.side_effect = Exception("erro")
    decode_payload_mock.return_value = (decoded_jwt_ok, HeimdallStatusResponses.SUCCESS)

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_external_fiscal_tax(request)

        assert (
            result.data
            == b'{"result": null, "message": "Unexpected error occurred", "success": false, "code": 100}'
        )
        assert update_external_fiscal_tax_residence_mock.called
        etria_mock.assert_called()
