import { Question } from './question';
import { QuestionState } from './question-state';

export interface AnsweredQuestion extends Question {
  answer: string;
  confidence: number;
  references: {
    question: string;
    answer: string;
    answerDate: Date;
    docId: string;
    similarity: number;
  }[];
  state: QuestionState;
}
