import httpx
from .api_error import APIError
from .authentication_error import AuthenticationError
from .product_not_found_error import ProductNotFoundError
from .product_already_found_error import ProductAlreadyFoundError
from functools import wraps


def request_exception_handler(func):
    async def inner_function(*args, **kwargs):
        try:
            
            response = await func(*args, **kwargs)
            match response.status_code:
                case 401: 
                    raise AuthenticationError("Request failed: Invalid access token.")
                case 404: 
                    raise ProductNotFoundError(response.status_code, response.text)
                case 409: 
                    raise ProductAlreadyFoundError(response.status_code, response.text)

            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            # We specifically catch HTTP errors and preserve the original status code
            raise APIError(status_code=e.response.status_code, message=str(e)) from e
        except Exception as e:
            # This catches other errors (e.g., timeouts, network issues)
            # and wraps them in a generic 500 error.
            if isinstance(e, APIError):
                raise  # Don't re-wrap our own exceptions
            raise APIError(status_code=500, message=str(e)) from e
        return response
    return inner_function
