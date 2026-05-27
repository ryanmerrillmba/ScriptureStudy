// js/prose-renderer.js

/**
 * Render a single prose translation column's verse cell.
 * @param {number} verseNum
 * @param {string} text
 * @param {string} cssClass - 'col-kjv' or 'col-esv'
 * @returns {HTMLElement}
 */
export function buildProseCell(verseNum, text, cssClass) {
  const cell = document.createElement('div');
  cell.className = cssClass;

  const num = document.createElement('sup');
  num.className = 'verse-num';
  num.textContent = verseNum;

  const content = document.createTextNode(text);

  cell.appendChild(num);
  cell.appendChild(content);
  return cell;
}
