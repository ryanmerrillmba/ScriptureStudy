// js/header.js
export function initHeader(onPrev, onNext) {
  document.getElementById('btn-prev').addEventListener('click', onPrev);
  document.getElementById('btn-next').addEventListener('click', onNext);
}

export function updateHeader(bookName, chapter, totalChapters) {
  document.getElementById('book-title').textContent = bookName;
  document.getElementById('chapter-display').textContent =
    `Chapter ${chapter} of ${totalChapters}`;
  document.getElementById('btn-prev').disabled = chapter <= 1;
  document.getElementById('btn-next').disabled = chapter >= totalChapters;
}
