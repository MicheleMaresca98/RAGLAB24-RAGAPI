import logging
from ast import literal_eval
from typing import List, Optional, Dict

from bson import ObjectId
from click import prompt
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

from django_core.settings import vector_store, embeddings, MONGODB_COLLECTION
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
            pre_filter=pre_filter,
            include_scores=True
        )
        relevant_docs = apply_threshold_and_format_docs(found_docs=found_docs)
        system_prompt = '''
            You are a helpful assistant.
            Your mission is to answer to questions.
            To reply to the a question you only use the information that are provided in the text.

            Here is the process to follow to answer to a question :
            1: Carefully analyse the information that are provided.

            2: If the information that are provided allow you to answer the reply with a JSON formatted as follow :
            {
                "answer": "The answer to the question"
                "confidence": "A confidence score between 1 and 10 that estimate how confident are you for this answer"
            }
            If the information provided does not contain the answer to the asked question reply:
            {
                "answer": "NO-ANSWER"
                "confidence": "0"
            }

            Try to have concise, useful and precise answers;
            In any case don't add extra text in the answer, just a JSONs is expected.
        '''

        prompt_template = '''
            Can you please provide an answer to this question: {{  question  }}

            Use only this information :
            {% for item in relevant_docs %}
            {
                "question": "{{ item.question }}",
                "answer": "{{ item.answer  }}"
            }
            {% endfor %}
        '''
        prompt_template = PromptTemplate(
            template=prompt_template,
            template_format='jinja2',
            input_variables=['question', 'relevant_docs']
        )
        human_prompt = prompt_template.format(question=question, relevant_docs=relevant_docs)

        llm = ChatBedrock(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs=dict(temperature=0, max_tokens=8096),
        )
        messages = [
            (
                "system",
                system_prompt,
            ),
            (
                "human", human_prompt,
            )
        ]
        llm_answers = llm.invoke(messages)

        try:
            answer = literal_eval(llm_answers.content)
            response = {
                "answer": answer["answer"],
                "confidence": answer["confidence"],
                "used_data": relevant_docs
            }
            return JsonResponse(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {"error": str(e)}
            return JsonResponse(data=response,status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        response = {"error": str(e)}
    return JsonResponse(data=response, status=status.HTTP_400_BAD_REQUEST)


def apply_threshold_and_format_docs(
    found_docs: List[Document], threshold: float = 0.8
) -> List[Dict]:
    relevant_docs = []
    for doc in found_docs:
        if doc.metadata['score'] > threshold:
            question = MONGODB_COLLECTION.find_one(
                {"_id": ObjectId(doc.metadata['_id'])}
            )
            relevant_doc = {
                "question": question['question'],
                "answer": doc.metadata['answer'],
                "doc_id": doc.metadata['doc_id']
            }
            relevant_docs.append(relevant_doc)
    return relevant_docs


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

            for line_index, line in enumerate(lines):
                for cell_index, cell in enumerate(line):
                    if d["question"] in cell:
                        d["position"] = {"line": line_index, "cell": cell_index}
                        break
                if "position" in d:
                    break

            if "position" not in d:
                d["position"] = {"line": -1, "cell": -1}

            cleaned_questions_list.append(d)

        return JsonResponse(data={"questions": cleaned_questions_list}, status=status.HTTP_200_OK)
    except Exception as e:
        response = {"error": str(e)}
    return JsonResponse(data=response, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def update_answer(
        request: Request, version: str = None
) -> JsonResponse:
    # in_serializer = ExtractQuestionInputSerializer(data=request.data)
    # in_serializer.is_valid(raise_exception=True)
    print(request.data)
    try:
        doc_id: str = request.data['doc_id']
        question: str = request.data['question']
        category: str = request.data['category']
        answer: str = request.data['answer']
        action: str = request.data['action']


        status = "Pending"
        if action == "accept":
            status = "Accepted"
        if action == "acceptPermanent":
            status = "Accepted"
        elif action == "approve":
            status = "Approved"
        elif action == "reject":
            status = "Rejected"
        
        MONGODB_COLLECTION.update_one(
            {"doc_id": doc_id, "question": question},
            {"$set": {"answer": answer, 
                      "status": status, 
                      "category": category,
                      "accept_permanent": action == "acceptPermanent",
                      "answer_date" : datetime.datetime.now()}}
        )

        return JsonResponse(status=status.HTTP_200_OK)
    except Exception as e:
        response = {"error": str(e)}
    return JsonResponse(data=response, status=status.HTTP_400_BAD_REQUEST)

