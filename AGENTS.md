# Agent Instructions

- Before merging any branch into `main`, create a backup branch from the branch being merged.
- Name the backup branch `<branch_to_be_merged>_backup`.

- This rule applies to all future merges into `main`.


## Destructive Edit Safeguard

- If a request would delete or overwrite a large portion of a dataset file (for example, removing a broad ID range like "51 to end"), do not execute immediately.
- First, restate the exact impact with concrete counts or ranges (for example, "this will delete questions eng-vocab-0051 through eng-vocab-0175").
- Ask for explicit confirmation before applying the destructive change, unless the user has already confirmed after seeing that impact summary.
- When the user goal is quality cleanup, prefer targeted removal of only the flagged or invalid items instead of bulk truncation.
- After destructive edits, include a short post-change summary of what was removed and what remains.

## Octopus Endpoint Notes

- The `/octopus` endpoint returns an HTML page (not JSON).
- It shows the best (cheapest) continuous upcoming usage window for each supported appliance duration.
- For each suggested window, the UI includes a collapsed-by-default expandable section with a mini table of half-hour slots and their tariff values in `p/kWh`.

## Vocabulary Endpoint Notes

- The `/vocab` endpoint returns an HTML practice page for `static/English/Vocabulary/questions.json`.
- By default, `/vocab` shows 10 randomly sampled questions. Supported quiz sizes are `5`, `10`, `15`, `20`, `25`, and `30`.
- If the requested quiz size is larger than the available question bank, show all available questions.
- The server shuffles the selected question set and shuffles each question's choices before sending them to the page.
- It is acceptable for the HTML document to carry answer metadata such as `correct` and `target_word`, but the page must not visibly display correct answers before marking.
- The main `Submit` button marks the quiz in the browser. Unanswered questions count as wrong.
- After submit, show the score as a fraction such as `7/10`: green for `>= 80%`, amber for `>= 60%` and `< 80%`, and red for `< 60%`.
- On submit, wrong questions should not reveal the correct answer. They should remain answerable and show a per-question `Retry` button until the student selects the correct option.
- When a retry attempt is correct, show `Retry correct` in blue instead of the normal first-attempt `Correct` label.
- Retry marking is client-side only and does not send feedback to the server.
- On submit, send the `target_word` values for questions missed on the first marking attempt to `POST /vocab/feedback` using this payload shape:
  ```json
  {
    "missed_target_words": ["example"]
  }
  ```
- Marking should not wait for feedback to complete. The page should show feedback status beside the submit button.
- The `Regenerate` control should request a fresh random set without a full page reload when practical, using `GET /vocab/questions?count=<count>`.

## Study Question Storage

- Store multiple choice study questions under `static/<Subject>/<Category>/questions.json`.
- Use folder names to identify the subject and category, for example `static/English/Vocabulary/questions.json`.
- Each `questions.json` file should contain a raw JSON array of question objects, not an outer wrapper object.
- Do not include `level` or `difficulty` fields unless the schema is intentionally changed later.
- Each question object should use:
  - `id`: stable unique id, for example `eng-vocab-0001`.
  - `type`: snake_case question type, for example `word_meaning`, `reverse_meaning`, `fill_in_blank`, `alternative_word`, or `part_of_speech`.
  - `target_word`: the single canonical vocabulary item being tested.
  - `prompt`: object containing the source material shown to the student, such as `meaning` and/or `sentence`.
  - `question`: student-facing question text.
  - `choices`: array of answer objects, each with `text` and `correct`.
  - `explanation`: short explanation of the correct answer.
- Exactly one choice should have `"correct": true`.

## Preparing Vocabulary Question JSON

- When the user provides plain-text vocabulary MCQs, append them to `static/English/Vocabulary/questions.json` unless they specify another subject/category.
- Continue the existing id sequence. For example, if the last id is `eng-vocab-0024`, the next id is `eng-vocab-0025`.
- The same vocabulary word may appear in more than one question as long as the questions are different, for example a word meaning question and a fill-in-the-blank question for the same word.
- Use top-level `target_word` as the single canonical field for the vocabulary item being tested. Do not put `target_word` inside `prompt`, and do not use a separate `word` field.
- Include `target_word` for every vocabulary question type, including reverse-meaning and fill-in-the-blank questions. The app should not expose `target_word` while preparing the student-facing exercise; it is metadata for scoring, review, or future filtering.
- If `target_word` is not explicitly specified in the user's input, infer it from the question using best judgement, usually from the `Word:` line, the correct answer, the highlighted/referenced word, or the blank's correct completion.
- If `target_word` cannot be determined confidently, skip adding that question and report it back to the user.
- Preserve the user's answer option order, but do not store option letters such as `A`, `B`, `C`, `D`, or `E`.
- Convert each answer option to `{ "text": "...", "correct": true/false }`.
- Mark exactly one answer as correct, based on the intended answer from the prompt.
- Add a concise `explanation` for every new question. Explain why the correct answer is correct; do not merely repeat the answer.
- Use ASCII punctuation in JSON strings where practical, including straight quotes rather than curly quotes.
- After editing a question bank, validate it with `python3 -m json.tool static/English/Vocabulary/questions.json`.

Use these mappings for vocabulary question batches:

- `Type 1: Word Meaning MCQ`
  - `type`: `word_meaning`
  - `target_word`: `<word>`
  - `prompt`: `{}`
  - `question`: `What does "<word>" mean?`
- `Type 2: Reverse Meaning MCQ`
  - `type`: `reverse_meaning`
  - `target_word`: `<correct answer>`
  - `prompt`: `{ "meaning": "<meaning>" }`
  - `question`: `Which word matches the meaning given?`
- `Type 3: Fill in the Blank MCQ`
  - `type`: `fill_in_blank`
  - `target_word`: `<correct answer>`
  - `prompt`: `{ "sentence": "<sentence with ______>" }`
  - `question`: `Which word best completes the sentence?`
- `Type 4: Alternative Word MCQ`
  - `type`: `alternative_word`
  - `target_word`: `<target word>`
  - `prompt`: `{ "sentence": "<sentence>" }`
  - `question`: `Which word could best replace "<target word>" without changing the meaning?`
- `Type 5: Part of Speech MCQ`
  - `type`: `part_of_speech`
  - `target_word`: `<target word>`
  - `prompt`: `{ "sentence": "<sentence>" }`
  - `question`: `In this sentence, what part of speech is "<target word>"?`

Before finishing, check:

- The top level is still a JSON array.
- Every new id is unique and sequential.
- Every new question has `id`, `type`, `target_word`, `prompt`, `question`, `choices`, and `explanation`.
- Every new `target_word` is either provided by the user or confidently inferred; uncertain questions are skipped and reported.
- No prompt uses `target_word` or `word`.
- Every new question has exactly one correct choice.
- Repeated vocabulary is acceptable when the question itself is distinct.
- No new question includes `level` or `difficulty`.
