import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AnsweredQuestion } from './answered-question';
import { Question } from './question';
import { read, write, utils, WorkSheet } from 'xlsx';
import { firstValueFrom, lastValueFrom, Observable, Subject } from 'rxjs';
import { parse } from 'papaparse';

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

  readonly ASK_QUESTION_API = 'http://localhost:8000/api/v1/answers';

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
      const sheetDataJson = this.sheetToJson(sheet);
      chunkCount += Math.ceil(sheetDataJson.length / chunkSize);
    }

    for (const sheetName of workbook.SheetNames) {
      const sheet = workbook.Sheets[sheetName];
      const sheetDataJson = this.sheetToJson(sheet);

      for (let i = 0; i < sheetDataJson.length; i += chunkSize) {
        const chunk = sheetDataJson.slice(i, i + chunkSize);
        const data = {
          sheet_name: sheetName,
          lines: chunk as string[][],
        };
        console.log('Sending chunk to API: ', data);
        const answer = await this.callExtractQuestionAPI(i, data);
        console.log('Answer received: ', answer);
        chunkCounter++;
        subject.next(chunkCounter / chunkCount);
        subject.next(answer);
      }
    }
    subject.complete();
  }

  private sheetToJson(sheet: WorkSheet): string[][] {
    const sheetDataCsv = utils.sheet_to_csv(sheet);
    const sheetDataJson = parse(sheetDataCsv, { header: false })
      .data as string[][];
    // Remove empty rows in the end
    while (
      sheetDataJson[sheetDataJson.length - 1].every((cell) => cell === '')
    ) {
      sheetDataJson.pop();
    }
    return sheetDataJson;
  }

  private async callExtractQuestionAPI(
    firstRow: number,
    data: {
      sheet_name: string;
      lines: string[][];
    }
  ): Promise<Question[]> {
    const answer = await lastValueFrom(
      this.http.post<{
        questions: {
          question: string;
          category: string;
          position: {
            line: number;
            cell: number;
          };
        }[];
      }>(this.EXTRACT_QUESTION_API, data)
    );

    return answer.questions.map((question) => ({
      doc_id: this.file?.name,
      text: question.question,
      category: question.category,
      sheetName: data.sheet_name,
      position: {
        row: question.position.line + firstRow,
        column: question.position.cell,
      },
    }));
  }

  async askQuestion(question: Question): Promise<AnsweredQuestion> {
    console.log('Question asked: ', question);
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    // return {
    //   category: question.category,
    //   text: question.text,
    //   sheetName: question.sheetName,
    //   state: 'Human',
    //   answer: `Answer to ${question.text}`,
    //   confidence: Math.random(),
    //   references: ['Reference 1', 'Reference 2'],
    // };
    const answer = await lastValueFrom(
      this.http.post<{
        answer: string;
        confidence: number;
        used_data: {
          question: string;
          answer: string;
          doc_id: string;
          similarity: number;
        }[];
      }>(this.ASK_QUESTION_API, {
        question: question.text,
        category: question.category,
        products: [],
      })
    );
    return {
      answer: answer.answer,
      confidence: answer.confidence,
      references: answer.used_data.map((data) => ({
        question: data.question,
        answer: data.answer,
        docId: data.doc_id,
        similarity: data.similarity,
      })),
      position: question.position,
      category: question.category,
      text: question.text,
      sheetName: question.sheetName,
      state: 'Human',
    };
  }

  async updateQuestion(question: AnsweredQuestion) {
    console.log('Question updated: ', question);
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  async exportToExcel(questions: AnsweredQuestion[]) {
    if (!this.file) {
      console.error('No file selected');
      return;
    }
    const buffer = await this.file?.arrayBuffer();
    const workbook = read(buffer);

    for (const question of questions) {
      const sheet = workbook.Sheets[question.sheetName];
      const cellPosition = utils.encode_cell({
        r: question.position.row,
        c: question.position.column + 1,
      });
      let cell = sheet[cellPosition];
      if (!cell) {
        cell = { t: 's', v: '' };
        sheet[cellPosition] = cell;
      }
      cell.v = question.answer;
    }

    const bufferOut = write(workbook, { type: 'array', bookType: 'xlsx' });
    const blob = new Blob([bufferOut], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = this.file.name;
    a.click();
  }
}
