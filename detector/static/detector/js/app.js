(function () {
  const drop = document.getElementById('drop');
  const fileInput = document.getElementById('file');
  const preview = document.getElementById('preview');
  const idle = drop.querySelector('.drop-idle');
  const runBtn = document.getElementById('run');
  const clearBtn = document.getElementById('clear');
  const result = document.getElementById('result');
  let current = null; // File or Blob to send

  function csrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }
  function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  function setImage(blob, name) {
    current = { blob, name: name || 'upload.png' };
    if (preview.src.startsWith('blob:')) URL.revokeObjectURL(preview.src);
    preview.src = URL.createObjectURL(blob);
    preview.hidden = false; idle.hidden = true;
    runBtn.disabled = false; clearBtn.hidden = false;
    result.innerHTML = '<div class="placeholder">Ready. Press “Detect defect”.</div>';
  }
  function clearAll() {
    current = null; preview.hidden = true; idle.hidden = false;
    runBtn.disabled = true; clearBtn.hidden = true; fileInput.value = '';
    document.querySelectorAll('.sample.selected').forEach(e => e.classList.remove('selected'));
    result.innerHTML = '<div class="placeholder">The result will appear here.</div>';
  }

  async function loadFromUrl(url, name) {
    const r = await fetch(url);
    if (!r.ok) throw new Error('Could not load image');
    setImage(await r.blob(), name);
  }

  // Gallery: drag + tap-to-select
  document.querySelectorAll('.sample').forEach(img => {
    img.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/x-sample-url', img.src);
      e.dataTransfer.setData('text/x-sample-name', img.dataset.file);
      e.dataTransfer.effectAllowed = 'copy';
    });
    img.addEventListener('click', async () => {
      document.querySelectorAll('.sample.selected').forEach(e => e.classList.remove('selected'));
      img.classList.add('selected');
      await loadFromUrl(img.src, img.dataset.file);
      document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
    });
  });

  // Drop zone
  ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', async e => {
    const url = e.dataTransfer.getData('text/x-sample-url');
    if (url) {
      try { await loadFromUrl(url, e.dataTransfer.getData('text/x-sample-name')); } catch (err) { showError(err.message); }
      return;
    }
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if (f && f.type.startsWith('image/')) setImage(f, f.name);
    else showError('Please drop an image file.');
  });
  drop.addEventListener('click', () => fileInput.click());
  drop.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); } });
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) setImage(fileInput.files[0], fileInput.files[0].name); });
  clearBtn.addEventListener('click', clearAll);

  function showError(msg) { result.innerHTML = '<p class="err">' + esc(msg) + '</p>'; }

  runBtn.addEventListener('click', async () => {
    if (!current) return;
    runBtn.disabled = true;
    result.innerHTML = '<div class="spin"></div>';
    const fd = new FormData();
    fd.append('image', current.blob, current.name);
    try {
      const r = await fetch(window.PREDICT_URL, { method: 'POST', body: fd, headers: { 'X-CSRFToken': csrf() } });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || 'Prediction failed');
      render(data);
    } catch (err) { showError(err.message); }
    runBtn.disabled = false;
  });

  function render(d) {
    const bars = d.scores.slice(0, 6).map((s, i) =>
      '<div class="bar' + (i === 0 ? ' top' : '') + '"><span>' + esc(s.label) + '</span>' +
      '<div class="track"><div class="fill" data-w="' + (s.score * 100).toFixed(1) + '"></div></div>' +
      '<span>' + (s.score * 100).toFixed(1) + '%</span></div>').join('');
    result.innerHTML =
      '<div class="verdict"><div><small>Detected</small><strong>' + esc(d.label) + '</strong></div>' +
      '<div class="conf">' + (d.confidence * 100).toFixed(1) + '%</div></div>' + bars +
      (d.mode === 'demo' ? '<span class="tag">Demo mode &middot; model weights not loaded</span>' : '');
    requestAnimationFrame(() => result.querySelectorAll('.fill').forEach(f => f.style.width = f.dataset.w + '%'));
  }
})();
