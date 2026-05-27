// js/app.js
import { initSidebar, setSidebarActive } from './sidebar.js';
import { initHeader, updateHeader } from './header.js';
import { buildProseCell } from './prose-renderer.js';
import { buildInterlinearCell } from './interlinear-renderer.js';

const state = {
  books: [],
  currentSlug: null,
  currentChapter: 1,
};

async function loadJSON(path) {
  const resp = await fetch(path);
  if (!resp.ok) throw new Error(`Failed to load ${path}: ${resp.status}`);
  return resp.json();
}

function getBook() {
  return state.books.find(b => b.slug === state.currentSlug);
}

async function renderChapter() {
  const book = getBook();
  if (!book) return;

  const [kjvData, esvData, ilData] = await Promise.all([
    loadJSON(`data/kjv/${book.slug}.json`),
    loadJSON(`data/esv/${book.slug}.json`),
    loadJSON(`data/interlinear/${book.slug}.json`),
  ]);

  const ch = state.currentChapter - 1; // 0-indexed
  const kjvVerses = kjvData.chapters[ch]?.verses || [];
  const esvVerses = esvData.chapters[ch]?.verses || [];
  const ilVerses  = ilData.chapters[ch]?.verses  || [];

  const maxVerses = Math.max(kjvVerses.length, esvVerses.length, ilVerses.length);

  const container = document.getElementById('verse-rows');
  container.innerHTML = '';

  for (let i = 0; i < maxVerses; i++) {
    const kjvV = kjvVerses[i];
    const esvV = esvVerses[i];
    const ilV  = ilVerses[i];
    const verseNum = (kjvV || esvV || ilV).verse;

    const row = document.createElement('div');
    row.className = 'verse-row';
    row.dataset.verse = verseNum;

    row.appendChild(buildProseCell(verseNum, kjvV?.text ?? '', 'col-kjv'));
    row.appendChild(buildProseCell(verseNum, esvV?.text ?? '', 'col-esv'));
    row.appendChild(buildInterlinearCell(verseNum, ilV?.words ?? []));

    container.appendChild(row);
  }

  updateHeader(book.name, state.currentChapter, book.chapters);
  setSidebarActive(book.slug);

  // Sync URL hash for bookmarking
  history.replaceState(null, '', `#${book.slug}/${state.currentChapter}`);

  // Scroll to top of content
  document.getElementById('scroll-container').scrollTop = 0;
}

function selectBook(slug, chapter = 1) {
  state.currentSlug = slug;
  state.currentChapter = chapter;
  renderChapter();
}

function prevChapter() {
  if (state.currentChapter > 1) {
    state.currentChapter--;
    renderChapter();
  }
}

function nextChapter() {
  const book = getBook();
  if (book && state.currentChapter < book.chapters) {
    state.currentChapter++;
    renderChapter();
  }
}

async function init() {
  state.books = await loadJSON('data/books.json');

  initSidebar(state.books, slug => selectBook(slug, 1));
  initHeader(prevChapter, nextChapter);

  // Restore from URL hash if present
  const hash = window.location.hash.slice(1); // e.g. "genesis/3"
  if (hash) {
    const [slug, chStr] = hash.split('/');
    const ch = parseInt(chStr, 10) || 1;
    const book = state.books.find(b => b.slug === slug);
    if (book) {
      selectBook(slug, ch);
      return;
    }
  }

  // Default: open Genesis chapter 1
  selectBook('genesis', 1);
}

init();
