class AppException(Exception):
    status_code = 500
    message = "Internal server error"

    def __init__(self, message=None):
        if message:
            self.message = message

    def to_dict(self):
        return {"error": self.message}


class PermissionDenied(AppException):
    status_code = 403
    message = "Permission denied"


class NotFound(AppException):
    status_code = 404
    message = "Resource not found"


class BadRequest(AppException):
    status_code = 400
    message = "Bad request"


class Unauthorized(AppException):
    status_code = 401
    message = "Unauthorized"
