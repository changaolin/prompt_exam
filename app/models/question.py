from .. import db
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class Option:
    label: str
    content: str

class QuestionBank(db.Model):
    __tablename__ = 'question_banks'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='bank', lazy=True)

    def add_question(self, question):
        self.questions.append(question)

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('question_banks.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False)
    question = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    answer = db.Column(db.String(100))
    answer_points = db.Column(db.JSON)
    options = db.relationship('Option', backref='question', lazy=True)

    def __init__(self, number, question, type, options=None, answer='', answer_points=None):
        self.number = number
        self.question = question
        self.type = type
        self.answer = answer
        self.answer_points = answer_points or []
        if options:
            for opt in options:
                if isinstance(opt, dict):
                    self.options.append(Option(**opt))
                else:
                    self.options.append(opt)

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'question': self.question,
            'type': self.type,
            'options': [opt.to_dict() for opt in self.options],
            'answer': self.answer,
            'answer_points': self.answer_points if self.type == 'essay' else None
        }

class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    label = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __init__(self, label, content):
        self.label = label
        self.content = content

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'content': self.content
        }