from django.db.models import Sum


def calculate_average_score(user_results):
    total_questions = user_results.aggregate(total_questions=Sum('questions')).get('total_questions') or 0
    total_correct_answers = user_results.aggregate(total_correct=Sum('correct_answers')).get('total_correct') or 0

    average_score = (total_correct_answers / total_questions) * 100 if total_questions > 0 else 0
    return round(average_score, 2)
