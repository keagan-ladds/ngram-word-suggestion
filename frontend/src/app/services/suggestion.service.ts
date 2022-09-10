import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SuggestionResponse } from '../models/suggestion_response';

@Injectable({
  providedIn: 'root'
})
export class SuggestionService {

  constructor(private http: HttpClient) { }

  getSuggestions(text: string): Observable<SuggestionResponse> {
    return this.http.post<SuggestionResponse>('http://127.0.0.1:5000/api/v1/suggest', {
      text: text
    });
  }
}
