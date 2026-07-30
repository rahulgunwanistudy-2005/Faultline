(() => {
  const root = document.getElementById('judge-root');
  const total = 30000;
  const starts = [0, 3000, 8000, 14000, 21000, 25000, 28000];
  const captions = [
    'She did everything right. Over half still failed.',
    'Scores show who is wrong. Faultline finds the procedure causing it.',
    'This class is not one problem. It is four different next moves.',
    'Every candidate procedure is executed against the actual worksheet.',
    'Now it locks an answer before the held-out work can be revealed.',
    'The signed reveal returns the separately stored answer.',
    'When evidence is split, ask the questions that buy the most information.'
  ];
  let elapsed = 0;
  let playing = true;
  let started = performance.now();
  let data = window.__FAULTLINE_DEMO__;
  let proofPrediction = null;
  let proofReveal = null;
  let proofError = '';
  let predictionStarted = false;
  let revealStarted = false;

  const esc = value => String(value).replace(/[&<>"']/g, match => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[match]));
  const svg = (path, size = 16) => `<span class="static-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="${size}" height="${size}">${path}</svg></span>`;
  const play = svg('<path d="m6 3 14 9-14 9z"/>');
  const pause = svg('<path d="M8 4v16M16 4v16"/>');
  const restart = svg('<path d="M3 12a9 9 0 1 0 3-6.7M3 4v6h6"/>');
  const skip = svg('<path d="m5 4 10 8-10 8V4ZM19 5v14"/>');
  const check = svg('<path d="m5 12 4 4L19 6"/>', 12);
  const lock = svg('<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>', 12);
  const eye = svg('<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/>', 15);
  const chevron = svg('<path d="m9 18 6-6-6-6"/>');
  const frac = value => {
    const parts = String(value ?? '—').split('/');
    return `<span class="judge-fraction"><span>${esc(parts[0])}</span><i></i><span>${esc(parts[1] || '')}</span></span>`;
  };
  const stageFor = value => {
    let stage = 0;
    starts.forEach((point, index) => { if (value >= point) stage = index; });
    return stage;
  };
  const brand = () => '<a href="/" class="judge-brand"><span><i></i><i></i><i></i></span>Faultline</a>';

  async function ensurePrediction() {
    if (predictionStarted) return;
    predictionStarted = true;
    try {
      const response = await fetch('/v1/students/bea/held-out-prediction', {method: 'POST'});
      const payload = await response.json();
      if (!response.ok || payload.state !== 'locked') throw new Error(payload.detail || payload.reason || 'Prediction unavailable');
      proofPrediction = payload;
    } catch (error) {
      proofError = error.message || 'Prediction service unavailable';
    }
    render();
  }

  async function ensureReveal() {
    if (revealStarted || !proofPrediction) return;
    revealStarted = true;
    try {
      const response = await fetch('/v1/students/bea/held-out-reveal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({proof_token: proofPrediction.proof_token})
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Reveal unavailable');
      proofReveal = payload;
    } catch (error) {
      proofError = error.message || 'Reveal service unavailable';
    }
    render();
  }

  function hook() {
    return '<section class="judge-hook"><div class="judge-stack"><i></i><i></i><i></i></div><div><small>A TEACHER’S FRIDAY NIGHT</small><blockquote>“During the lessons they all seem to get it, but test day comes and most of them fail.”</blockquote><p>The in-lesson signal looked right. The procedure underneath was not.</p></div></section>';
  }

  function upload() {
    return '<section class="judge-upload-stage"><div class="judge-paper"><span>1/2 + 1/3</span><b>2/5</b><em>Bea · page 04</em><div class="judge-scan"></div></div><div class="judge-upload-copy"><span class="judge-kicker">VERIFIED DEMO FIXTURE</span><h2>Intermediate work is the signal.</h2><p>12 synthetic students. 84 visible answers. Every reading carries its own confidence.</p><div class="judge-process"><span class="done">' + check + ' visible work loaded</span><span class="done">' + check + ' held-out answers omitted</span><span class="active"><i></i> executing hypotheses</span></div></div></section>';
  }

  function map() {
    const lanes = data.lanes.filter(lane => lane.count);
    return `<section class="judge-map-stage"><header><div><small>PERIOD 3 · FRACTIONS EXIT TICKET</small><h2>One score hid four different problems.</h2></div><span>${data.summary.students} students</span></header><div class="judge-map-line"><span>class score</span><svg viewBox="0 0 900 100" preserveAspectRatio="none"><path d="M10 50 C155 50 180 50 260 50"></path>${lanes.map((lane, index) => `<path class="b-${index}" d="M260 50 C380 50 410 ${10 + index * 26} 540 ${10 + index * 26} S760 ${10 + index * 26} 890 ${10 + index * 26}"></path>`).join('')}</svg></div><div class="judge-lanes">${lanes.map((lane, index) => `<article class="lane-${index}"><strong>${lane.count}</strong><div><small>${esc(lane.kicker)}</small><h3>${esc(lane.label)}</h3></div></article>`).join('')}</div></section>`;
  }

  function evidence(showPrediction = false, showReveal = false) {
    const student = data.students.find(item => item.student_id === 'bea');
    const replay = `<div class="judge-replay"><header><span>Problem</span><span>Observed</span><span>Procedure predicts</span><span>Fit</span></header>${student.observations.slice(0, 5).map(observation => `<div><strong>${esc(observation.expression)}</strong>${frac(observation.observed)}${frac(observation.predicted)}<span class="judge-match">${check} exact</span></div>`).join('')}</div>`;
    const predicted = proofPrediction?.predicted_answer || 'locking…';
    const actual = proofReveal?.actual_answer || 'revealing…';
    const revealBadge = proofReveal ? `${check} ${proofReveal.matched ? 'exact match' : 'does not match'}` : `${lock} signed reveal pending`;
    const proof = `<div class="judge-proof ${proofReveal ? 'is-revealed' : ''}"><div><small>UNSEEN PROBLEM</small><strong>${esc(student.held_out.problem.expression)}</strong></div>${chevron}<div class="judge-prediction"><small>FAULTLINE LOCKS</small>${frac(predicted)}<span>${lock} signed prediction token</span></div>${showReveal ? `${chevron}<div class="judge-actual"><small>HELD-OUT WORK</small>${frac(actual)}<span>${revealBadge}</span></div>` : ''}</div>`;
    const error = proofError ? `<div class="judge-method-note">${eye} ${esc(proofError)}; no answer is fabricated.</div>` : `<div class="judge-method-note">${eye} The initial class payload contains no held-out answer.</div>`;
    return `<section class="judge-evidence-stage"><div class="judge-evidence-title"><span class="judge-avatar">B</span><div><small>${student.diagnosis.posterior_percent}% POSTERIOR · ${student.diagnosis.reproduction}% REPRODUCED</small><h2>${esc(student.diagnosis.label)}</h2><p>${esc(student.diagnosis.description)}</p></div></div>${showPrediction ? proof : replay}${error}</section>`;
  }

  function tomorrow() {
    const student = data.students.find(item => item.student_id === 'jai');
    return `<section class="judge-tomorrow-stage"><div><small>FAULTLINE REFUSES TO GUESS</small><h2>Evidence split?<br>Buy the most information.</h2><p>Jai’s handwriting confidence is too low for a named diagnosis. These questions separate the surviving procedures in under four minutes.</p></div><div class="judge-question-list">${student.diagnostic_items.map((question, index) => `<article><span>0${index + 1}</span><strong>${esc(question.expression)}</strong><small>${Number(question.information_gain).toFixed(2)} bits expected</small></article>`).join('')}</div></section>`;
  }

  function resetProof() {
    proofPrediction = null;
    proofReveal = null;
    proofError = '';
    predictionStarted = false;
    revealStarted = false;
  }

  function render() {
    const stage = stageFor(elapsed);
    if (stage >= 4) ensurePrediction();
    if (stage >= 5) ensureReveal();
    const views = [hook, upload, map, () => evidence(), () => evidence(true), () => evidence(true, true), tomorrow];
    root.innerHTML = `<main class="judge-shell"><header class="judge-topbar">${brand()}<div><span class="judge-demo-badge">SYNTHETIC DEMO</span><a href="/" class="judge-skip">Skip to live app ${skip}</a></div></header><div class="judge-viewport">${views[stage]()}</div><div class="judge-caption"><span>${String(stage + 1).padStart(2, '0')}</span><p>${captions[stage]}</p></div><footer class="judge-controls"><button data-act="toggle" aria-label="${playing ? 'Pause Judge Mode' : 'Play Judge Mode'}">${playing ? pause : play}</button><button data-act="restart" aria-label="Restart Judge Mode">${restart}</button><div class="judge-timeline" aria-hidden="true"><i style="width:${Math.min(elapsed / total * 100, 100)}%"></i>${starts.map(point => `<b class="${elapsed >= point ? 'passed' : ''}" style="left:${point / total * 100}%"></b>`).join('')}</div><time>${String(Math.floor(elapsed / 1000)).padStart(2, '0')} / 30</time>${!playing && elapsed >= total ? '<a href="/" class="judge-live-link">Open live app →</a>' : ''}</footer></main>`;
    root.querySelector('[data-act="toggle"]').onclick = () => {
      playing = !playing;
      if (playing) started = performance.now() - elapsed;
      render();
    };
    root.querySelector('[data-act="restart"]').onclick = () => {
      elapsed = 0;
      playing = true;
      started = performance.now();
      resetProof();
      render();
    };
  }

  function tick() {
    if (!playing) return;
    elapsed = Math.min(performance.now() - started, total);
    if (elapsed >= total) playing = false;
    render();
  }

  render();
  window.setInterval(tick, 100);
})();
