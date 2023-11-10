from django.conf import settings
from django.db import models

from company.models import Company
from services.utils.models import TimeStampedModel


class Quiz(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    frequency = models.PositiveIntegerField(null=True)


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Result(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField(default=0)
    current_average_value = models.FloatField(default=0.0)
    total_questions = models.PositiveIntegerField(default=0)
    total_correct_answers = models.PositiveIntegerField(default=0)
