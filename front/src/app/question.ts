export interface Question {
  text: string;
  sheetName: string;
  category: string;
  position: {
    row: number;
    column: number;
  }
}
