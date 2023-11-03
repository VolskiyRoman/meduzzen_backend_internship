from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Quiz, Result
from quiz_app.permissions import IsCompanyAdminOrOwner
from quiz_app.serializers import QuestionSerializer, QuizCreateSerializer


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

        total_questions = quiz.questions.count()
        correct_answers = 0

        for i in user_input:
            question_id = i.get('question')
            answers = i.get('answers')
            question = quiz.questions.filter(id=question_id).first()

            if question:
                correct_answer_ids = question.answers.filter(is_correct=True).values_list('id', flat=True)
                if set(answers) == set(correct_answer_ids):
                    correct_answers += 1

        Result.objects.create(
            quiz=quiz,
            user=request.user,
            questions=total_questions,
            correct_answers=correct_answers
        )

        return Response("Quiz completed successfully", status=status.HTTP_200_OK)

    @action(detail=False, url_path='average-score', methods=['GET'])
    def average_score(self, request):
        user = request.user
        user_results = Result.objects.filter(user=user)

        total_questions = user_results.aggregate(total_questions=Sum('questions')).get('total_questions') or 0
        total_correct_answers = user_results.aggregate(total_correct=Sum('correct_answers')).get('total_correct') or 0

        if total_questions > 0:
            average_score = (total_correct_answers / total_questions) * 100
        else:
            average_score = 0

        return Response({"average_score": round(average_score, 2)}, status=status.HTTP_200_OK)

