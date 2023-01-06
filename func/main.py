from http import HTTPStatus

from etria_logger import Gladsheim
from flask import request, Request, Response

from func.src.domain.enums.response.code import InternalCode
from func.src.domain.exceptions.model import (
    UnauthorizedError,
    InternalServerError,
    InvalidStepError,
    DeviceInfoRequestFailed,
    DeviceInfoNotSupplied,
)
from func.src.domain.models.jwt_data.model import Jwt
from func.src.domain.models.request.model import TaxResidenceRequest, TaxResidencesMaker
from func.src.domain.models.response.model import ResponseModel
from func.src.services.fiscal_tax.service import FiscalTaxService
from func.src.transport.device_info.transport import DeviceSecurity


async def update_external_fiscal_tax(request: Request = request) -> Response:
    try:
        raw_params = request.json
        x_thebes_answer = request.headers.get("x-thebes-answer")
        x_device_info = request.headers.get("x-device-info")

        jwt = await Jwt.build(x_thebes_answer)
        tax_residences = await TaxResidencesMaker.create(**raw_params)
        device_info = await DeviceSecurity.get_device_info(x_device_info)

        tax_residence_request = TaxResidenceRequest(
            jwt=jwt, tax_residences=tax_residences, device_info=device_info
        )

        external_fiscal_tax = (
            await FiscalTaxService.update_external_fiscal_tax_residence(
                tax_residence_request=tax_residence_request
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

    except DeviceInfoRequestFailed as ex:
        message = "Error trying to get device info"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False,
            code=InternalCode.INTERNAL_SERVER_ERROR,
            message=message,
        ).build_http_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return response

    except DeviceInfoNotSupplied as ex:
        message = "Device info not supplied"
        Gladsheim.error(error=ex, message=message)
        response = ResponseModel(
            success=False,
            code=InternalCode.INVALID_PARAMS,
            message=message,
        ).build_http_response(status=HTTPStatus.BAD_REQUEST)
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
