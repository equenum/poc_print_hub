import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { provideToastr, ToastNoAnimation } from 'ngx-toastr'; 

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes),
    provideHttpClient(withFetch()),
    provideToastr({
      toastComponent: ToastNoAnimation,
      timeOut: 3000,
      positionClass: 'toast-top-right',
      preventDuplicates: true,
      maxOpened: 1
    })
  ]
};
