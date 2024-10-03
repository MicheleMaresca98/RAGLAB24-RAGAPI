import { Routes } from '@angular/router';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { EditorComponent } from './editor/editor.component';

export const routes: Routes = [
  // Default route to the FileUploadComponent
  {
    path: '',
    pathMatch: 'full',
    component: FileUploadComponent,
  },
  // /editor route to EditorComponent
  {
    path: 'editor',
    component: EditorComponent,
  },
];
