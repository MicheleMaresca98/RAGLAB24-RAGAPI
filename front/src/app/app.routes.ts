import { Routes } from '@angular/router';
import { FileUploadComponent } from './file-upload/file-upload.component';

export const routes: Routes = [
    // Default route to the FileUploadComponent
    {
        path: '',
        pathMatch: 'full',
        component: FileUploadComponent
    }
];
