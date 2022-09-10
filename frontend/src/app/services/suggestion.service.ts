import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { SuggestionResponse } from '../models/suggestion_response';

@Injectable({
  providedIn: 'root'
})
export class SuggestionService {

  constructor(private http: HttpClient) { }

  getSuggestions(text: string): Observable<SuggestionResponse> {
    return this.http.post<SuggestionResponse>(environment.api_url + 'api/v1/suggest', {
      text: text
    });
  }
}
