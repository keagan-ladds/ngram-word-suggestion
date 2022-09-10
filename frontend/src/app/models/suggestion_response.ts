export class SuggestionResponse
{
    next_words: WordSuggestion[];
    replacements: WordReplacement[];
}

export class WordSuggestion {
    score: number;
    token: string;
}

export class WordReplacement {
    token: string;
    replacement: string;
}