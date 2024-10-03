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

  categories = [
    { name: 'IT', label: 'IT'},
    { name: 'DEVOPS', label: 'Dev Ops'},
    { name: 'SECURITY', label: 'Security'},
    { name: 'COMPLIANCE', label: 'Compliance'},
    { name: 'ESG', label: 'ESG'},
    { name: 'HR', label: 'HR'},
    { name: 'LEGAL', label: 'Legal'},
  ];

  constructor(http: HttpClient) {}

  async extractQuestions(): Promise<QuestionExtraction> {
    console.log('Extracting questions...');
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      questions: [
        {
          text: 'What is the capital of France?',
          sheetName: 'Sheet1',
          category: 'IT',
        },
        {
          text: 'What is the capital of Germany?',
          sheetName: 'Sheet1',
          category: 'DEVOPS',
        },
        {
          text: 'What is the capital of Italy?',
          sheetName: 'Sheet1',
          category: 'SECURITY',
        },
        {
          text: 'What is the capital of Spain?',
          sheetName: 'Sheet1',
          category: 'COMPLIANCE',
        },
      ],
    };
  }

  async askQuestion(question: Question): Promise<AnsweredQuestion> {
    console.log('Question asked: ', question);
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
    console.log('Question updated: ', question);
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}
