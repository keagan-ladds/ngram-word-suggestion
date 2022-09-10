import { DOCUMENT } from '@angular/common';
import { ComponentFactoryResolver, Directive, ElementRef, Inject, OnChanges, Renderer2, SimpleChanges, ViewContainerRef } from '@angular/core';
import { Observable } from 'rxjs';
import { getCaretPosition, getValue, insertValue } from '../autocomplete-utils';
import { AutocompleteListComponent } from '../components/autocomplete-list/autocomplete-list.component';
import { WordReplacement, WordSuggestion } from '../models/suggestion_response';
import { SuggestionService } from '../services/suggestion.service';


const KEY_BACKSPACE = 8;
const KEY_TAB = 9;
const KEY_ENTER = 13;
const KEY_SHIFT = 16;
const KEY_ESCAPE = 27;
const KEY_SPACE = 32;
const KEY_LEFT = 37;
const KEY_UP = 38;
const KEY_RIGHT = 39;
const KEY_DOWN = 40;
const KEY_BUFFERED = 229;

@Directive({
  selector: '[autocomplete]',
  host: {
    '(keydown)': 'keyHandler($event)',
    '(input)': 'inputHandler($event)',
    '(click)': 'keyHandler($event)',
    '(blur)': 'blurHandler($event)',
    'autocomplete': 'off'
  }
})
export class AutocompleteDirective implements OnChanges {

  private readonly AutocompleteElementId = 'autocomplete-span'
  private lastKeyCode!: number;
  private iframe: any; // optional
  private startPos: number;
  private previousStartPos: number;

  private autocompleteList: AutocompleteListComponent;

  private autocompleteElement: HTMLElement;

  private searchPhrase: string;
  private autocompleteOpen: boolean;
  private suggestions: WordSuggestion[];
  private replacements: WordReplacement[];

  private currentSuggestionIndex: number;

  constructor(private _element: ElementRef,
    private _componentResolver: ComponentFactoryResolver,
    private _viewContainerRef: ViewContainerRef,
    private renderer: Renderer2,
    private suggestionService: SuggestionService,
    @Inject(DOCUMENT) private document: Document) { }

  ngOnChanges(changes: SimpleChanges): void {

  }

  blurHandler(event: any) {
  }

  inputHandler(event: any, nativeElement: HTMLInputElement = this._element.nativeElement) {
    //this.keyHandler(event, nativeElement);
  }

  // @param nativeElement is the alternative text element in an iframe scenario
  keyHandler(event: any, nativeElement: HTMLInputElement = this._element.nativeElement) {
    this.lastKeyCode = event.keyCode;

    if (event.isComposing || event.keyCode === KEY_BUFFERED) {
      return;
    }

    // get current text of the input
    const value = nativeElement.innerText;
    // save selection start and end position
    const start = nativeElement.selectionStart;
    const end = nativeElement.selectionEnd;

    let val: string = getValue(nativeElement) ?? '';
    let pos = getCaretPosition(nativeElement, this.iframe);
    let charPressed = event.key;
    if (!charPressed) {
      let charCode = event.which || event.keyCode;
      if (!event.shiftKey && (charCode >= 65 && charCode <= 90)) {
        charPressed = String.fromCharCode(charCode + 32);
      }
      // else if (event.shiftKey && charCode === KEY_2) {
      //   charPressed = this.config.triggerChar;
      // }
      else {
        // TODO (dmacfarlane) fix this for non-alpha keys
        // http://stackoverflow.com/questions/2220196/how-to-decode-character-pressed-from-jquerys-keydowns-event-handler?lq=1
        charPressed = String.fromCharCode(event.which || event.keyCode);
      }
    }

    console.log(event);


    if (event.keyCode == KEY_SPACE && !this.autocompleteOpen) {
      this.startPos = pos;
      this.searchPhrase = val.substr(0, pos).trim();
      this.autocompleteOpen = true;
      this.suggestionService.getSuggestions(this.searchPhrase).subscribe(response => {
        if (response && response.next_words.length > 0) {
          this.suggestions = response.next_words;
          this.replacements = response.replacements;
          this.currentSuggestionIndex = 0;

          const currentSuggestion = this.suggestions[0].token;

          this.updateAutocompleteText(nativeElement, currentSuggestion)
          this.showSearchList(nativeElement);
          this.updateAutocompleteList(this.suggestions);
        }
      })
    }
    else if (this.autocompleteOpen) {
      if (pos < this.startPos) {
        this.stopAutocomplete(nativeElement);
      }
      else if (event.keyCode == KEY_SPACE) {
        this.previousStartPos = this.startPos;
        this.stopAutocomplete(nativeElement);
        this.keyHandler(event, nativeElement);
      } else if (event.isClick == true) {
        this.stopAutocomplete(nativeElement);
      }
      else if (this.autocompleteList?.hidden) {
        if (event.keyCode == KEY_TAB && this.currentSuggestionIndex != -1) {
          this.stopEvent(event);
          const selectedValue = this.suggestions[this.currentSuggestionIndex].token;
          if (this.replacements.length > 0)
          {
            const text = this.replacements[0].replacement + ' ' + selectedValue;
            insertValue(nativeElement, this.previousStartPos + 1, pos, text, this.iframe);
          }
          else
          {
            insertValue(nativeElement, this.startPos + 1, pos, selectedValue, this.iframe);
          }

          this.stopAutocomplete(nativeElement);
          return;
        }
      }
      else if (!this.autocompleteList?.hidden) {

        if (event.keyCode == KEY_ENTER || event.keyCode == KEY_TAB) {
          this.stopEvent(event);
          console.log('event.KeyCode: ', event.keyCode);
          const selectedItem = this.autocompleteList.activeItem;
          if (this.replacements.length > 0)
          {
            const text = this.replacements[0].replacement + ' ' + selectedItem.token;
            insertValue(nativeElement, this.previousStartPos + 1, pos, text, this.iframe);
          }
          else
          {
            insertValue(nativeElement, this.startPos + 1, pos, selectedItem.token, this.iframe);
          }
          
          this.stopAutocomplete(nativeElement);
        }
        else if (event.keyCode == KEY_UP) {
          this.stopEvent(event);
          this.autocompleteList.activatePreviousItem();
        }
        else if (event.keyCode == KEY_DOWN) {
          this.stopEvent(event);
          this.autocompleteList.activateNextItem();
        }
      }
    }

    if (this.autocompleteOpen) {
      const textBeforeCursor = val.substring(0, pos) + (charPressed.length == 1 ? charPressed : '');

      const tokens = textBeforeCursor.trim().split(/\s+/);
      console.log('Tokens: ', tokens);
      console.log(textBeforeCursor);
      if (tokens.length != 0 && this.suggestions && this.currentSuggestionIndex != -1) {

        var currentSuggestion = this.suggestions[this.currentSuggestionIndex].token;
        const lastToken = tokens[tokens.length - 1];
        const filteredResults = this.suggestions.filter(suggest => suggest.token.startsWith(lastToken));
        if (currentSuggestion.startsWith(lastToken)) {
          const suggesttion = currentSuggestion.substring(lastToken.length, currentSuggestion.length);
          this.updateAutocompleteList(filteredResults);
          this.updateAutocompleteText(nativeElement, suggesttion);
        } else {


          this.updateAutocompleteList(filteredResults);

          this.currentSuggestionIndex = this.suggestions.findIndex(suggest => suggest.token.startsWith(lastToken))


          if (this.currentSuggestionIndex != -1) {
            currentSuggestion = this.suggestions[this.currentSuggestionIndex].token;
            const suggesttion = currentSuggestion.substring(lastToken.length, currentSuggestion.length)
            this.updateAutocompleteText(nativeElement, suggesttion);
          }
          else {
            this.updateAutocompleteList(this.suggestions);
            this.updateAutocompleteText(nativeElement, '');
          }
        }
      }
    }



    return;

  }


  stopAutocomplete(nativeElement: HTMLInputElement) {
    this.autocompleteOpen = false;
    this.startPos = -1;

    if (this.autocompleteList && !this.autocompleteList.hidden) {
      this.autocompleteList.hidden = true;
    }

    if (this.autocompleteElement)
      this.removeAutocomplete(nativeElement);

  }

  updateAutocompleteText(nativeElement: HTMLInputElement, text: string) {
    if (!this.autocompleteElement || this.document.getElementById(this.AutocompleteElementId) == undefined) {
      const sel = this.document.getSelection();
      const range = sel.getRangeAt(0);
      range.deleteContents();
      this.autocompleteElement = this.document.createElement('span');
      this.autocompleteElement.id = this.AutocompleteElementId;
      this.autocompleteElement.textContent = text;
      range.insertNode(this.autocompleteElement);
      range.collapse(true);
      //this.renderer.appendChild(nativeElement, this.autocompleteElement);
      this.renderer.addClass(this.autocompleteElement, 'prediction-hint');
    }
    else {
      this.autocompleteElement.textContent = text;
      this.renderer.setValue(this.autocompleteElement, text);
    }
  }

  removeAutocomplete(nativeElement: HTMLInputElement) {
    const element = this.document.getElementById(this.autocompleteElement.id);
    if (element !== undefined) {
      this.renderer.removeChild(nativeElement, element);
      this.autocompleteElement = undefined;
    }
  }

  stopEvent(event: any) {
    //if (event instanceof KeyboardEvent) { // does not work for iframe
    if (!event.wasClick) {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
    }
  }

  

  updateAutocompleteList(items: any[]) {
    if (items) {
      this.autocompleteList.items = items;
    }

    this.autocompleteList.hidden = !(this.autocompleteList.items.length > 1);
  }

  showSearchList(nativeElement: HTMLInputElement) {

    if (this.autocompleteList == null) {
      let componentFactory = this._componentResolver.resolveComponentFactory(AutocompleteListComponent);
      let componentRef = this._viewContainerRef.createComponent(componentFactory);
      this.autocompleteList = componentRef.instance;
      componentRef.instance['itemClick'].subscribe(() => {
        nativeElement.focus();
        let fakeKeydown = { key: 'Enter', keyCode: KEY_ENTER, wasClick: true };
        this.keyHandler(fakeKeydown, nativeElement);
      });
    }
    this.autocompleteList.labelKey = 'token';
    this.autocompleteList.dropUp = false;
    this.autocompleteList.styleOff = false;
    this.autocompleteList.activeIndex = 0;
    this.autocompleteList.hidden = false;
    this.autocompleteList.position(nativeElement, this.iframe);
    window.requestAnimationFrame(() => this.autocompleteList.reset());
  }

}
