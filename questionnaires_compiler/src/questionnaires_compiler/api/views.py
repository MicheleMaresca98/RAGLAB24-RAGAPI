import logging
from typing import List, Optional

from django.http import JsonResponse
from langchain_core.documents import Document
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    renderer_classes
)
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request

from django_core.settings import vector_store, embeddings
from questionnaires_compiler.api.serializers.answer import (
    AnswersInputSerializer, AnswersOutputSerializer)


log = logging.getLogger(__name__)


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def answers(
    request: Request, version: str = None
) -> JsonResponse:
    in_serializer = AnswersInputSerializer(data=request.data)
    in_serializer.is_valid(raise_exception=True)
    try:
        question: str = in_serializer.data['question']
        category: str = in_serializer.data['category']
        products: Optional[List[str]] = in_serializer.data.get('products', None)

        _and = [
            {"category": {"$eq": category}},
        ]
        if products:
            _and.append({"products": {"$eq": products}})

        pre_filter = {
            "$and": _and
        }
        found_docs = vector_store.similarity_search(
            query=question,
            k=5,
            pre_filter=pre_filter
        )
        confidence = perform_confidence()
        response = {
            "answer": found_docs[0]['answer'],
            "doc_ids": [doc.metadata['doc_id'] for doc in found_docs],
            "confidence": confidence
        }
        # out_serializer = AnswersOutputSerializer(
        #     data=response)
        # out_serializer.is_valid(raise_exception=True)
        # response_data = out_serializer.data
        response_data = response
        return JsonResponse(
            data=response_data, status=status.HTTP_200_OK)
    except Exception as e:
        response = {"error": str(e)}
    return JsonResponse(data=response, status=status.HTTP_400_BAD_REQUEST)


def perform_confidence(found_docs: List[Document]) -> str:
    response = 'LOW'

    response = 'MEDIUM'

    response = 'HIGH'
    return response