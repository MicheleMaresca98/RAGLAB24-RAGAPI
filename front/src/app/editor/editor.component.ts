import { Component, OnInit } from '@angular/core';
import { RagService } from '../rag.service';
import { AnsweredQuestion } from '../answered-question';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './editor.component.html',
  styleUrl: './editor.component.scss',
})
export class EditorComponent implements OnInit {
  questions: AnsweredQuestion[] = [];

  questionIndex = 0;

  constructor(private ragService: RagService) {}

  ngOnInit(): void {
    this.loadQuestions();
  }

  async loadQuestions() {
    const extractedQuestions = await this.ragService.extractQuestions();
    this.questions = extractedQuestions.questions.map((question) => ({
      text: question.text,
      sheetName: question.sheetName,
      category: question.category,
      answer: '',
      state: 'Waiting',
    }));

    this.questionIndex = 0;
    for (const [index, question] of this.questions.entries()) {
      const answeredQuestion = await this.ragService.askQuestion(question);
      this.questions[index] = answeredQuestion;
      console.log('Question answered: ', answeredQuestion);
    }
  }

  get currentQuestion(): AnsweredQuestion | undefined {
    return this.questions[this.questionIndex];
  }

  questionStateClass(question: AnsweredQuestion) {
    let questionClasses = [];
    switch (question.state) {
      case 'Human':
        questionClasses = ['fa-user'];
        break;
      case 'Accepted':
        questionClasses = ['fa-check'];
        break;
      case 'Rejected':
        questionClasses = ['fa-times'];
        break;
      case 'Edited':
        questionClasses = ['fa-edit'];
        break;
      case 'Waiting':
        questionClasses = ['fa-spinner', 'fa-spin', 'question-color-loading'];
        break;
    }
    return {
      fa: true,
      ...questionClasses.reduce((acc, c) => ({ ...acc, [c]: true }), {}),
    };
  }

  selectQuestion(index: number) {
    this.questionIndex = index;
  }

  nextQuestion() {
    this.questionIndex++;
    if (this.questionIndex >= this.questions.length) {
      this.questionIndex = 0;
    }
  }

  previousQuestion() {
    this.questionIndex--;
    if (this.questionIndex < 0) {
      this.questionIndex = this.questions.length - 1;
    }
  }

  updateCurrentQuestion() {
    this.ragService.updateQuestion(this.currentQuestion!);
  }
}
