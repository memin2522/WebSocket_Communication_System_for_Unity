"""API REST (mecanismo de consulta periódica previo a los WebSockets).

Se conserva el comportamiento original sin cambios, incluida la condición
de POST /question (ver docs/comportamientos-conocidos.md).
"""
from dataclasses import dataclass
from typing import Optional

from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .schemas import QuestionSchema, AnswerSchema

blp = Blueprint("Main", __name__)


@dataclass
class RestState:
    question: Optional[dict] = None
    answer: Optional[str] = None


def _state() -> RestState:
    return current_app.extensions["rest_state"]


@blp.route("/")
class MainOperations(MethodView):
    def get(self):
        title = current_app.config["API_TITLE"]
        return (
            f"<h1>This is the main page of the {title} api. "
            "If you see this everything is working correctly</h1>"
        )


@blp.route("/question")
class QuestionOperations(MethodView):

    @blp.arguments(QuestionSchema)
    @blp.response(201, QuestionSchema)
    def post(self, question_data):
        state = _state()
        # Condición original conservada: solo guarda si ya hay una pregunta.
        if state.question is not None:
            state.question = question_data
            return state.question
        abort(400, message="There is already a question being procesed")

    @blp.response(201, QuestionSchema)
    def get(self):
        state = _state()
        if state.question is not None:
            response = state.question
            state.question = None
            return response
        abort(400, message="There is no question to return")


@blp.route("/answer")
class AnswerOperations(MethodView):

    @blp.arguments(AnswerSchema)
    @blp.response(201, AnswerSchema)
    def post(self, answer_data):
        state = _state()
        state.answer = answer_data["answer"]
        return {"answer": state.answer}

    @blp.response(200, AnswerSchema)
    def get(self):
        state = _state()
        if state.answer:
            out = {"answer": state.answer}
            state.answer = None
            return out
        abort(400, message="There is no answer to return")


@blp.route("/health")
def health():
    return "OK", 200
