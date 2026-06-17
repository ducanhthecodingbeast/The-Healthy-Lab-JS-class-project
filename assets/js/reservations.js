const RESERVATION_KEY = 'thl_reservations';
const QUEUE_KEY = 'thl_queue_entries';

document.addEventListener('DOMContentLoaded', () => {
  if (!requireLogin()) return;

  const user = getCurrentUser() || {};
  fillUserDefaults(user);
  renderLocalLists();

  document.getElementById('reservation-form').addEventListener('submit', saveReservation);
  document.getElementById('queue-form').addEventListener('submit', saveQueueEntry);
});

function fillUserDefaults(user) {
  document.getElementById('res-name').value = user.name || '';
  document.getElementById('res-phone').value = user.phone || '';
  document.getElementById('queue-name').value = user.name || '';
  document.getElementById('queue-phone').value = user.phone || '';
}

function readList(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) || [];
  } catch {
    return [];
  }
}

function writeList(key, list) {
  localStorage.setItem(key, JSON.stringify(list));
}

async function saveReservation(event) {
  event.preventDefault();
  const reservation = {
    customer_name: document.getElementById('res-name').value,
    customer_phone: document.getElementById('res-phone').value,
    party_size: Number(document.getElementById('res-party').value),
    reservation_time: document.getElementById('res-time').value,
    note: document.getElementById('res-note').value,
    status: 'booked'
  };

  const created = await createReservation(reservation);
  if (!created) {
    const list = readList(RESERVATION_KEY);
    list.unshift({ ...reservation, id: Date.now() });
    writeList(RESERVATION_KEY, list);
  }
  setStatus('Reservation saved');
  event.target.reset();
  fillUserDefaults(getCurrentUser() || {});
  renderLocalLists();
}

async function saveQueueEntry(event) {
  event.preventDefault();
  const entry = {
    customer_name: document.getElementById('queue-name').value,
    customer_phone: document.getElementById('queue-phone').value,
    party_size: Number(document.getElementById('queue-party').value),
    status: 'waiting',
    wait_minutes: 0
  };

  const created = await createQueueEntry(entry);
  if (!created) {
    const list = readList(QUEUE_KEY);
    list.unshift({ ...entry, id: Date.now() });
    writeList(QUEUE_KEY, list);
  }
  setStatus('Queue entry saved');
  event.target.reset();
  fillUserDefaults(getCurrentUser() || {});
  renderLocalLists();
}

function renderLocalLists() {
  renderList('reservation-list', readList(RESERVATION_KEY), item => `
    <strong>${item.customer_name} · ${item.party_size} guests</strong>
    <span>${item.reservation_time || 'Time pending'} · ${item.status}</span>
  `);
  renderList('queue-list', readList(QUEUE_KEY), item => `
    <strong>${item.customer_name} · ${item.party_size} guests</strong>
    <span>${item.status} · ${item.wait_minutes || 0} min</span>
  `);
}

function renderList(id, list, template) {
  const target = document.getElementById(id);
  target.innerHTML = list.length
    ? list.map(item => `<div class="guest-list-item">${template(item)}</div>`).join('')
    : '<p style="font-size:1.4rem; color:#777; margin:0;">No entries yet.</p>';
}

function setStatus(message) {
  const status = document.getElementById('guest-status');
  status.textContent = message;
  setTimeout(() => {
    status.textContent = 'Ready';
  }, 2500);
}
