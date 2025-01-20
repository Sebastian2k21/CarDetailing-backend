from rest_framework.response import Response


class ServiceException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

    def get_response(self):
        return Response({"message": self.message}, status=self.status_code)
