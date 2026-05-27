// js/sidebar.js
const CATEGORIES = ['Law', 'History', 'Poetry', 'Major Prophets', 'Minor Prophets'];

export function initSidebar(books, onSelect) {
  const container = document.getElementById('book-list');

  const byCategory = {};
  for (const book of books) {
    (byCategory[book.category] ||= []).push(book);
  }

  for (const cat of CATEGORIES) {
    const catBooks = byCategory[cat] || [];
    if (!catBooks.length) continue;

    const label = document.createElement('div');
    label.className = 'category-label';
    label.textContent = cat;
    container.appendChild(label);

    for (const book of catBooks) {
      const item = document.createElement('div');
      item.className = 'book-item';
      item.textContent = book.name;
      item.dataset.slug = book.slug;
      item.addEventListener('click', () => onSelect(book.slug));
      container.appendChild(item);
    }
  }
}

export function setSidebarActive(slug) {
  document.querySelectorAll('.book-item').forEach(el => {
    el.classList.toggle('active', el.dataset.slug === slug);
  });
}
