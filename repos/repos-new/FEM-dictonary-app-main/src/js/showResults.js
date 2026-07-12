const resultsContainer = document.getElementById("results");

export const showSpinner = () => {
  resultsContainer.innerHTML = `
    <div class="spinner-wrapper">
      <p class="sr-only">Loading...</p>
      <div class="spinner"></div>
    </div>
  `;
};

export const clearResults = () => {
  resultsContainer.innerHTML = "";
};

export const showResults = (data) => {
  let results = ``;
  results += generateHeader(data);
  results += generateMeanings(data);
  results += generateSource(data);
  resultsContainer.innerHTML = results;
};

export const showNotFound = () => {
  resultsContainer.innerHTML = `
    <section class="results__not-found">
      <img src="images/not-found.svg" alt="" class="not-found__icon">
      <h3 class="not-found__title">No Definitions Found</h3>
      <p class="not-found__text">Sorry pal, we couldn't find definitions for the word you were looking for. You can try the search again at later time or head to the web instead.</p>
    </section>
  `;
};

const generateHeader = (data) => {
  const { word, phonetics } = data[0];
  const phonetic = phonetics[phonetics.length - 1].text || "";
  const audio = phonetics[phonetics.length - 1].audio || "";

  const header = `
    <header class="results__header">
      <div>
        <h2 class="results__title">${word}</h2>
        <p class="results__pronuntiation">
            <span class="sr-only">Pronunciation:</span>
            ${phonetic}
        </p>
      </div>
      <div>
        ${audio ? generateAudioButton(audio) : ""}
      </div>
    </header>
  `;

  return header;
};

const generateAudioButton = (audio) => {
  return `
    <button class="results__play-button" aria-label="Play pronunciation" onclick="new Audio('${audio}').play();">
      <svg xmlns="http://www.w3.org/2000/svg" width="75" height="75" viewBox="0 0 75 75">
        <g fill="#A445ED" fill-rule="evenodd">
          <circle cx="37.5" cy="37.5" r="37.5" opacity=".25"/>
          <path d="M29 27v21l21-10.5z"/>
        </g>
      </svg>
    </button>
  `;
};

const generateDefinitions = (definitions) =>
  definitions.map(({ definition }) => `<li>${definition}</li>`);

const generateAlternatives = (type, alternatives) => {
  if (alternatives.length === 0) return "";

  return `
      <div class="results__alternatives">
        <h3 class="results__subtitle-2">${type}:</h3>
        <p>${alternatives.join(", ")}</p>
      </div>
    `;
};

const generateMeanings = (data) => {
  const meanings = data[0].meanings;

  const generateMeaningPart = (meaning) => `
    <section class="results__details">
      <div class="results__header-2">
        <p class="results__subtitle-1">
          <strong class="sr-only">Part of speech:</strong>
          <span>
            ${meaning.partOfSpeech}
          </span>
        </p>
        <span class="separator-line"></span>
      </div>

      <h3 class="results__subtitle-2">Meaning:</h3>
      <ul class="results__list">
        ${generateDefinitions(meaning.definitions).join("")}
      </ul>
      ${generateAlternatives("Synonyms", meaning.synonyms)}
      ${generateAlternatives("Antonyms", meaning.antonyms)}
    </section>
  `;

  return meanings.map(generateMeaningPart).join("");
};

const generateSource = (data) => {
  const link = data[0].sourceUrls[0];

  const source = `
    <section class="results__source">
      <span class="separator-line"></span>
      <p>
        <strong>Source</strong>
        <a href="${link}" target="_blank" rel="noopener noreferrer">
          ${link}
          <i class="new-window-icon"></i>
        </a>
      </p>
    </section>
  `;

  return source;
};
