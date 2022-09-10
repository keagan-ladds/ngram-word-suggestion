import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { AutocompleteDirective } from './directives/autocomplete.directive';
import { AutocompleteListComponent } from './components/autocomplete-list/autocomplete-list.component';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [
    AppComponent,
    AutocompleteDirective,
    AutocompleteListComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent],
  exports: [
  ]
})
export class AppModule { }
