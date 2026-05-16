document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('hamburger');
    const menu = document.getElementById('menu');

    if (hamburger && menu) {
        hamburger.addEventListener('click', () => {
            menu.classList.toggle('open');
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const quiz = document.getElementById('vocab-quiz');
    const questionList = document.getElementById('vocab-question-list');
    const countInput = document.getElementById('vocab-count');
    const countLabel = document.getElementById('vocab-count-label');
    const regenerateButton = document.getElementById('vocab-regenerate');
    const submitStatus = document.getElementById('vocab-submit-status');

    if (!quiz || !questionList || !countInput || !countLabel || !regenerateButton || !submitStatus) {
        return;
    }

    const allowedCounts = window.vocabAllowedCounts || [5, 10, 15, 20, 25, 30];
    let questions = window.vocabInitialQuestions || [];

    const getSelectedCount = () => allowedCounts[Number(countInput.value)] || 10;

    const setStatus = (message, tone = '') => {
        submitStatus.textContent = message;
        submitStatus.dataset.tone = tone;
    };

    const renderPrompt = (prompt) => {
        const parts = [];

        if (prompt.meaning) {
            parts.push(`<p class="vocab-prompt"><strong>Meaning:</strong> ${escapeHtml(prompt.meaning)}</p>`);
        }

        if (prompt.sentence) {
            parts.push(`<p class="vocab-prompt">${escapeHtml(prompt.sentence)}</p>`);
        }

        return parts.join('');
    };

    const renderQuestions = () => {
        questionList.innerHTML = '';
        setStatus('');

        if (!questions.length) {
            questionList.innerHTML = '<section class="vocab-empty">No vocabulary questions are available.</section>';
            return;
        }

        const fragment = document.createDocumentFragment();

        questions.forEach((question, index) => {
            const article = document.createElement('article');
            article.className = 'vocab-question';
            article.dataset.questionIndex = String(index);
            article.dataset.targetWord = question.target_word || '';

            const choices = (question.choices || []).map((choice, choiceIndex) => `
                <label class="vocab-choice">
                    <input
                        type="radio"
                        name="vocab-${escapeHtml(question.id)}"
                        value="${choiceIndex}"
                        data-correct="${choice.correct ? 'true' : 'false'}"
                    >
                    <span>${escapeHtml(choice.text)}</span>
                </label>
            `).join('');

            article.innerHTML = `
                <div class="vocab-question-head">
                    <span class="vocab-number">Question ${index + 1}</span>
                    <span class="vocab-result" aria-live="polite"></span>
                </div>
                ${renderPrompt(question.prompt || {})}
                <h2>${escapeHtml(question.question || '')}</h2>
                <div class="vocab-choices">${choices}</div>
                <div class="vocab-retry-row">
                    <button type="button" class="vocab-button vocab-button-small vocab-retry" hidden>Retry</button>
                </div>
            `;

            fragment.appendChild(article);
        });

        questionList.appendChild(fragment);
    };

    const markQuestion = (questionElement) => {
        const selectedChoice = questionElement.querySelector('input[type="radio"]:checked');
        const result = questionElement.querySelector('.vocab-result');
        const retryButton = questionElement.querySelector('.vocab-retry');
        const isCorrect = selectedChoice && selectedChoice.dataset.correct === 'true';

        questionElement.classList.remove('is-correct', 'is-wrong');

        if (isCorrect) {
            questionElement.classList.add('is-correct');
            result.textContent = 'Correct';
            retryButton.hidden = true;
            return true;
        }

        questionElement.classList.add('is-wrong');
        result.textContent = selectedChoice ? 'Try again' : 'No answer selected';
        retryButton.hidden = false;
        return false;
    };

    const sendFeedback = async (missedTargetWords) => {
        setStatus('Sending feedback...', 'pending');

        try {
            const response = await fetch('/vocab/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ missed_target_words: missedTargetWords }),
            });

            if (!response.ok) {
                throw new Error('Feedback failed');
            }

            setStatus('Feedback received', 'success');
        } catch (error) {
            setStatus('Feedback failed', 'error');
        }
    };

    countInput.addEventListener('input', () => {
        countLabel.textContent = String(getSelectedCount());
    });

    regenerateButton.addEventListener('click', async () => {
        const count = getSelectedCount();
        regenerateButton.disabled = true;
        setStatus('Loading new questions...', 'pending');

        try {
            const response = await fetch(`/vocab/questions?count=${count}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Could not load questions');
            }

            questions = data.questions || [];
            renderQuestions();
            setStatus(`Loaded ${questions.length} questions`, 'success');
        } catch (error) {
            setStatus('Could not regenerate questions', 'error');
        } finally {
            regenerateButton.disabled = false;
        }
    });

    quiz.addEventListener('click', (event) => {
        if (!event.target.classList.contains('vocab-retry')) {
            return;
        }

        const questionElement = event.target.closest('.vocab-question');
        markQuestion(questionElement);
    });

    quiz.addEventListener('submit', (event) => {
        event.preventDefault();

        const missedTargetWords = [];
        const questionElements = questionList.querySelectorAll('.vocab-question');

        questionElements.forEach((questionElement) => {
            const isCorrect = markQuestion(questionElement);

            if (!isCorrect && questionElement.dataset.targetWord) {
                missedTargetWords.push(questionElement.dataset.targetWord);
            }
        });

        sendFeedback(missedTargetWords);
    });

    renderQuestions();
});

const escapeHtml = (value) => {
    const element = document.createElement('div');
    element.textContent = value || '';
    return element.innerHTML;
};
