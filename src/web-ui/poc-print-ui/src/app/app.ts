import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

// extract
interface SelectOption {
  value: string;
  displayName: string;
}

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.html'
})
export class App {
  protected readonly title = signal('poc-print-ui');

  readonly bodyTypeOptions: SelectOption[] = [
    { value: 'text', displayName: 'Text' },
    { value: 'keyvalue', displayName: 'Key-Value' }
  ];

  readonly feedSelectorTypeOptions: SelectOption[] = [
    { value: 'slider', displayName: 'Slider' },
    { value: 'custom', displayName: 'Custom' }
  ];

  selectedBodyType = signal<string>('text');
  selectedFeedSelectorType = signal<string>('slider');
  selectedFeedTimes = signal<number>(5);
  
  getBodyTypePlaceholder(): string {
    switch (this.selectedBodyType()) {
      case 'text':
        return 'Enter message text';
      case 'keyvalue':
        return 'Enter JSON message, e.g., { "key": "value" }';
      default:
        return 'Enter message text';
    }
  }
}