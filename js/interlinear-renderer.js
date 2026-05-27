// js/interlinear-renderer.js

/**
 * Build a single Hebrew word block element.
 * @param {{ hebrew: string, strongs: string, gloss: string }} word
 * @returns {HTMLElement}
 */
function buildWordBlock(word) {
  const block = document.createElement('div');
  block.className = 'word-block';

  const heb = document.createElement('span');
  heb.className = 'word-hebrew';
  heb.textContent = word.hebrew;

  const strongs = document.createElement('span');
  strongs.className = 'word-strongs';
  strongs.textContent = word.strongs;

  const gloss = document.createElement('span');
  gloss.className = 'word-gloss';
  gloss.textContent = word.gloss;

  block.appendChild(heb);
  block.appendChild(strongs);
  block.appendChild(gloss);
  return block;
}

/**
 * Build the interlinear column cell for one verse.
 * @param {number} verseNum
 * @param {{ hebrew: string, strongs: string, gloss: string }[]} words
 * @returns {HTMLElement}
 */
export function buildInterlinearCell(verseNum, words) {
  const cell = document.createElement('div');
  cell.className = 'col-interlinear';

  const num = document.createElement('sup');
  num.className = 'verse-num';
  num.textContent = verseNum;
  cell.appendChild(num);

  for (const word of words) {
    if (word.hebrew && word.hebrew.trim()) {
      cell.appendChild(buildWordBlock(word));
    }
  }
  return cell;
}
