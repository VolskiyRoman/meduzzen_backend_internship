from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from quiz_app.models import Quiz
from quiz_app.permissions import IsCompanyAdminOrOwner
from quiz_app.serializers import QuizCreateSerializer, QuestionSerializer


class QuizManagementViewSet(viewsets.ModelViewSet):
    serializer_class = QuizCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdminOrOwner]
    queryset = Quiz.objects.all()

    def get_permissions(self):
        if self.action in [
            'list',
            'retrieve'
        ]:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsCompanyAdminOrOwner()]

    def get_queryset(self):
        return Quiz.objects.filter(company__members=self.request.user)

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
