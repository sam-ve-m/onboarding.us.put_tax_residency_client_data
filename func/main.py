from http import HTTPStatus

from etria_logger import Gladsheim
from flask import request, Request, Response
from heimdall_client import Heimdall, HeimdallStatusResponses

from src.domain.enums.response.code import InternalCode
from src.domain.exceptions.model import (
    UnauthorizedError,
    InternalServerError,
    InvalidStepError,
)
from src.domain.models.request.model import TaxResidencesMaker
from src.domain.models.response.model import ResponseModel
from src.services.fiscal_tax.service import FiscalTaxService


async def update_external_fiscal_tax(request: Request = request) -> Response:
    raw_params = request.json
    x_thebes_answer = request.headers.get("x-thebes-answer")

    try:
        jwt_content, heimdall_status = await Heimdall.decode_payload(
            jwt=x_thebes_answer
        )
        if heimdall_status != HeimdallStatusResponses.SUCCESS:
            raise UnauthorizedError()

        tax_residence_model = await TaxResidencesMaker.create(**raw_params)

        payload = {
            "x_thebes_answer": x_thebes_answer,
            "data": jwt_content["decoded_jwt"],
        }
        external_fiscal_tax = (
            await FiscalTaxService.update_external_fiscal_tax_residence(
                tax_residence=tax_residence_model, payload=payload
            )
        )

        response = ResponseModel(
            result=external_fiscal_tax,
            success=True,
            code=InternalCode.SUCCESS,
            message="Register Updated.",
        ).build_http_response(status=HTTPStatus.OK)
        return response

    except ValueError as ex:
        message = "Invalid parameters"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False, code=InternalCode.INVALID_PARAMS, message=message
        ).build_http_response(status=HTTPStatus.BAD_REQUEST)
        return response

    except UnauthorizedError as ex:
        message = "JWT invalid or not supplied"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False,
            code=InternalCode.JWT_INVALID,
            message=message,
        ).build_http_response(status=HTTPStatus.UNAUTHORIZED)
        return response

    except InvalidStepError as ex:
        message = "User in invalid onboarding step"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False, code=InternalCode.INVALID_PARAMS, message=message
        ).build_http_response(status=HTTPStatus.UNAUTHORIZED)
        return response

    except InternalServerError as ex:
        message = "Failed to update register"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False, code=InternalCode.INTERNAL_SERVER_ERROR, message=message
        ).build_http_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return response

    except Exception as ex:
        message = "Unexpected error occurred"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False, code=InternalCode.INTERNAL_SERVER_ERROR, message=message
        ).build_http_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return response
