from rest_framework import serializers

from quiz_app.models import Quiz, Result

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('owner', 'members', 'admins')


class UserActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField


class QuizListSerializer(serializers.ModelSerializer):
    last_attempt = serializers.SerializerMethodField()

    def get_last_attempt(self, obj):
        last_result = Result.objects.filter(quiz=obj).order_by('-created_at').first()
        if last_result:
            return last_result.created_at
        else:
            return None

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'last_attempt')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('id', 'questions', 'correct_answers', 'current_average_value', 'total_questions', 'total_correct_answers')


class QuizResultsSerializer(serializers.ModelSerializer):
    results = ResultSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'results')
