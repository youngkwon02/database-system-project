def success(status, message, data):
    return {
        "status": status,
        "success": True,
        "message": message,
        "data": data
    }


def fail(status, message):
    return {
        "status": status,
        "success": False,
        "message": message,
    }
