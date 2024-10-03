import { Component, ElementRef, ViewChild } from '@angular/core';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, NgbDropdownModule],
  templateUrl: './file-upload.component.html',
  styleUrl: './file-upload.component.scss',
})
export class FileUploadComponent {
  products = [
    { id: 'ESAW', label: 'eSignAnywhere' },
    { id: 'STRONGDOX', label: 'Strongdox' },
    { id: 'SAFEDOX', label: 'SafeDox' },
    { id: 'OT', label: 'Onboarding Today' },
  ];

  @ViewChild('fileInput', { read: ElementRef })
  fileInput!: ElementRef<HTMLInputElement>;

  dragover = false;

  file?: File;

  // dropZone click event handler
  dropZoneClick() {
    this.fileInput.nativeElement.click();
  }

  onDragOver(event: Event) {
    event.preventDefault();
    event.stopPropagation();
    this.dragover = true;
  }

  onDragLeave(event: Event) {
    event.preventDefault();
    event.stopPropagation();
    this.dragover = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.dragover = false;
    this.file = event.dataTransfer?.files[0];
    console.log('file: ', this.file);
  }

  onFileChange(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    this.file = files?.item(0) || undefined;
    console.log('file: ', this.file);
  }

  onRemoveFile() {
    this.file = undefined;
  }
}
