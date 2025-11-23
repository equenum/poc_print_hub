import { Inject, Injectable } from '@angular/core';
import { EnvConfig } from '../interfaces';
import { WINDOW } from '../injection.tokens';

@Injectable({
  providedIn: 'root',
})
export class EnvService {
  private config: EnvConfig;

  constructor(@Inject(WINDOW) private window: Window) {
    if ((this.window as any)["env"]) {
      this.config = (this.window as any)["env"];
    } else {
      this.config = {} as EnvConfig;
    }
  }

  get isProduction(): boolean {
    return this.config.isProduction;
  }

  get apiUrl(): string {
    return this.config.apiUrl;
  }
}
