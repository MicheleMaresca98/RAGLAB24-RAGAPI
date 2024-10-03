import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AnsweredQuestion } from './answered-question';
import { Question } from './question';

interface QuestionExtraction {
  questions: Question[];
}

@Injectable({
  providedIn: 'root',
})
export class RagService {
  file: File | undefined;
  selectedProducts: string[] = [];

  constructor(http: HttpClient) {}

  async extractQuestions(): Promise<QuestionExtraction> {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      questions: [
        {
          text: 'What is the capital of France?',
          sheetName: 'Sheet1',
          category: 'Geography',
        },
        {
          text: 'What is the capital of Germany?',
          sheetName: 'Sheet1',
          category: 'Geography',
        },
        {
          text: 'What is the capital of Italy?',
          sheetName: 'Sheet1',
          category: 'Geography',
        },
        {
          text: 'What is the capital of Spain?',
          sheetName: 'Sheet1',
          category: 'Geography',
        },
      ],
    };
  }

  async askQuestion(question: Question): Promise<AnsweredQuestion> {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      category: question.category,
      text: question.text,
      sheetName: question.sheetName,
      state: 'Human',
      answer: `Answer to ${question.text}`,
    };
  }

  async updateQuestion(question: AnsweredQuestion) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}
