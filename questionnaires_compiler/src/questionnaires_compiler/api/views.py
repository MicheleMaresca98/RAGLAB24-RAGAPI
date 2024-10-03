import logging
from ast import literal_eval
from typing import List, Optional

from django.http import JsonResponse
from langchain_aws import ChatBedrock
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    renderer_classes
)
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request

from django_core.settings import vector_store, embeddings
from questionnaires_compiler.api.serializers.answer import (
    AnswersInputSerializer, AnswersOutputSerializer, ExtractQuestionInputSerializer)

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


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def extract_questions(
        request: Request, version: str = None
) -> JsonResponse:
    # in_serializer = ExtractQuestionInputSerializer(data=request.data)
    # in_serializer.is_valid(raise_exception=True)
    print(request.data)
    try:
        sheet_name: str = request.data['sheet_name']
        lines: List[List[str]] = request.data['lines']

        system_prompt = """
            You are a helpful assistant.
            Your mission is to extract question, answer from the given text.
            The given text is the content of a table (typically an excel sheet).
            
            Here is the process to follow:
            1: Try to identify if the text only contains instructions. If so, return only an empty list without extra text. 
            
            2: If the text contains questions, extract them and return them as a list of JSONs formatted as follow:
            {
                "question": "The question extracted from the text",
                "category": "could be [GENERAL, IT, HR, SECURITY, COMPLIANCE, ESG, LEGAL, FINANCE, OTHER]
            }
            Don't add extra text in the answer, just the list of JSONs is expected. 
        """

        prompt_template = PromptTemplate.from_template("""
                                                      Sheet name: {sheet_name}
                                                      {text}
                                                      """)
        text = "\n".join([", ".join(line) for line in lines])

        messages = [
            (
                "system",
                system_prompt,
            ),
            ("human", prompt_template.format(sheet_name=sheet_name, text=text)),
        ]

        llm = ChatBedrock(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs=dict(temperature=0, max_tokens=8096),
        )

        llm_answers = llm.invoke(messages)
        try:
            questions_list = literal_eval(llm_answers.content)
        except SyntaxError as e:
            log.error(f"Syntax error in LLM answer: {llm_answers.content}")
            return JsonResponse(
                data={"error": "Syntax error in LLM answer"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        cleaned_questions_list = []
        for d in questions_list:
            if "question" not in d or "category" not in d:
                continue
            cleaned_questions_list.append(d)

        return JsonResponse(data={"questions": cleaned_questions_list}, status=status.HTTP_200_OK)
    except Exception as e:
        response = {"error": str(e)}
    return JsonResponse(data=response, status=status.HTTP_400_BAD_REQUEST)

