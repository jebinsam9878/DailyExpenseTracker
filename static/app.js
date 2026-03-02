document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('expenseForm');
    const expensesTable = document.getElementById('expensesTable');
    const totalBadge = document.getElementById('totalBadge');
    const submitBtn = document.getElementById('submitBtn');
    const cancelEdit = document.getElementById('cancelEdit');
    const chartElem = document.getElementById('expenseChart');
    const expenseChartCtx = chartElem ? chartElem.getContext('2d') : null;
    const filterStart = document.getElementById('filterStart');
    const filterEnd = document.getElementById('filterEnd');
    const filterCategory = document.getElementById('filterCategory');
    const exportCsvBtn = document.getElementById('exportCsv');
    const searchText = document.getElementById('searchText');
    const quickFilterButtons = document.querySelectorAll('.quick-filter-btn');
    const lastUpdatedLabel = document.getElementById('lastUpdated');
    const noteModal = new bootstrap.Modal(document.getElementById('noteModal'));
    const modalNotesContent = document.getElementById('modalNotesContent');

    let expenses = [];
    let editingId = document.getElementById('expenseId') ? document.getElementById('expenseId').value || null : null;
    let chart = null;

    function formatDateString(s) {
        if (!s) return '';
        const d = new Date(s);
        if (isNaN(d)) return s;
        return d.toLocaleDateString('en-GB');
    }

    function loadInitialExpenses() {
        const rows = expensesTable ? expensesTable.querySelectorAll('tbody tr') : [];
        rows.forEach(row => {
            const id = row.dataset.id;
            const date = row.querySelector('.exp-date').textContent.trim();
            const name = row.querySelector('.exp-name').textContent.trim();
            const cat = row.dataset.category || '';
            const amountText = row.querySelector('.exp-amount').textContent.replace('₹', '').trim();
            const amount = parseFloat(amountText);
            const notes = row.dataset.notes || '';
            expenses.push({ id, date, name, category: cat, amount, notes });
        });
    }


    function renderCategoryBadge(category) {
        switch (category) {
            case 'Food':
                return '<span class="category-badge badge-food">🍔 Food</span>';
            case 'Transport':
                return '<span class="category-badge badge-transport">🚗 Transport</span>';
            case 'Shopping':
                return '<span class="category-badge badge-shopping">🛍️ Shopping</span>';
            case 'Utilities':
                return '<span class="category-badge badge-utilities">⚡ Utilities</span>';
            case 'Other':
                return '<span class="category-badge badge-other">📦 Other</span>';
            default:
                return category || '';
        }
    }

    function renderTable(data = expenses) {
        const tbody = expensesTable.querySelector('tbody');
        tbody.innerHTML = '';
        data.forEach(e => {
            const tr = document.createElement('tr');
            tr.dataset.id = e.id;
            tr.dataset.notes = e.notes || '';
            tr.innerHTML = `
                <td class="exp-date">${formatDateString(e.date)}</td>
                <td class="exp-cat">${renderCategoryBadge(e.category)}</td>
                <td class="exp-name"><strong>${e.name}</strong></td>
                <td class="exp-amount fw-bold text-end" style="color: #4facfe;">₹${e.amount.toFixed(2)}</td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-secondary me-1 edit-btn" title="Edit"><i class="fas fa-pen"></i></button>
                  <button class="btn btn-sm btn-outline-danger delete-btn" title="Delete"><i class="fas fa-trash"></i></button>
                  <button class="btn btn-sm btn-outline-info note-btn" title="View notes${e.notes ? (': ' + e.notes.replace(/"/g,'\"').slice(0,50)) : ''}"><i class="fas fa-sticky-note"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        // delegation listener attached once at init, no further action needed here
    }

    function renderChart(dataSet = expenses) {
        if (!expenseChartCtx) return; // nothing to do if canvas missing
        const labels = dataSet.map(e => e.date);
        const data = dataSet.map(e => e.amount);
        if (chart) {
            chart.data.labels = labels;
            chart.data.datasets[0].data = data;
            chart.update();
        } else {
            // Create gradient for the chart
            const gradient = expenseChartCtx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(102, 126, 234, 0.6)');
            gradient.addColorStop(1, 'rgba(240, 147, 251, 0.1)');

            chart = new Chart(expenseChartCtx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'Expense (₹)',
                        data,
                        borderColor: '#667eea',
                        backgroundColor: gradient,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#667eea',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    animation: { duration: 0 },          // disable animations for faster redraw
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        x: { 
                            display: true,
                            ticks: { color: '#e0e0e0', font: { weight: '600' } },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        y: { 
                            beginAtZero: true,
                            ticks: { color: '#e0e0e0', font: { weight: '600' } },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        }
                    },
                    plugins: {
                        legend: { 
                            labels: { 
                                color: '#e0e0e0',
                                font: { size: 12, weight: '600' },
                                padding: 20
                            } 
                        },
                        filler: {
                            propagate: true
                        }
                    }
                }
            });
        }
    }

    // old per-row binding replaced by delegation for reliability
    function bindTableActions() {
        // no longer used; kept for backward compatibility if called
    }

    function bindNoteButtons() {
        // nothing here; all clicks are handled via delegation
    }

    function onEdit(evt) {
        const tr = evt.target.closest('tr');
        if (!tr) return;
        editingId = tr.dataset.id;
        const exp = expenses.find(e => e.id == editingId);
        if (exp) {
            form.date.value = exp.date;
            form.name.value = exp.name;
            form.amount.value = exp.amount;
            form.category.value = exp.category || '';
            form.notes.value = exp.notes || '';
            submitBtn.textContent = 'Update Expense';
            submitBtn.classList.remove('btn-success');
            submitBtn.classList.add('btn-warning');
            cancelEdit.classList.remove('d-none');
        }
    }

    function onDelete(evt) {
        const tr = evt.target.closest('tr');
        if (!tr) return;
        const id = tr.dataset.id;
        if (!confirm('Are you sure you want to delete this entry?')) return;
        fetch(`/api/expenses/${id}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(() => {
                expenses = expenses.filter(e => e.id != id);
                applyFilters();
            });
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            date: form.date.value,
            category: form.category.value,
            name: form.name.value,
            amount: parseFloat(form.amount.value),
            notes: form.notes.value
        };
        if (editingId) {
            fetch(`/api/expenses/${editingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(updated => {
                const idx = expenses.findIndex(e => e.id == editingId);
                expenses[idx] = updated;
                // clear filters so the updated item is visible
                filterStart.value = '';
                filterEnd.value = '';
                filterCategory.value = '';
                applyFilters();
                resetForm();
                fetchLatest();
            })
            .catch(err => console.error('Error updating expense', err));
        } else {
            fetch('/api/expenses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(r => {
                if (!r.ok) throw new Error('Add failed: ' + r.status);
                return r.json();
            })
            .then(created => {
                if (!expenses.find(e => e.id == created.id)) {
                    expenses.push(created);
                }
                // clear any active filters when new record added
                filterStart.value = '';
                filterEnd.value = '';
                filterCategory.value = '';
                applyFilters();
                resetForm();
                // scroll to bottom of table so the new entry is visible
                const tbody = expensesTable.querySelector('tbody');
                if (tbody) {
                    tbody.lastElementChild?.scrollIntoView({ behavior: 'smooth' });
                }
                // also refresh from server in case of others
                fetchLatest();
            })
            .catch(err => console.error('Error adding expense', err));
        }
    });

    cancelEdit.addEventListener('click', resetForm);

    function resetForm() {
        editingId = null;
        form.reset();
        submitBtn.textContent = 'Add Expense';
        submitBtn.classList.remove('btn-warning');
        submitBtn.classList.add('btn-success');
        cancelEdit.classList.add('d-none');
    }

    // filtering helpers
    function updateEmptyState() {
        const emptyEl = document.getElementById('emptyMessage');
        const tableWrapper = document.querySelector('.table-responsive');
        if (expenses.length === 0) {
            if (emptyEl) emptyEl.classList.remove('d-none');
            if (tableWrapper) tableWrapper.classList.add('d-none');
        } else {
            if (emptyEl) emptyEl.classList.add('d-none');
            if (tableWrapper) tableWrapper.classList.remove('d-none');
        }
    }

    function applyFilters() {
        let filtered = expenses.slice();
        if (filterStart.value) {
            filtered = filtered.filter(e => e.date >= filterStart.value);
        }
        if (filterEnd.value) {
            filtered = filtered.filter(e => e.date <= filterEnd.value);
        }
        if (filterCategory.value) {
            filtered = filtered.filter(e => e.category === filterCategory.value);
        }
        const search = (searchText?.value || '').trim().toLowerCase();
        if (search) {
            filtered = filtered.filter(e =>
                (e.name && e.name.toLowerCase().includes(search)) ||
                (e.notes && e.notes.toLowerCase().includes(search))
            );
        }
        // perform DOM updates on next paint for smoother experience
        window.requestAnimationFrame(() => {
            renderTable(filtered);
            renderChart(filtered);
            updateTotal(filtered);
            updateEmptyState();
        });
    }

    function updateTotal(data = expenses) {
        const total = data.reduce((sum, e) => sum + e.amount, 0);
        if (totalBadge) {
            totalBadge.textContent = `₹${total.toFixed(2)}`;
        }
        const totalFooter = document.getElementById('totalBadgeFooter');
        if (totalFooter) {
            totalFooter.textContent = `₹${total.toFixed(2)}`;
        }
        const countBadge = document.getElementById('countBadge');
        if (countBadge) {
            countBadge.textContent = data.length;
        }
        const statCount = document.getElementById('statCount');
        if (statCount) {
            statCount.textContent = data.length;
        }
        // additional stats
        const amounts = data.map(e => e.amount);
        const avgBadge = document.getElementById('statAvg');
        const maxBadge = document.getElementById('statMax');
        const minBadge = document.getElementById('statMin');
        if (avgBadge) {
            const avg = amounts.length ? amounts.reduce((a,b)=>a+b,0)/amounts.length : 0;
            avgBadge.textContent = `₹${avg.toFixed(2)}`;
        }
        if (maxBadge) {
            const max = amounts.length ? Math.max(...amounts) : 0;
            maxBadge.textContent = `₹${max.toFixed(2)}`;
        }
        if (minBadge) {
            const min = amounts.length ? Math.min(...amounts) : 0;
            minBadge.textContent = `₹${min.toFixed(2)}`;
        }
    }

    function onShowNotes(evt) {
        const tr = evt.target.closest('tr');
        if (!tr) return;
        let notes = tr.dataset.notes || '';
        notes = notes.trim();
        // treat lone dash or placeholder as empty
        if (notes === '-' || notes === '—') notes = '';
        modalNotesContent.textContent = notes || 'No notes available.';
        if (noteModal) noteModal.show();
    }

    function exportCsv() {
        const header = ['Date','Category','Description','Amount','Notes'];
        const rows = expenses.map(e => [e.date,e.category || '',e.name,e.amount,e.notes || '']);
        let csv = header.join(',') + '\n';
        rows.forEach(r => { csv += r.map(v=>`"${v}"`).join(',') + '\n'; });
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'expenses.csv';
        a.click();
        URL.revokeObjectURL(url);
    }

    filterStart.addEventListener('change', applyFilters);
    filterEnd.addEventListener('change', applyFilters);
    filterCategory.addEventListener('change', applyFilters);
    exportCsvBtn.addEventListener('click', exportCsv);
    if (searchText) {
        searchText.addEventListener('input', () => {
            // debounce-like behaviour via rAF inside applyFilters
            applyFilters();
        });
    }

    function applyQuickRange(range) {
        const today = new Date();
        const toIso = d => d.toISOString().slice(0, 10);
        if (range === 'all') {
            filterStart.value = '';
            filterEnd.value = '';
        } else if (range === 'today') {
            const iso = toIso(today);
            filterStart.value = iso;
            filterEnd.value = iso;
        } else if (range === 'week') {
            const start = new Date(today);
            const day = start.getDay() || 7; // make Monday start if needed
            start.setDate(start.getDate() - (day - 1));
            filterStart.value = toIso(start);
            filterEnd.value = toIso(today);
        } else if (range === 'month') {
            const start = new Date(today.getFullYear(), today.getMonth(), 1);
            filterStart.value = toIso(start);
            filterEnd.value = toIso(today);
        }
        applyFilters();
    }

    quickFilterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const range = btn.dataset.range;
            applyQuickRange(range);
        });
    });

    // auto-poll new data every 10 seconds
    let _lastFetchHash = '';
    function fetchLatest() {
        fetch('/api/expenses')
          .then(r => r.json())
          .then(data => {
              // compute a simple hash (json string sorted by id) to detect changes
              const sorted = data.slice().sort((a,b)=>a.id-b.id);
              const hash = JSON.stringify(sorted.map(e=>[e.id,e.date,e.amount,e.category,e.name,e.notes]));
              if (hash === _lastFetchHash) {
                  // no change -> skip expensive re-render
                  return;
              }
              _lastFetchHash = hash;
              // merge incoming items with existing array to avoid duplicates
              const byId = new Map();
              expenses.forEach(e => byId.set(e.id, e));
              data.forEach(e => byId.set(e.id, e));
              expenses = Array.from(byId.values()).sort((a,b)=>a.id - b.id);
              applyFilters();
              if (lastUpdatedLabel) {
                  const now = new Date();
                  lastUpdatedLabel.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              }
          })
          .catch(err => console.error('fetchLatest error', err));
    }
    // start polling for new expenses
    const POLL_MS = 10000;
    let pollId = setInterval(fetchLatest, POLL_MS);
    // pause polling when page/tab is not visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            clearInterval(pollId);
        } else {
            pollId = setInterval(fetchLatest, POLL_MS);
            // immediately refresh when returning
            fetchLatest();
        }
    });

    // initialization
    if (expensesTable) {
        loadInitialExpenses();
        // attach a single listener to tbody for edit/delete/notes
        const tbody = expensesTable.querySelector('tbody');
        if (tbody) {
            tbody.addEventListener('click', function(evt) {
                if (evt.target.closest('.edit-btn')) {
                    onEdit(evt);
                } else if (evt.target.closest('.delete-btn')) {
                    onDelete(evt);
                } else if (evt.target.closest('.note-btn')) {
                    onShowNotes(evt);
                } else {
                    // click on row itself; if it carries notes, open modal
                    const tr = evt.target.closest('tr');
                    if (tr && tr.dataset.notes && tr.dataset.notes.trim()) {
                        onShowNotes(evt);
                    }
                }
            });
        }
        if (editingId) {
            submitBtn.textContent = 'Update Expense';
            submitBtn.classList.remove('btn-success');
            submitBtn.classList.add('btn-warning');
            cancelEdit.classList.remove('d-none');
        }
        updateTotal();
        renderChart();
        updateEmptyState();
        // old binding functions no longer needed
        // bindTableActions();
        // bindNoteButtons();
    }
});