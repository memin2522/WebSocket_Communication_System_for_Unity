from marshmallow import Schema, fields


class QuestionSchema(Schema):
    question = fields.Str(required=True)


class AnswerSchema(Schema):
    answer = fields.Str(required=True)
