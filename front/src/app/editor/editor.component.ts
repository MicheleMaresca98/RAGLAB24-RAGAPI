import { RagService } from '../rag.service';
import { AnsweredQuestion } from '../answered-question';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Component, ElementRef, ViewChild, OnInit } from '@angular/core';

@Component({
  selector: 'app-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './editor.component.html',
  styleUrl: './editor.component.scss',
})
export class EditorComponent implements OnInit {
  @ViewChild('currentAnswer', { read: ElementRef })
  currentAnswer!: ElementRef<HTMLTextAreaElement>;

  questions: AnsweredQuestion[] = [];

  questionIndex = 0;

  readonly categories: { name: string; label: string }[];

  constructor(private ragService: RagService) {
    this.categories = this.ragService.categories;
  }

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
      if (index === 0) {
        this.selectCurrentAnswerText();
      }
      console.log('Question answered: ', answeredQuestion);
    }
  }

  get currentQuestion(): AnsweredQuestion | undefined {
    return this.questions[this.questionIndex];
  }

  categoryLabel(category: string) {
    return this.categories.find((c) => c.name === category)?.label;
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

  questionStateText(question: AnsweredQuestion) {
    switch (question.state) {
      case 'Human':
        return 'Needs review';
      case 'Accepted':
        return 'Accepted';
      case 'Rejected':
        return 'Rejected';
      case 'Edited':
        return 'Edited';
      case 'Waiting':
        return 'Waiting';
    }
  }

  selectQuestion(index: number) {
    this.questionIndex = index;
  }

  nextQuestion() {
    this.questionIndex++;
    if (this.questionIndex >= this.questions.length) {
      this.questionIndex = 0;
    }
    this.selectCurrentAnswerText();
  }

  previousQuestion() {
    this.questionIndex--;
    if (this.questionIndex < 0) {
      this.questionIndex = this.questions.length - 1;
    }
    this.selectCurrentAnswerText();
  }

  onShiftEnter(event: Event) {
    event.preventDefault();
    event.stopPropagation();
    this.updateCurrentQuestion();
  }

  async updateCurrentQuestion() {
    if (!this.currentQuestion) {
      return;
    }
    const question = this.currentQuestion;
    this.nextQuestion();
    question.state = 'Waiting';
    await this.ragService.updateQuestion({
      ...question,
      state: 'Accepted',
    });
    question.state = 'Accepted';
  }

  private selectCurrentAnswerText() {
    setTimeout(() => {
      this.currentAnswer.nativeElement.focus();
      this.currentAnswer.nativeElement.select();
    }, 0);
  }
}
