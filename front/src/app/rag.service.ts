import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AnsweredQuestion } from './answered-question';
import { Question } from './question';
import { read, writeFileXLSX, utils } from 'xlsx';
import { firstValueFrom, lastValueFrom, Observable, Subject } from 'rxjs';

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
    { name: 'GENERAL', label: 'General' },
    { name: 'IT', label: 'IT' },
    { name: 'DEVOPS', label: 'Dev Ops' },
    { name: 'SECURITY', label: 'Security' },
    { name: 'COMPLIANCE', label: 'Compliance' },
    { name: 'ESG', label: 'ESG' },
    { name: 'HR', label: 'HR' },
    { name: 'LEGAL', label: 'Legal' },
  ];

  readonly EXTRACT_QUESTION_API =
    'http://localhost:8000/api/v1/extract_questions';

  constructor(private http: HttpClient) {}

  extractQuestions(): Observable<Question[] | number> {
    console.log('Extracting questions...');
    const res = new Subject<Question[] | number>();
    const workbook = read(this.file as Blob, { type: 'array' });
    this.readFileAndExtractQuestions(res);
    return res.asObservable();
  }

  private async readFileAndExtractQuestions(
    subject: Subject<Question[] | number>
  ) {
    if (!this.file) {
      subject.error('No file selected');
      return;
    }
    const buffer = await this.file?.arrayBuffer();
    const workbook = read(buffer, { type: 'array' });

    let chunkCount = 0;
    let chunkCounter = 0;
    const chunkSize = 10;

    for (const sheetName of workbook.SheetNames) {
      const sheet = workbook.Sheets[sheetName];
      const sheetDataJson = utils.sheet_to_json(sheet);
      chunkCount += Math.ceil(sheetDataJson.length / chunkSize);
    }

    for (const sheetName of workbook.SheetNames) {
      const sheet = workbook.Sheets[sheetName];
      const sheetDataJson = utils
        .sheet_to_json(sheet)
        .map((row: any) =>
          Object.values(row).map((cell: any) => cell.toString())
        );

      for (let i = 0; i < sheetDataJson.length; i += chunkSize) {
        const chunk = sheetDataJson.slice(i, i + chunkSize);
        const data = {
          sheet_name: sheetName,
          lines: chunk as string[][],
        };
        console.log('Sending chunk to API: ', data);

        const answer = await this.callExtractQuestionAPI(data);
        chunkCounter++;
        subject.next(chunkCounter / chunkCount);
        subject.next(answer);
      }
    }
    subject.complete();
  }

  private async callExtractQuestionAPI(data: {
    sheet_name: string;
    lines: string[][];
  }): Promise<Question[]> {
    const answer = await lastValueFrom(
      this.http.post<{ questions: { question: string; category: string }[] }>(
        this.EXTRACT_QUESTION_API,
        data
      )
    );

    return answer.questions.map((question) => ({
      text: question.question,
      category: question.category,
      sheetName: data.sheet_name,
    }));
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
      confidence: Math.random(),
      references: ['Reference 1', 'Reference 2'],
    };
  }

  async updateQuestion(question: AnsweredQuestion) {
    console.log('Question updated: ', question);
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}
