# Vocabulary Question Authoring Instructions (Local Scope)

These instructions apply to files under `static/English/Vocabulary/`.

## Source Material
- Use `word_bank.txt` as the source of tested vocabulary words.
- Tested word (or clear derivative) must come from `word_bank.txt`.
- Distractors/synonyms can come from inside or outside the word bank.

## Output Target
- Add new questions to `questions.json` (do not replace existing questions).
- Output must follow the repository JSON schema defined in the root `AGENTS.md`.
- Top level of `questions.json` must remain a raw JSON array.

## Word Selection
- Select words randomly, preferring words used least often so far.
- Reusing the same target word is allowed when the question itself is different.
- Derived forms are allowed when clearly linked to a word-bank base word.

## Maintaining `word_bank.txt`
- When asked to add new words or phrases to `word_bank.txt`, first check whether each item already exists in the word bank.
- Only append items that are not already present.
- Keep one vocabulary item per line.

## Question Type Selection Default
- If the user does not specify question type(s), produce a mixed question set that includes a mixture of all 5 defined types.

## Supported Question Types and JSON Mapping
1. **Type 1: Word Meaning MCQ**
   - `type`: `word_meaning`
   - `target_word`: tested word
   - `prompt`: `{}`
   - `question`: `What does "<word>" mean?`

2. **Type 2: Reverse Meaning MCQ**
   - `type`: `reverse_meaning`
   - `target_word`: correct answer word
   - `prompt`: `{ "meaning": "..." }`
   - `question`: `Which word matches the meaning given?`

3. **Type 3: Fill in the Blank MCQ**
   - `type`: `fill_in_blank`
   - `target_word`: correct answer word
   - `prompt`: `{ "sentence": "...______..." }`
   - `question`: `Which word best completes the sentence?`

4. **Type 4: Alternative Word MCQ**
   - `type`: `alternative_word`
   - `target_word`: replaceable word in sentence
   - `prompt`: `{ "sentence": "..." }`
   - `question`: `Which word could best replace "<target_word>" without changing the meaning?`

5. **Type 5: Part of Speech MCQ**
   - `type`: `part_of_speech`
   - `target_word`: analysed word
   - `prompt`: `{ "sentence": "..." }`
   - `question`: `In this sentence, what part of speech is "<target_word>"?`

## MCQ Construction Rules
- Exactly 5 choices per question.
- Exactly 1 choice has `"correct": true`.
- Shuffle answer order so the correct option is not fixed to one position.
- Preserve user-provided option order only when converting from a provided plain-text MCQ set.
- Keep language suitable for Year 8 learners.

## Required Fields Per Question
Each new question object must include:
- `id` (sequential and unique, e.g. `eng-vocab-00xx`)
- `type`
- `target_word`
- `prompt`
- `question`
- `choices` (`[{"text":"...","correct":true/false}, ...]`)
- `explanation` (brief, useful reason)

## Guardrails
- Do not add `level` or `difficulty` unless schema intentionally changes.
- Do not put `target_word` inside `prompt`.
- If `target_word` cannot be inferred confidently from input, skip that question and report it.

## Validation
After editing `questions.json`, run:
- `python3 -m json.tool static/English/Vocabulary/questions.json`
