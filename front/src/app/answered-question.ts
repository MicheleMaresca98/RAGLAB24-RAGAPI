import { Question } from './question';
import { QuestionState } from './question-state';

export interface AnsweredQuestion extends Question {
  answer: string;
  state: QuestionState;
}
