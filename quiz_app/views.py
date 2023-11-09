from django.contrib.auth.backends import UserModel
from django.core.cache import cache
from django.db.models import Max, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from company.models import Company
from company.serializers import ResultSerializer
from quiz_app.models import Question, Quiz, Result
from quiz_app.permissions import IsCompanyAdminOrOwner
from quiz_app.serializers import QuestionSerializer, QuizCreateSerializer
from services.utils.average_value import calculate_average_score
from services.utils.export_data import generate_csv_response


class QuizManagementViewSet(viewsets.ModelViewSet):
    serializer_class = QuizCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdminOrOwner]
    queryset = Quiz.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'complete_quiz', 'average_score', 'global_rating', 'user-quiz-results']:
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
        response = generate_csv_response(results, "quiz_results.csv",
                                         ['id', 'user', 'company', 'quiz', 'score', 'date_passed'])
        return response

    @action(detail=False, url_path='global-rating', methods=['GET'])
    def global_rating(self, request):
        all_results = Result.objects.all()
        total_questions = 0
        total_correct = 0

        for result in all_results:
            total_questions += result.questions
            total_correct += result.correct_answers

        global_rating = 0.0
        if total_questions > 0:
            global_rating = total_correct / total_questions

        return Response({'global_rating': global_rating})

    @action(detail=True, url_path='user-quiz-results', methods=['GET'])
    def user_quiz_results(self, request, pk=None):
        user = get_object_or_404(UserModel, pk=pk)

        results = Result.objects.filter(user=user)

        serialized_results = ResultSerializer(results, many=True).data

        response_data = {
            'id': user.id,
            'results': serialized_results
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='all-users-quiz-results', methods=['GET'])
    def all_users_quiz_results(self, request):
        all_users = UserModel.objects.all()

        results = Result.objects.select_related('user').filter(user__in=all_users)

        user_results_mapping = {}
        for result in results:
            if result.user.id not in user_results_mapping:
                user_results_mapping[result.user.id] = {
                    'id': result.user.id,
                    'results': []
                }
            serialized_result = ResultSerializer(result).data
            user_results_mapping[result.user.id]['results'].append(serialized_result)

        all_user_results = list(user_results_mapping.values())

        return Response(all_user_results, status=status.HTTP_200_OK)

    @action(detail=True, url_path='company-users-last-results', methods=['GET'])
    def company_users_last_results(self, request, pk=None):
        company = get_object_or_404(Company, pk=pk)

        last_results = Result.objects.filter(quiz__company=company).values('user').annotate(
            last_result_date=Max('created_at'))

        user_last_results = []
        for result in last_results:
            user_id = result['user']
            last_result_date = result['last_result_date']

            user_last_results.append({
                'id': user_id,
                'last_result_date': last_result_date
            })

        return Response(user_last_results, status=status.HTTP_200_OK)
