import { RagService } from '../rag.service';
import { AnsweredQuestion } from '../answered-question';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Component, ElementRef, ViewChild, OnInit } from '@angular/core';
import { lastValueFrom, tap } from 'rxjs';
import { QuestionState } from '../question-state';
import { Router } from '@angular/router';

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

  progress = 0;

  constructor(private ragService: RagService, private router: Router) {
    this.categories = this.ragService.categories;
    if (!ragService.file) {
      this.router.navigate(['/']);
    }
  }

  ngOnInit(): void {
    this.loadQuestions();
  }

  async loadQuestions() {
    this.questionIndex = 0;

    await lastValueFrom(
      this.ragService.extractQuestions().pipe(
        tap((res) => {
          if (typeof res === 'number') {
            console.log('progress: ', res);
            this.progress = res;
          } else {
            const extractedQuestions = res.map((question) => ({
              text: question.text,
              sheetName: question.sheetName,
              category: question.category,
              answer: '',
              state: 'Waiting' as QuestionState,
              confidence: 0,
              references: [],
            }));
            this.questions.push(...extractedQuestions);
          }
        })
      )
    );

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

  confidenceLabel(confidence: number) {
    if (confidence < 0.5) {
      return 'Low';
    }
    if (confidence < 0.8) {
      return 'Medium';
    }
    return 'High';
  }

  confidenceColor(confidence: number) {
    const red = 0;
    const green = 90;

    const interpolate = (start: number, end: number, factor: number) => {
      return start + (end - start) * factor;
    };

    const factor = confidence; // Assuming confidence is between 0 and 1

    const hue = Math.round(interpolate(red, green, factor));

    return `hsl(${hue} 80% 40%)`;
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
