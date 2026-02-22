const form = document.getElementById('commentForm');
const list = document.getElementById('commentList');

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const name = document.getElementById('name').value.trim();
  const stars = document.getElementById('stars').value;
  const message = document.getElementById('message').value.trim();

  if (!name || !stars || !message) return;

  const div = document.createElement('div');
  div.className = 'comment-item';
  div.innerHTML = `<strong>${escapeHtml(name)}</strong> · <span>${escapeHtml(stars)}</span><p>${escapeHtml(message)}</p>`;
  list.prepend(div);

  form.reset();
});

function escapeHtml(text) {
  const map = {
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}