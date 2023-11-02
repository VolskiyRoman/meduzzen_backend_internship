from rest_framework import serializers

from quiz_app.models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct']

    def validate(self, data):
        return data


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['question_text', 'answers']

    def validate(self, data):
        if 'answers' not in data or len(data['answers']) < 2:
            raise serializers.ValidationError("There should be at least 2 answers for each question.")

        correct_answers = [answer for answer in data['answers'] if answer['is_correct']]
        if len(correct_answers) < 1:
            raise serializers.ValidationError("There must be at least 1 correct answer for each question.")
        return data

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'company', 'title', 'description', 'questions', 'frequency']

    def validate(self, data):
        questions = data.get('questions', [])
        if len(questions) < 2:
            raise serializers.ValidationError("There must be at least 2 questions for the quiz.")
        return data

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop('answers')
            question = Question.objects.create(quiz=quiz, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return quiz

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.frequency = validated_data.get('frequency', instance.frequency)
        instance.save()

        return instance
