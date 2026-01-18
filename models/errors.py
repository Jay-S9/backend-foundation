from fastapi import HTTPException


def unauthorized():
    raise HTTPException(
        status_code=401,
        detail={
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid or missing API key"
            }
        }
    )


def forbidden(action: str):
    raise HTTPException(
        status_code=403,
        detail={
            "error": {
                "code": "FORBIDDEN",
                "message": f"Not allowed to perform action: {action}"
            }
        }
    )


def not_found(resource: str):
    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND",
                "message": f"{resource} not found"
            }
        }
    )


def conflict(reason: str):
    raise HTTPException(
        status_code=409,
        detail={
            "error": {
                "code": "CONFLICT",
                "message": reason
            }
        }
    )


def bad_request(message: str):
    raise HTTPException(
        status_code=400,
        detail={
            "error": {
                "code": "BAD_REQUEST",
                "message": message
            }
        }
    )
