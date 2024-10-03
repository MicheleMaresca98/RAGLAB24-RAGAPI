from rest_framework import serializers

from questionnaires_compiler.core.schemas import QuestionCategory


class AnswersInputSerializer(serializers.Serializer):
    question = serializers.CharField()
    category = serializers.CharField()
    products = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        default=list,
    )


class ExtractQuestionInputSerializer(serializers.Serializer):
    sheet_name = serializers.CharField()
    lines = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
        ),
        allow_empty=False,
    )


class ResponseItemSerializer(serializers.Serializer):
    text_field = serializers.CharField()
    number_field = serializers.DecimalField(max_digits=10, decimal_places=6)


class AnswersOutputSerializer(serializers.Serializer):
    answer = serializers.CharField()
    doc_ids = serializers.ListField(
        child=ResponseItemSerializer()
    )
    confidence = serializers.CharField()
