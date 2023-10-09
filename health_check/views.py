from django.http import JsonResponse
from pydantic import BaseModel, ValidationError


class HealthCheckRequest(BaseModel):
    status_code: int


def health_check(request):
    # Отримайте дані як рядок з тіла запиту
    request_data_str = request.body.decode('utf-8')

    # Перевірка, чи не порожній рядок
    if not request_data_str.strip():
        # Якщо тіло запиту порожнє або складається лише з пробілів, то поверніть дані відповіді
        response_data = {
            "status_code": 200,
            "detail": "ok",
            "result": "working",
        }
        return JsonResponse(response_data)

    try:
        # Валідація даних, але не розкодування JSON
        request_data = HealthCheckRequest.parse_raw(request_data_str)
    except ValidationError as e:
        error_message = str(e)
        return JsonResponse({"error": error_message}, status=400)

    response_data = {
        "status_code": request_data.status_code,
        "detail": "ok",
        "result": "working",
    }

    return JsonResponse(response_data)
