import csv

from django.core.cache import cache
from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Question, Quiz, Result
from quiz_app.permissions import IsCompanyAdminOrOwner
from quiz_app.serializers import QuestionSerializer, QuizCreateSerializer
from services.utils.average_value import calculate_average_score


class QuizManagementViewSet(viewsets.ModelViewSet):
    serializer_class = QuizCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdminOrOwner]
    queryset = Quiz.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'complete_quiz', 'average_score']:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsCompanyAdminOrOwner()]

    def get_queryset(self):
        return (
            Quiz.objects
            .filter(company__members=self.request.user)
            .prefetch_related('company')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='delete-question', methods=['POST'])
    def delete_question(self, request, pk=None):
        quiz = self.get_object()
        question_id = request.data.get('question_id')

        question = quiz.questions.filter(id=question_id).first()

        if question:
            remaining_questions_count = quiz.questions.count()
            if remaining_questions_count <= 2:
                return Response("At least 2 questions are required. Could not delete the question.",
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                question.delete()
                return Response("Question deleted successfully", status=status.HTTP_200_OK)
        else:
            return Response("Question not found", status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, url_path='add-question', methods=['POST'])
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data['quiz'] = quiz
            serializer.save()

            return Response("Question added successfully", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path='complete', methods=['POST'])
    def complete_quiz(self, request, pk=None):
        quiz = self.get_object()
        user_input = request.data.get('user_input')

        quiz_with_answers = Quiz.objects.prefetch_related(
            Prefetch('questions', queryset=Question.objects.prefetch_related('answers'))
        ).get(id=quiz.id)

        questions = quiz_with_answers.questions.count()
        correct_answers = 0

        for request_data in user_input:
            question_id = request_data.get('question')
            answers = request_data.get('answers')

            question = next((q for q in quiz_with_answers.questions.all() if q.id == question_id), None)

            if question:
                correct_answer_ids = [answer.id for answer in question.answers.all() if answer.is_correct]
                if set(answers) == set(correct_answer_ids):
                    correct_answers += 1

                key = f"quiz:{quiz.id}:user:{request.user.id}:question:{question_id}"
                value = f"correct_answers:{correct_answers}, user_answers:{answers}"
                cache.set(key, value, timeout=172800)

        last_result = Result.objects.filter(quiz=quiz, user=request.user).order_by("created_at").last()

        if last_result:
            total_questions = questions + last_result.total_questions
            total_correct_answers = correct_answers + last_result.correct_answers
        else:
            total_questions = questions
            total_correct_answers = correct_answers

        Result.objects.create(
            quiz=quiz,
            user=request.user,
            questions=questions,
            correct_answers=correct_answers,
            current_average_value=total_correct_answers / total_questions,
            total_questions=total_questions,
            total_correct_answers=total_correct_answers
        )

        return Response("Quiz completed successfully", status=status.HTTP_200_OK)

    @action(detail=False, url_path='average-score', methods=['GET'])
    def average_score(self, request):
        user = request.user
        user_results = Result.objects.filter(user=user)
        average_score = calculate_average_score(user_results)
        return Response({"average_score": average_score}, status=status.HTTP_200_OK)

    @action(detail=False, url_path='user-export', methods=['GET'])
    def export_for_member(self, request):
        results = Result.objects.filter(user=request.user)
        serialized_data = [
            {
                'id': result.id,
                'user': str(result.user),
                'company': result.quiz.company.name,
                'quiz': str(result.quiz.title),
                'score': result.current_average_value,
                'date passed': result.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for result in results
        ]

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="quiz_results.csv"'

        writer = csv.DictWriter(response, fieldnames=['id', 'user', 'company', 'quiz', 'score', 'date passed'])
        writer.writeheader()
        writer.writerows(serialized_data)

        return response

