from rest_framework import serializers


class PageRequest(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1)
    maxItemsPerPage = serializers.IntegerField(required=False, default=10)


class PageResponse(serializers.Serializer):
    page = serializers.IntegerField(required=True)
    maxItemsPerPage = serializers.IntegerField(required=True)
    totalPages = serializers.IntegerField(required=True)
    totalItems = serializers.IntegerField(required=True)
