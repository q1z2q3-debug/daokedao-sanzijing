(function () {
  'use strict';
  var LS = {
    get: function (k, d) { try { var v = localStorage.getItem('szj.' + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem('szj.' + k, JSON.stringify(v)); } catch (e) {} }
  };
  var secs = Array.prototype.slice.call(document.querySelectorAll('.ls'));
  var byN = {}, aux = {};
  secs.forEach(function (s) {
    var n = s.dataset.n ? +s.dataset.n : 0;
    if (n) byN[n] = s;
    else if (s.dataset.aux) aux[s.dataset.aux] = s;
  });
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
  var total = 201;
  var state = {
    n: LS.get('n', 1), zoom: LS.get('zoom', 1), night: LS.get('night', 0),
    read: LS.get('read', {}), fav: LS.get('fav', {}), y: LS.get('y', {})
  };


  /* ---------- 工具 ---------- */
  function bridge() { return (window.App && typeof window.App === 'object') ? window.App : null; }
  function toast(msg) {
    var b = bridge();
    if (b && b.toast) { try { b.toast(String(msg)); return; } catch (e) {} }
    var t = document.getElementById('__toast');
    if (!t) {
      t = document.createElement('div'); t.id = '__toast';
      t.style.cssText = 'position:fixed;left:50%;bottom:96px;transform:translateX(-50%);background:rgba(40,34,26,.9);color:#F8F3E6;font:13px/1.5 "Noto Sans SC",sans-serif;padding:8px 14px;border-radius:16px;z-index:60;transition:opacity .2s;pointer-events:none';
      document.body.appendChild(t);
    }
    t.textContent = msg; t.style.opacity = '1';
    clearTimeout(t.__tm); t.__tm = setTimeout(function () { t.style.opacity = '0'; }, 1600);
  }
  function applyZoom() {
    var b = bridge();
    var levels = [90, 100, 112, 125];
    var pct = levels[state.zoom - 1] || 100;
    if (b && b.setTextZoom) { try { b.setTextZoom(pct); } catch (e) {} }
  }
  function applyNight() {
    document.documentElement.className = state.night ? 'theme-night' : 'theme-paper';
  }

  /* ---------- 显示 ---------- */
  function show(n, keepScroll) {
    n = Math.max(1, Math.min(total, n));
    secs.forEach(function (s) { s.style.display = 'none'; });
    var page = byN[n] || byN[1];
    if (!page) return;
    page.style.display = '';
    state.n = n;
    LS.set('n', n);
    var lno = page.querySelector('.lesson-no');
    document.getElementById('nowNo').textContent = lno ? lno.textContent : ('第 ' + n + ' 课');
    var h1 = page.querySelector('h1');
    document.getElementById('nowTi').textContent = h1 ? h1.textContent : '';
    document.getElementById('pgnNum').textContent = String(n);
    document.getElementById('prev').disabled = n <= 1;
    document.getElementById('next').disabled = n >= total;
    document.getElementById('favIc').textContent = state.fav[n] ? '★' : '☆';
    document.getElementById('favIc').className = state.fav[n] ? 'ic on' : 'ic';
    if (!keepScroll) {
      var y = state.y[n];
      window.scrollTo(0, typeof y === 'number' ? y : 0);
    }
    markCurrentInToc();
  }
  function showAux(k) {
    secs.forEach(function (s) { s.style.display = 'none'; });
    var el = aux[k]; if (!el) return;
    el.style.display = '';
    var LAB = { cover: ['封面', '三字经 · 二零一课'], frontis: ['扉页', '润泽说 道可道 · 少儿启蒙国学'], guide: ['读法', '三类读法'], appendix: ['附录', '次第链条与经文对照'] };
    var lb = LAB[k] || ['', ''];
    state.n = 0;
    document.getElementById('nowNo').textContent = lb[0];
    document.getElementById('nowTi').textContent = lb[1];
    document.getElementById('pgnNum').textContent = '';
    document.getElementById('prev').disabled = true;
    document.getElementById('next').disabled = false;
    document.getElementById('favIc').textContent = '☆';
    document.getElementById('favIc').className = 'ic';
    window.scrollTo(0, 0);
    markCurrentInToc();
    closeSheets();
  }

  /* ---------- 目录抽屉 ---------- */
  var tab = 'all';
  function buildToc() {
    var body = document.getElementById('tocBody');
    var h = '';
    SEGS.forEach(function (s) {
      var items = '';
      s.sub.forEach(function (sub) {
        var li = '';
        for (var n = sub.a; n <= sub.b; n++) {
          var t = TOC[n - 1]; if (!t) continue;
          if (tab === 'read' && !state.read[n]) continue;
          if (tab === 'fav' && !state.fav[n]) continue;
          var dot = state.fav[n] ? 'fav' : (state.read[n] ? 'read' : '');
          li += '<div class="item' + (n === state.n ? ' cur' : '') + '" data-n="' + n + '">' +
                '<span class="no">' + n + '</span><span class="ti">' + t[2] + '</span>' +
                '<span class="dot ' + dot + '"></span></div>';
        }
        if (li) items += '<div class="gsub">' + sub.name + '　第 ' + sub.a + '–' + sub.b + ' 课</div>' + li;
      });
      if (items) h += '<div class="grp">' + s.name + '　' + s.key + '</div>' + items;
    });
    if (!h) h = '<div class="empty">这里还空着。</div>';
    h += '<div class="gsub">另附</div>' +
         '<div class="item" data-aux="guide"><span class="no">—</span><span class="ti">三类读法（何以为人 · 何以知世 · 如何成人）</span><span class="dot"></span></div>' +
         '<div class="item" data-aux="appendix"><span class="no">—</span><span class="ti">附录 · 次第链条与经文对照</span><span class="dot"></span></div>';
    body.innerHTML = h;
    var cnt = Object.keys(state.read).length;
    document.getElementById('progHint').textContent = '已读 ' + cnt + ' / ' + total;
    body.querySelectorAll('.item').forEach(function (it) {
      it.addEventListener('click', function () {
        if (it.dataset.aux) { showAux(it.dataset.aux); }
        else { show(+it.dataset.n); closeSheets(); }
      });
    });
  }
  function markCurrentInToc() {
    var body = document.getElementById('tocBody');
    if (!body) return;
    body.querySelectorAll('.item').forEach(function (it) {
      it.classList.toggle('cur', it.dataset.n === String(state.n));
    });
  }

  /* ---------- 抽屉开关 ---------- */
  function openSheet(id) {
    closeSheets();
    document.getElementById(id).classList.add('on');
    document.getElementById('mask').classList.add('on');
    if (id === 'drawer') buildToc();
    if (id === 'search') setTimeout(function () { document.getElementById('q').focus(); }, 260);
  }
  function closeSheets() {
    document.querySelectorAll('.sheet').forEach(function (s) { s.classList.remove('on'); });
    document.getElementById('mask').classList.remove('on');
  }
  function anySheetOpen() { return !!document.querySelector('.sheet.on'); }

  /* ---------- 检索 ---------- */
  var indexed = null;
  function index() {
    if (indexed) return indexed;
    indexed = secs.map(function (s) {
      return { n: s.dataset.n ? +s.dataset.n : 0, el: s, txt: (s.textContent || '').replace(/\s+/g, ' ') };
    });
    return indexed;
  }
  function doSearch(q) {
    var res = document.getElementById('res');
    q = q.trim();
    if (q.length < 1) { res.innerHTML = '<div class="empty">输入一个字或一句，全 201 课一起翻。</div>'; return; }
    var hits = [], rose = index();
    for (var i = 0; i < rose.length; i++) {
      var it = rose[i]; if (!it.n) continue;
      var pos = it.txt.indexOf(q);
      if (pos < 0) continue;
      var s = Math.max(0, pos - 16), e = Math.min(it.txt.length, pos + q.length + 22);
      var pre = (s > 0 ? '…' : '') + it.txt.slice(s, pos);
      var hit = it.txt.slice(pos, pos + q.length);
      var post = it.txt.slice(pos + q.length, e) + (e < it.txt.length ? '…' : '');
      hits.push('<div class="rc" data-n="' + it.n + '"><div class="t">第 ' + it.n + ' 课 · ' + (TOC[it.n - 1] ? TOC[it.n - 1][2] : '') + '</div><div class="s">' + esc(pre) + '<em>' + esc(hit) + '</em>' + esc(post) + '</div></div>');
    }
    res.innerHTML = hits.length ? hits.slice(0, 60).join('') : '<div class="empty">没有找到「' + esc(q) + '」。</div>';
    res.querySelectorAll('.rc').forEach(function (c) {
      c.addEventListener('click', function () { show(+c.dataset.n); closeSheets(); });
    });
  }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* ---------- 事件 ---------- */
  document.getElementById('btnToc').addEventListener('click', function () { openSheet('drawer'); });
  document.getElementById('mask').addEventListener('click', closeSheets);
  document.querySelectorAll('[data-close]').forEach(function (b) {
    b.addEventListener('click', function () { closeSheets(); });
  });
  document.querySelectorAll('.sh-tabs button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.sh-tabs button').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on'); tab = b.dataset.tab; buildToc();
    });
  });
  document.getElementById('prev').addEventListener('click', function () { if (state.n > 0) show(state.n - 1); });
  document.getElementById('next').addEventListener('click', function () { show(state.n + 1); });
  ['cover', 'frontis'].forEach(function (k) {
    var el = aux[k];
    if (el) { el.style.cursor = 'pointer'; el.addEventListener('click', function (e) { if (e.target.closest('a')) return; show(1); }); }
  });
  var coverNext = document.querySelector('.cv-next');
  if (coverNext) coverNext.addEventListener('click', function (e) { e.stopPropagation(); show(1); });
  document.getElementById('btnFav').addEventListener('click', function () {
    if (state.n === 0) { toast('封面页不可收藏'); return; }
    if (state.fav[state.n]) { delete state.fav[state.n]; toast('已取消收藏'); }
    else { state.fav[state.n] = 1; toast('已收藏 · 第 ' + state.n + ' 课'); }
    LS.set('fav', state.fav);
    document.getElementById('favIc').textContent = state.fav[state.n] ? '★' : '☆';
    document.getElementById('favIc').className = state.fav[state.n] ? 'ic on' : 'ic';
  });
  document.querySelectorAll('#tools button').forEach(function (b) {
    b.addEventListener('click', function () {
      var a = b.dataset.act;
      if (a === 'smaller') { state.zoom = Math.max(1, state.zoom - 1); applyZoom(); LS.set('zoom', state.zoom); toast('字号 ' + [90, 100, 112, 125][state.zoom - 1] + '%'); }
      if (a === 'bigger') { state.zoom = Math.min(4, state.zoom + 1); applyZoom(); LS.set('zoom', state.zoom); toast('字号 ' + [90, 100, 112, 125][state.zoom - 1] + '%'); }
      if (a === 'night') { state.night = state.night ? 0 : 1; applyNight(); LS.set('night', state.night); b.classList.toggle('active', !!state.night); }
      if (a === 'search') openSheet('search');
      if (a === 'top') window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
  document.getElementById('q').addEventListener('input', function (e) { doSearch(e.target.value); });

  var tm = null;
  window.addEventListener('scroll', function () {
    if (tm) return;
    tm = setTimeout(function () {
      tm = null;
      state.y[state.n] = window.scrollY; LS.set('y', state.y);
      var page = byN[state.n];
      if (page) {
        var r = page.getBoundingClientRect();
        if (window.scrollY > 200 && (r.height + r.top < window.innerHeight * 0.4 || window.scrollY > r.height - 260)) {
          if (!state.read[state.n]) { state.read[state.n] = 1; LS.set('read', state.read); }
        }
      }
    }, 200);
  }, { passive: true });

  /* 返回键：先关抽屉，再退上一课，最后交系统 */
  window.appBack = function () {
    if (anySheetOpen()) { closeSheets(); return true; }
    if (state.n > 1) { show(state.n - 1); return true; }
    return false;
  };

  /* 首屏 */
  applyNight(); applyZoom();
  if (LS.get('n')) show(state.n, true); else showAux('cover');
  if (state.night) document.querySelector('[data-act="night"]').classList.add('active');
  doSearch('');
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (a && (a.getAttribute('href') || '').indexOf('javascript:') === 0) e.preventDefault();
  });
})();
