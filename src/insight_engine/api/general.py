def welcome():
    return {"message": "Welcome"}, 200


def echo(body):
    return body, 200


def error_duplicate():
    return {"error": "Duplicate"}, 409


def error_internal():
    return {"error": "Internal error"}, 500


def forbidden():
    return {"error": "Forbidden"}, 403