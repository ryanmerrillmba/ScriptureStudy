// === State ===
let books = [];
let currentBook = null;
let currentChapter = 1;

// === DOM Refs ===
const bookList = document.getElementById('book-list');
const verseRows = document.getElementById('verse-rows');
const scrollContainer = document.getElementById('scroll-container');
const bookSelect = document.getElementById('book-select');
const chapterSelect = document.getElementById('chapter-select');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');

// === Categories ===
const categoryOrder = ['Law', 'History', 'Poetry', 'Major Prophets', 'Minor Prophets'];

// === Init ===
async function init() {
  try {
    const resp = await fetch('data/books.json');
    books = await resp.json();
  } catch (err) {
    console.error('Failed to load books.json:', err);
    bookList.innerHTML = '<div class="empty-state">Failed to load books.</div>';
    return;
  }

  renderSidebar();
  populateBookSelect();

  // Parse hash: #genesis/3
  const hash = window.location.hash.slice(1);
  if (hash) {
    const parts = hash.split('/');
    const slug = parts[0];
    const chapter = parseInt(parts[1], 10) || 1;
    const book = books.find(b => b.slug === slug);
    if (book) {
      await loadChapter(book, chapter, false);
    }
  }
}

// === Dropdown Population ===
function populateBookSelect() {
  bookSelect.innerHTML = '';
  for (const book of books) {
    const opt = document.createElement('option');
    opt.value = book.slug;
    opt.textContent = book.name;
    if (currentBook && currentBook.slug === book.slug) {
      opt.selected = true;
    }
    bookSelect.appendChild(opt);
  }
}

function populateChapterSelect() {
  chapterSelect.innerHTML = '';
  if (!currentBook) return;

  for (let i = 1; i <= currentBook.chapters; i++) {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = i;
    if (i === currentChapter) {
      opt.selected = true;
    }
    chapterSelect.appendChild(opt);
  }
}

// === Sidebar Rendering ===
function renderSidebar() {
  bookList.innerHTML = '';

  const grouped = {};
  for (const cat of categoryOrder) {
    grouped[cat] = books.filter(b => b.category === cat);
  }

  for (const cat of categoryOrder) {
    const booksInCat = grouped[cat];
    if (!booksInCat || booksInCat.length === 0) continue;

    const label = document.createElement('div');
    label.className = 'book-category';
    label.textContent = cat;
    bookList.appendChild(label);

    for (const book of booksInCat) {
      const item = document.createElement('div');
      item.className = 'book-item';
      item.textContent = book.name;
      item.dataset.slug = book.slug;

      if (currentBook && currentBook.slug === book.slug) {
        item.classList.add('active');
      }

      item.addEventListener('click', () => loadChapter(book, 1, true));
      bookList.appendChild(item);
    }
  }
}

// === Chapter Loading ===
async function loadChapter(book, chapter, updateHash) {
  currentBook = book;
  currentChapter = chapter;

  // Update sidebar active state
  document.querySelectorAll('.book-item').forEach(item => {
    item.classList.toggle('active', item.dataset.slug === book.slug);
  });

  // Update dropdowns
  bookSelect.value = book.slug;
  populateChapterSelect();
  chapterSelect.value = chapter;

  // Update nav buttons
  btnPrev.disabled = chapter <= 1;
  btnNext.disabled = chapter >= book.chapters;

  // Update hash
  if (updateHash) {
    window.location.hash = `#${book.slug}/${chapter}`;
  }

  // Show loading state
  verseRows.innerHTML = '<div class="empty-state">Loading...</div>';

  try {
    const [kjvData, esvData, interlinearData] = await Promise.all([
      fetch(`data/kjv/${book.slug}.json`).then(r => r.json()),
      fetch(`data/esv/${book.slug}.json`).then(r => r.json()),
      fetch(`data/interlinear/${book.slug}.json`).then(r => r.json())
    ]);

    renderVerses(kjvData, esvData, interlinearData, chapter);
  } catch (err) {
    console.error('Failed to load chapter data:', err);
    verseRows.innerHTML = '<div class="empty-state">Failed to load chapter data. Make sure data files exist for this book.</div>';
  }
}

// === Verse Rendering ===
function renderVerses(kjvData, esvData, interlinearData, chapter) {
  verseRows.innerHTML = '';

  const kjvChapter = kjvData.chapters.find(c => c.chapter === chapter);
  const esvChapter = esvData.chapters.find(c => c.chapter === chapter);
  const interlinearChapter = interlinearData.chapters.find(c => c.chapter === chapter);

  if (!kjvChapter || !esvChapter || !interlinearChapter) {
    verseRows.innerHTML = '<div class="empty-state">Chapter data not found.</div>';
    return;
  }

  const maxVerses = Math.max(
    kjvChapter.verses.length,
    esvChapter.verses.length,
    interlinearChapter.verses.length
  );

  for (let i = 0; i < maxVerses; i++) {
    const kjvVerse = kjvChapter.verses[i];
    const esvVerse = esvChapter.verses[i];
    const interlinearVerse = interlinearChapter.verses[i];

    const verseNum = kjvVerse ? kjvVerse.verse
      : (esvVerse ? esvVerse.verse
      : (interlinearVerse ? interlinearVerse.verse : i + 1));

    const row = document.createElement('div');
    row.className = 'verse-row';

    // KJV cell
    const kjvCell = document.createElement('div');
    kjvCell.className = 'col-kjv';
    if (kjvVerse) {
      kjvCell.innerHTML = `<sup class="verse-num">${kjvVerse.verse}</sup>${escapeHtml(kjvVerse.text)}`;
    } else {
      kjvCell.innerHTML = `<sup class="verse-num">${verseNum}</sup><span style="color:#555">\u2014</span>`;
    }
    row.appendChild(kjvCell);

    // ESV cell
    const esvCell = document.createElement('div');
    esvCell.className = 'col-esv';
    if (esvVerse) {
      esvCell.innerHTML = `<sup class="verse-num">${esvVerse.verse}</sup>${escapeHtml(esvVerse.text)}`;
    } else {
      esvCell.innerHTML = `<sup class="verse-num">${verseNum}</sup><span style="color:#555">\u2014</span>`;
    }
    row.appendChild(esvCell);

    // Interlinear cell
    const interlinearCell = document.createElement('div');
    interlinearCell.className = 'col-interlinear';
    if (interlinearVerse) {
      let html = `<sup class="verse-num">${interlinearVerse.verse}</sup>`;
      html += '<div class="word-block-container">';
      for (const word of interlinearVerse.words) {
        html += `<div class="word-block">`;
        html += `<span class="font-display-hebrew text-display-hebrew text-custom-hebrew pb-1">${escapeHtml(word.hebrew)}</span>`;
        html += `<span class="font-strongs-number text-strongs-number text-custom-strongs">${escapeHtml(word.strongs)}</span>`;
        html += `<span class="font-gloss-text text-gloss-text text-custom-gloss italic pt-1">${escapeHtml(word.gloss)}</span>`;
        html += `</div>`;
      }
      html += '</div>';
      interlinearCell.innerHTML = html;
    } else {
      interlinearCell.innerHTML = `<sup class="verse-num">${verseNum}</sup><span style="color:#555">\u2014</span>`;
    }
    row.appendChild(interlinearCell);

    verseRows.appendChild(row);
  }

  // Scroll to top
  scrollContainer.scrollTop = 0;
}

// === Dropdown Event Handlers ===
bookSelect.addEventListener('change', () => {
  const slug = bookSelect.value;
  const book = books.find(b => b.slug === slug);
  if (book && (!currentBook || currentBook.slug !== slug)) {
    loadChapter(book, 1, true);
  }
});

chapterSelect.addEventListener('change', () => {
  const chapter = parseInt(chapterSelect.value, 10);
  if (currentBook && chapter !== currentChapter) {
    loadChapter(currentBook, chapter, true);
  }
});

// === Nav Buttons ===
btnPrev.addEventListener('click', () => {
  if (currentBook && currentChapter > 1) {
    loadChapter(currentBook, currentChapter - 1, true);
  }
});

btnNext.addEventListener('click', () => {
  if (currentBook && currentChapter < currentBook.chapters) {
    loadChapter(currentBook, currentChapter + 1, true);
  }
});

// === Utility ===
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// === Hash Change (browser back/forward) ===
window.addEventListener('hashchange', () => {
  const hash = window.location.hash.slice(1);
  if (hash) {
    const parts = hash.split('/');
    const slug = parts[0];
    const chapter = parseInt(parts[1], 10) || 1;
    const book = books.find(b => b.slug === slug);
    if (book) {
      loadChapter(book, chapter, false);
    }
  }
});

// === Boot ===
init();
