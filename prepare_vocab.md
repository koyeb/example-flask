# Preparing Vocabulary Question JSON

Use this guide to convert plain-text vocabulary multiple choice questions into the app's JSON format.

## Target File

Vocabulary questions should be stored here:

```text
static/English/Vocabulary/questions.json
```

The file must contain a raw JSON array:

```json
[
  {
    "id": "eng-vocab-0001",
    "type": "word_meaning",
    "target_word": "reclusive",
    "prompt": {},
    "question": "What does \"reclusive\" mean?",
    "choices": [
      {
        "text": "Very eager to argue",
        "correct": false
      },
      {
        "text": "Preferring to live alone or avoid other people",
        "correct": true
      }
    ],
    "explanation": "Reclusive means preferring to live alone or avoid other people."
  }
]
```

Do not wrap the array in a top-level object. Do not add `level` or `difficulty`.

The same vocabulary word may appear in more than one question as long as the questions are different. For example, `prudent` may be used once in a word meaning question and again in an alternative word question.

## Required Fields

Each question must have:

- `id`: stable unique id in sequence, such as `eng-vocab-0001`.
- `type`: snake_case type name.
- `target_word`: the single vocabulary item being tested.
- `prompt`: source material shown to the student, such as a meaning or sentence.
- `question`: the text shown to the student.
- `choices`: answer options as objects with `text` and `correct`.
- `explanation`: a short explanation for the correct answer.

Exactly one choice must have `"correct": true`.

Use top-level `target_word` as the single canonical field for the vocabulary item being tested. Do not put `target_word` inside `prompt`, and do not use a separate `word` field. Include `target_word` for every question type, including reverse-meaning and fill-in-the-blank questions. The app should not display `target_word` while preparing the student-facing exercise; it is metadata for scoring, review, or future filtering.

If `target_word` is not explicitly specified in the input, infer it using best judgement. Usually it comes from the `Word:` line, the correct answer, the highlighted/referenced word, or the blank's correct completion. If `target_word` cannot be determined confidently, skip that question and report it back instead of guessing.

## Question Types

Use these type names:

```text
word_meaning
reverse_meaning
fill_in_blank
alternative_word
part_of_speech
```

## Type Mapping

For `Type 1: Word Meaning MCQ`, convert:

```text
Word: reclusive
```

to:

```json
"type": "word_meaning",
"target_word": "reclusive",
"prompt": {},
"question": "What does \"reclusive\" mean?"
```

For `Type 2: Reverse Meaning MCQ`, convert:

```text
Meaning given:
“Done secretly, especially because it should not be noticed.”
```

to:

```json
"type": "reverse_meaning",
"target_word": "surreptitious",
"prompt": {
  "meaning": "Done secretly, especially because it should not be noticed."
},
"question": "Which word matches the meaning given?"
```

For `Type 3: Fill in the Blank MCQ`, convert the sentence to:

```json
"type": "fill_in_blank",
"target_word": "wither",
"prompt": {
  "sentence": "The old bridge looked strong, but the wooden railings had begun to ______ after years of rain and wind."
},
"question": "Which word best completes the sentence?"
```

For `Type 4: Alternative Word MCQ`, convert the sentence and target word to:

```json
"type": "alternative_word",
"target_word": "terse",
"prompt": {
  "sentence": "His terse reply made it clear that he did not want to discuss the matter further."
},
"question": "Which word could best replace \"terse\" without changing the meaning?"
```

For `Type 5: Part of Speech MCQ`, convert the sentence and target word to:

```json
"type": "part_of_speech",
"target_word": "meticulously",
"prompt": {
  "sentence": "The students worked meticulously on their model castle, checking every tiny detail."
},
"question": "In this sentence, what part of speech is \"meticulously\"?"
```

## Choices

Convert lettered answers into the `choices` array. Preserve the answer text, but do not store the letters `A`, `B`, `C`, `D`, or `E`.

```json
"choices": [
  {
    "text": "Surreptitious",
    "correct": true
  },
  {
    "text": "Robust",
    "correct": false
  }
]
```

## Explanations

Add a concise explanation for each question. The explanation should explain why the correct answer is correct, not merely repeat the answer.

Examples:

```text
Surreptitious means done secretly or in a hidden way.
Wither means to dry up, weaken, or decay.
Meticulously describes how the students worked, so it is an adverb.
```

## Validation Checklist

Before returning the JSON:

- The output is valid JSON.
- The top level is an array.
- Every question has all required fields.
- Every question has top-level `target_word`.
- Every `target_word` is either provided by the input or confidently inferred; uncertain questions are skipped and reported.
- No prompt uses `target_word` or `word`.
- Every `id` is unique.
- Every `type` is one of the approved type names.
- Every question has exactly one correct choice.
- Repeated vocabulary is acceptable when the question itself is distinct.
- No question includes `level` or `difficulty`.
- Quotation marks inside strings are escaped correctly.
