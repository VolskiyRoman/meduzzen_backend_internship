import csv

from django.http import HttpResponse


def generate_csv_response(results, filename, fields):
    serialized_data = [
        {
            'id': result.id,
            'user': str(result.user),
            'company': result.quiz.company.name,
            'quiz': str(result.quiz.title),
            'score': result.current_average_value,
            'date_passed': result.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for result in results
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.DictWriter(response, fieldnames=fields)
    writer.writeheader()
    writer.writerows(serialized_data)

    return response
