/* 공명 소개 — 공통 동작 */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 스테이션 링크 ---------- */
  var stationHref =
    location.protocol === "file:"
      ? "../공명스테이션_예시.html"
      : "station.html"; /* GitHub Pages / 로컬: 소개와 같은 폴더 */
  document.querySelectorAll("[data-station]").forEach(function (a) {
    a.setAttribute("href", stationHref);
  });

  /* ---------- 목차 생성 + 현재 위치 (섹션 1개 이상이면 항상) ---------- */
  var toc = document.getElementById("toc");
  var secs = Array.prototype.slice.call(document.querySelectorAll(".sec[data-toc][id]"));
  var links = [];
  if (toc && secs.length >= 1) {
    var ol = toc.querySelector("ol");
    if (ol) {
      secs.forEach(function (sec) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#" + sec.id;
        a.textContent = sec.getAttribute("data-toc");
        li.appendChild(a);
        ol.appendChild(li);
        links.push(a);
      });
      toc.classList.add("ready");

      var ticking = false;
      var sync = function () {
        ticking = false;
        var y = window.scrollY + 140;
        var idx = 0;
        for (var i = 0; i < secs.length; i++) {
          if (secs[i].offsetTop <= y) idx = i;
        }
        links.forEach(function (a, i) {
          if (i === idx) a.classList.add("active");
          else a.classList.remove("active");
        });
      };
      window.addEventListener("scroll", function () {
        if (!ticking) { ticking = true; requestAnimationFrame(sync); }
      }, { passive: true });
      sync();
    }
  }

  /* ---------- 스크롤 등장 (실패해도 본문은 보이게) ---------- */
  var revealTargets = document.querySelectorAll(".sec, .door, .home-sec, .home-tail");
  revealTargets.forEach(function (t) { t.classList.add("reveal"); });
  if (!reduce && "IntersectionObserver" in window && revealTargets.length) {
    document.documentElement.classList.add("js-motion");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -4% 0px", threshold: 0.01 });
    revealTargets.forEach(function (t) { io.observe(t); });
    /* 이미 화면에 있는 요소 / 옵저버 누락 대비 */
    requestAnimationFrame(function () {
      revealTargets.forEach(function (t) {
        var r = t.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) t.classList.add("in");
      });
    });
    window.setTimeout(function () {
      revealTargets.forEach(function (t) { t.classList.add("in"); });
    }, 1200);
  } else {
    revealTargets.forEach(function (t) { t.classList.add("in"); });
  }

  /* ---------- 홈: 한 줄 파동 ---------- */
  var wave = document.getElementById("wave");
  if (wave) {
    var path = wave.querySelector("path");
    var W = 1000, H = 64, MID = H / 2, N = 140;
    var amp = 0, phase = 0, raf = null;

    var draw = function (a) {
      var d = "M 0 " + MID;
      for (var i = 1; i <= N; i++) {
        var x = (W / N) * i;
        var t = i / N;
        var env = Math.sin(Math.PI * t);
        var y = MID + a * env * Math.sin(t * 9 + phase);
        d += " L " + x.toFixed(1) + " " + y.toFixed(2);
      }
      path.setAttribute("d", d);
    };

    if (reduce) {
      draw(0);
    } else {
      var tick = function () {
        phase += 0.09;
        amp *= 0.962;
        draw(amp);
        if (amp > 0.08) raf = requestAnimationFrame(tick);
        else { amp = 0; draw(0); raf = null; }
      };
      var nudge = function (power) {
        amp = Math.min(13, amp + power);
        if (!raf) raf = requestAnimationFrame(tick);
      };
      draw(0);
      var lastY = window.scrollY;
      window.addEventListener("scroll", function () {
        var dy = Math.abs(window.scrollY - lastY);
        lastY = window.scrollY;
        nudge(Math.min(4, dy * 0.12));
      }, { passive: true });
      var lastX = null;
      window.addEventListener("pointermove", function (e) {
        if (lastX === null) { lastX = e.clientX; return; }
        var dx = Math.abs(e.clientX - lastX);
        lastX = e.clientX;
        nudge(Math.min(2.2, dx * 0.035));
      }, { passive: true });
      document.querySelectorAll(".door, .nav-tabs a").forEach(function (el) {
        el.addEventListener("pointerenter", function () { nudge(3); });
      });
    }
  }

  /* ---------- 세계: 흔적 슬라이더 ---------- */
  var range = document.getElementById("traceRange");
  if (range) {
    var fill = document.getElementById("traceFill");
    var out = document.getElementById("traceOut");
    var val = document.getElementById("traceVal");
    var words = [
      [0, "아무에게도 닿지 않음"],
      [12, "거의 남지 않음"],
      [34, "몇 사람에게 남음"],
      [62, "여러 사람에게 오래"],
      [86, "널리, 오래"]
    ];
    var label = function (v) {
      var w = words[0][1];
      for (var i = 0; i < words.length; i++) if (v >= words[i][0]) w = words[i][1];
      return w;
    };
    var apply = function () {
      var v = Number(range.value);
      fill.style.width = v + "%";
      out.textContent = label(v);
      val.textContent = label(v);
    };
    range.addEventListener("input", apply);
    apply();
  }

  /* ---------- 공명: 메아리 ↔ 공명 ---------- */
  var echoStage = document.getElementById("echoStage");
  if (echoStage) {
    var echoRead = document.getElementById("echoRead");
    var readings = {
      echo: "말은 입 밖에 나왔지만 받은 사람이 없습니다. 문장은 사라진 것이 아니라 갈 곳을 잃고, 말한 사람 안에서만 다시 들립니다.",
      reso: "같은 문장이 다른 사람의 줄에 닿아, 그 줄이 함께 울립니다. 문제가 풀린 것은 아닙니다. 그 저녁이 세계 안에 있던 일이 되었습니다."
    };
    document.querySelectorAll("[data-echo]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var s = btn.getAttribute("data-echo");
        document.querySelectorAll("[data-echo]").forEach(function (b) {
          b.setAttribute("aria-pressed", String(b === btn));
        });
        echoStage.setAttribute("data-state", "none");
        window.requestAnimationFrame(function () {
          echoStage.setAttribute("data-state", s);
        });
        echoRead.textContent = readings[s];
      });
    });
  }

  /* ---------- 탭 레일 (세계선 / 오는 법 지도) ---------- */
  document.querySelectorAll("[data-rail]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll("[data-rail-tab]"));
    if (!tabs.length) return;
    var select = function (i) {
      tabs.forEach(function (tab, j) {
        var on = i === j;
        tab.setAttribute("aria-selected", String(on));
        tab.setAttribute("tabindex", on ? "0" : "-1");
        var panel = document.getElementById(tab.getAttribute("aria-controls"));
        if (panel) panel.classList.toggle("on", on);
      });
    };
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(i); });
      tab.addEventListener("keydown", function (e) {
        var k = e.key, next = null;
        if (k === "ArrowRight" || k === "ArrowDown") next = (i + 1) % tabs.length;
        if (k === "ArrowLeft" || k === "ArrowUp") next = (i - 1 + tabs.length) % tabs.length;
        if (k === "Home") next = 0;
        if (k === "End") next = tabs.length - 1;
        if (k === "Enter" || k === " ") { e.preventDefault(); select(i); return; }
        if (next !== null) { e.preventDefault(); select(next); tabs[next].focus(); }
      });
    });
    select(0);
  });

  /* ---------- 오는 법: 지도 (확대·축소·끌기) ---------- */
  document.querySelectorAll("[data-map]").forEach(function (box) {
    var svg = box.querySelector(".map-canvas");
    var view = box.querySelector(".m-view");
    var pins = Array.prototype.slice.call(box.querySelectorAll("[data-pin]"));
    if (!svg || !view || !pins.length) return;

    var vb = svg.viewBox.baseVal;
    var W = vb.width || 860, H = vb.height || 918;
    var ZS = [1, 3, 7, 14];
    var LV = ["1", "2", "3", "3"];
    var zi = 0, tx = 0, ty = 0, cur = 0;
    var zoomIn = box.querySelector('[data-map-zoom="1"]');
    var zoomOut = box.querySelector('[data-map-zoom="-1"]');
    var reset = box.querySelector("[data-map-reset]");

    var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

    var metrics = function () {
      var r = svg.getBoundingClientRect();
      if (!r.width || !r.height) return { ox: 0, oy: 0, vw: W, vh: H, k: 1 };
      var k = Math.max(r.width / W, r.height / H);
      var vw = r.width / k, vh = r.height / k;
      return { ox: (W - vw) / 2, oy: (H - vh) / 2, vw: vw, vh: vh, k: k };
    };

    var apply = function () {
      var z = ZS[zi], m = metrics();
      tx = clamp(tx, m.ox + m.vw - W * z, m.ox);
      ty = clamp(ty, m.oy + m.vh - H * z, m.oy);
      view.setAttribute("transform", "translate(" + tx.toFixed(1) + " " + ty.toFixed(1) + ") scale(" + z + ")");
      svg.setAttribute("data-z", LV[zi]);
      svg.style.setProperty("--mz", String(z));
      var inv = (1 / z).toFixed(4);
      pins.forEach(function (pin) {
        pin.setAttribute("transform", "translate(" + pin.getAttribute("data-x") + " " +
          pin.getAttribute("data-y") + ") scale(" + inv + ")");
      });
      if (zoomIn) zoomIn.disabled = zi === ZS.length - 1;
      if (zoomOut) zoomOut.disabled = zi === 0;
    };

    var zoomTo = function (ni, cx, cy) {
      var z0 = ZS[zi], m = metrics();
      var mx = m.ox + m.vw / 2, my = m.oy + m.vh / 2;
      if (cx === undefined) { cx = (mx - tx) / z0; cy = (my - ty) / z0; }
      zi = clamp(ni, 0, ZS.length - 1);
      var z = ZS[zi];
      tx = mx - cx * z;
      ty = my - cy * z;
      apply();
    };

    var card = document.getElementById("mapCard");
    var cardBody = document.getElementById("mapCardBody");
    var esc = function (t) {
      return String(t == null ? "" : t).replace(/[&<>"]/g, function (ch) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
      });
    };
    var fillCard = function (pin) {
      if (!card || !cardBody) return;
      card.hidden = false;
      cardBody.innerHTML =
        "<h4>" + esc(pin.getAttribute("data-name")) + "</h4>" +
        "<p class='map-where'>" + esc(pin.getAttribute("data-addr")) + "</p>" +
        "<dl><div><dt>여는 시간</dt><dd>" + esc(pin.getAttribute("data-hours")) + "</dd></div>" +
        "<div><dt>자리</dt><dd>" + esc(pin.getAttribute("data-seat")) + "</dd></div></dl>";
    };
    var markList = function (id) {
      var box = document.querySelector(".place-scroll");
      document.querySelectorAll("#placeList [data-place]").forEach(function (btn) {
        var on = btn.getAttribute("data-place") === id;
        btn.classList.toggle("on", on);
        if (!on || !box) return;
        var li = btn.closest("li");
        if (!li || li.hidden) return;
        var br = btn.getBoundingClientRect();
        var cr = box.getBoundingClientRect();
        if (br.top < cr.top) box.scrollTop -= cr.top - br.top;
        else if (br.bottom > cr.bottom) box.scrollTop += br.bottom - cr.bottom;
      });
    };
    var select = function (i, fly) {
      cur = i;
      pins.forEach(function (pin, j) {
        var on = i === j;
        pin.setAttribute("aria-selected", String(on));
        pin.setAttribute("tabindex", on ? "0" : "-1");
      });
      pins[i].parentNode.appendChild(pins[i]);
      fillCard(pins[i]);
      markList(pins[i].getAttribute("data-id"));
      if (fly) {
        zoomTo(Math.max(zi, 2), +pins[i].getAttribute("data-x"), +pins[i].getAttribute("data-y"));
      }
    };

    pins.forEach(function (pin, i) {
      pin.addEventListener("click", function (e) { e.stopPropagation(); select(i, true); });
      pin.addEventListener("keydown", function (e) {
        var k = e.key, next = null;
        if (k === "ArrowRight" || k === "ArrowDown") next = (i + 1) % pins.length;
        if (k === "ArrowLeft" || k === "ArrowUp") next = (i - 1 + pins.length) % pins.length;
        if (k === "Home") next = 0;
        if (k === "End") next = pins.length - 1;
        if (k === "Enter" || k === " ") { e.preventDefault(); e.stopPropagation(); select(i, true); return; }
        if (next !== null) { e.preventDefault(); e.stopPropagation(); select(next, true); pins[next].focus(); }
      });
    });

    if (zoomIn) zoomIn.addEventListener("click", function () { zoomTo(zi + 1); });
    if (zoomOut) zoomOut.addEventListener("click", function () { zoomTo(zi - 1); });
    if (reset) reset.addEventListener("click", function () { zi = 0; tx = 0; ty = 0; apply(); });
    var closer = box.querySelector("[data-map-close]");
    if (closer) closer.addEventListener("click", function () { if (card) card.hidden = true; });

    svg.addEventListener("dblclick", function (e) {
      var r = svg.getBoundingClientRect(), m = metrics();
      var ux = m.ox + (e.clientX - r.left) / m.k;
      var uy = m.oy + (e.clientY - r.top) / m.k;
      zoomTo(zi + 1, (ux - tx) / ZS[zi], (uy - ty) / ZS[zi]);
    });

    var drag = null;
    svg.addEventListener("pointerdown", function (e) {
      if (e.button !== undefined && e.button !== 0) return;
      drag = { x: e.clientX, y: e.clientY, k: 1 / metrics().k, moved: false };
      svg.classList.add("dragging");
      if (svg.setPointerCapture) svg.setPointerCapture(e.pointerId);
    });
    svg.addEventListener("pointermove", function (e) {
      if (!drag) return;
      var dx = (e.clientX - drag.x) * drag.k;
      var dy = (e.clientY - drag.y) * drag.k;
      if (Math.abs(dx) + Math.abs(dy) > 3) drag.moved = true;
      drag.x = e.clientX; drag.y = e.clientY;
      tx += dx; ty += dy;
      apply();
    });
    var endDrag = function (e) {
      var moved = drag && drag.moved;
      drag = null;
      svg.classList.remove("dragging");
      if (!e || e.type !== "pointerup" || moved) return;
      var best = -1, bestD = 32;
      pins.forEach(function (pin, i) {
        var b = pin.getBoundingClientRect();
        var cx = b.left + b.width / 2;
        var cy = b.top + b.height * 0.35;
        var d = Math.hypot(e.clientX - cx, e.clientY - cy);
        if (d < bestD) { bestD = d; best = i; }
      });
      if (best >= 0) select(best, true);
    };
    svg.addEventListener("pointerup", endDrag);
    svg.addEventListener("pointercancel", function () { drag = null; svg.classList.remove("dragging"); });

    svg.setAttribute("tabindex", "0");
    pins[0].setAttribute("tabindex", "0");
    svg.addEventListener("keydown", function (e) {
      var step = 60;
      if (e.key === "+" || e.key === "=") { e.preventDefault(); zoomTo(zi + 1); return; }
      if (e.key === "-" || e.key === "_") { e.preventDefault(); zoomTo(zi - 1); return; }
      if (e.key === "ArrowLeft") { tx += step; } else if (e.key === "ArrowRight") { tx -= step; }
      else if (e.key === "ArrowUp") { ty += step; } else if (e.key === "ArrowDown") { ty -= step; }
      else return;
      e.preventDefault();
      apply();
    });

    apply();
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(apply, 120);
    });
  });


  var regionSel = document.getElementById("placeRegion");
  var citySel = document.getElementById("placeCity");
  var placeItems = document.querySelectorAll("#placeList li");
  if (regionSel && citySel && placeItems.length) {
    var refillCities = function () {
      var reg = regionSel.value;
      var seen = [];
      var html = '<option value="">전체</option>';
      Array.prototype.forEach.call(placeItems, function (li) {
        var r = li.getAttribute("data-region");
        var c = li.getAttribute("data-city");
        if (reg && r !== reg) return;
        var value = reg ? c : (r + "|" + c);
        var label = reg ? c : (r + " " + c);
        if (seen.indexOf(value) >= 0) return;
        seen.push(value);
        html += '<option value="' + value + '">' + label + "</option>";
      });
      citySel.innerHTML = html;
    };
    var applyFilter = function () {
      var reg = regionSel.value, city = citySel.value, shown = 0;
      Array.prototype.forEach.call(placeItems, function (li) {
        var key = li.getAttribute("data-region") + "|" + li.getAttribute("data-city");
        var show = (!reg || li.getAttribute("data-region") === reg) &&
          (!city || city === li.getAttribute("data-city") || city === key);
        li.hidden = !show;
        if (show) shown++;
      });
      var empty = document.getElementById("placeEmpty");
      if (empty) empty.hidden = shown !== 0;
    };
    regionSel.addEventListener("change", function () { refillCities(); applyFilter(); });
    citySel.addEventListener("change", applyFilter);
    refillCities();
    document.getElementById("placeList").addEventListener("click", function (e) {
      var btn = e.target.closest("[data-place]");
      if (!btn) return;
      var id = btn.getAttribute("data-place");
      var map = document.querySelector("[data-map]");
      if (!map) return;
      var pins = map.querySelectorAll("[data-pin]");
      for (var i = 0; i < pins.length; i++) {
        if (pins[i].getAttribute("data-id") === id) {
          pins[i].dispatchEvent(new MouseEvent("click", { bubbles: true }));
          break;
        }
      }
    });
  }

  /* ---------- 공명: 이중층 ---------- */
  var layerBox = document.getElementById("layerBox");
  if (layerBox) {
    var note = document.getElementById("layerNote");
    var state = { 1: false, 2: false };
    var notes = {
      "00": "두 층은 따로 켜집니다. 아래의 영향부터 켜 보십시오.",
      "10": "영향이 있었다고 공명 경험이 성립하지는 않습니다. 2층은 경험하는 쪽의 자기 판단이고, 그 버튼은 당사자 자리에만 있습니다.",
      "01": "발신자가 받는 사람을 몰라도 공명 경험은 일어날 수 있습니다. 책, 작품, 사상도 그렇습니다.",
      "11": "1층은 2층의 조건이자 배경이지, 2층의 객관 인증이 아닙니다. 중심에 있는 것은 2층입니다."
    };
    var sync2 = function () {
      layerBox.querySelectorAll("[data-layer]").forEach(function (el) {
        el.setAttribute("data-on", String(state[el.getAttribute("data-layer")]));
      });
      layerBox.querySelectorAll("[data-toggle]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(state[b.getAttribute("data-toggle")]));
      });
      note.textContent = notes[(state[1] ? "1" : "0") + (state[2] ? "1" : "0")];
    };
    layerBox.querySelectorAll("[data-toggle]").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.getAttribute("data-toggle");
        state[k] = !state[k];
        sync2();
      });
    });
    sync2();
  }

  /* ---------- 구원: 주석 달린 정의 ---------- */
  var defNote = document.getElementById("defNote");
  if (defNote) {
    var notesDef = {
      n1: ["세계와 무관하게 완결된 존재", "내가 나 혼자서 만들어졌고, 세계와 상관없이 이미 완성되어 있다고 보는 관점입니다. 강해 보이지만, 내 줄 위에 이미 새겨진 남의 글씨를 지우는 관점이기도 합니다."],
      n2: ["관계 속에서 형성된", "나를 이루는 것 가운데 상당 부분이 관계에서 왔다는 사실입니다. 관계가 나를 형성한다는 말이지, 나의 모든 것이 타인의 평가로 결정된다는 말은 아닙니다."],
      n3: ["그 이해에 따라", "느낌이나 깨달음에서 멈추지 않는다는 뜻입니다. 인식에서 시작하되 삶의 방향과 행동으로 이어지는 것을 중요하게 봅니다. 다만 인식과 행동이 늘 일치한다고 주장하지는 않습니다."],
      n4: ["다시 선택해 가는 과정", "한 번의 사건이 아니라 과정입니다. 평생 여러 번 다시 선택할 수 있습니다. 순간의 깨달음은 그 과정의 일부이고, 도달했는지 아닌지로 등급을 두지 않습니다."]
    };
    var marks = document.querySelectorAll("[data-note]");
    marks.forEach(function (m) {
      m.addEventListener("click", function () {
        var key = m.getAttribute("data-note");
        var on = m.getAttribute("aria-pressed") !== "true";
        marks.forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        if (on) {
          m.setAttribute("aria-pressed", "true");
          defNote.innerHTML = "";
          var strong = document.createElement("strong");
          strong.textContent = notesDef[key][0];
          var p = document.createElement("span");
          p.textContent = notesDef[key][1];
          defNote.appendChild(strong);
          defNote.appendChild(p);
        } else {
          defNote.textContent = "밑줄 친 구절을 누르면 그 부분의 뜻을 풀어 둔 설명이 나옵니다.";
        }
      });
    });
  }

  /* ---------- 선과 책임: 네 질문 ---------- */
  var caseBox = document.getElementById("caseBox");
  if (caseBox) {
    var cases = [
      {
        desc: "힘들어 보이는 사람에게 좋다고 생각한 조언을 했습니다. 그 말이 상대를 더 몰아세웠습니다.",
        a: [
          "돕고 싶었습니다. 해칠 뜻은 없었습니다.",
          "상대가 원하는지 묻지 않고 조언을 먼저 했습니다. 먼저 듣는 선택도 가능했습니다.",
          "상대는 자기 이야기가 해결해야 할 과제로 바뀌는 경험을 했습니다.",
          "상대의 말을 상대의 말로 두지 않고, 내 해결의 재료로 삼았을 수 있습니다.",
          "원하는지 물어볼 수 있었습니다. 지금 할 일은 그 말을 거두고, 다음에는 먼저 듣는 쪽에 서는 것입니다."
        ]
      },
      {
        desc: "길에서 울고 있는 사람을 스쳐 지났습니다. 바빴고, 사정은 몰랐습니다.",
        a: [
          "해칠 뜻도, 도울 뜻도 없었습니다.",
          "지나갔습니다. 멈춰 설 수도 있었지만, 멈추지 않을 자유도 있습니다.",
          "그 사람의 그 순간은 아무에게도 닿지 않았습니다.",
          "그 사람을 도구로 쓴 것은 아닙니다. 다만 그 순간의 고통을 부당하게 무시한 것인지는 따로 물을 수 있습니다.",
          "법을 어긴 것은 아닙니다. 다만 응답하지 않을 자유가 언제나 모든 책임을 면제하지는 않습니다."
        ]
      },
      {
        desc: "내 몫을 챙기려고 한 일이 우연히 다른 사람에게도 이익이 되었습니다.",
        a: [
          "다른 사람을 위한 뜻은 없었습니다.",
          "내 이익을 기준으로 선택했습니다. 다른 선택도 가능했습니다.",
          "결과적으로 두 사람 모두에게 이익이 생겼습니다.",
          "타인을 수단으로만 썼는지는 이 사례만으로 단정하지 않습니다.",
          "좋은 결과가 의도를 되돌려 선하게 만들지는 않습니다. 해치려 했는데 우연히 이익이 생긴 일을 선이라고 하지도 않습니다."
        ]
      }
    ];
    var caseDesc = document.getElementById("caseDesc");
    var cells = caseBox.querySelectorAll("[data-q]");
    var btns = caseBox.querySelectorAll("[data-case]");
    var pickCase = function (i) {
      btns.forEach(function (b) {
        b.setAttribute("aria-pressed", String(Number(b.getAttribute("data-case")) === i));
      });
      caseDesc.textContent = cases[i].desc;
      cells.forEach(function (c) {
        c.textContent = cases[i].a[Number(c.getAttribute("data-q"))];
      });
    };
    btns.forEach(function (b) {
      b.addEventListener("click", function () { pickCase(Number(b.getAttribute("data-case"))); });
    });
    pickCase(0);
  }

  /* ---------- 열어 둔 물음: 주장 필터 ---------- */
  var claims = document.getElementById("claims");
  if (claims) {
    document.querySelectorAll("[data-filter]").forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-filter");
        claims.setAttribute("data-f", f);
        document.querySelectorAll("[data-filter]").forEach(function (x) {
          x.setAttribute("aria-pressed", String(x === b));
        });
      });
    });
  }

  /* ---------- 실천: 의례 스텝 ---------- */
  var stepBox = document.getElementById("stepBox");
  if (stepBox) {
    var steps = [
      {
        t: "앉음",
        plain: "들어와 앉습니다. 문은 닫힙니다. 서두르지 않습니다. 같이 모이는 자리가 아닙니다. 한 사람이 들어가 앉습니다.",
        not: "이름을 묻지 않습니다. 신앙을 확인하지 않습니다. 성직자는 없고, 문양에 절하지 않습니다."
      },
      {
        t: "여는 말",
        say: ["오늘의 경험 하나를 말씀해 주십시오. 없어도 됩니다."],
        not: "침묵이 먼저입니다. 먼저 앉은 사람의 이름 없는 문장이 있으면 그것만 들립니다. 여는 말은 부스가 합니다. 전통의 말은 문을 닫기 전에 고를 수 있고, 고르지 않아도 됩니다."
      },
      {
        t: "오늘의 경험 하나",
        plain: "말하고 싶으면 오늘의 역 하나를 말합니다. 가족일 수도 있고, 실패한 일일 수도 있고, 아무 일도 없던 저녁일 수도 있습니다.",
        not: "말이 나오지 않으면, 말하지 않는 것도 그 시간입니다. 빈칸도 줄 위에 있습니다. 말하지 못한 경험도 덜 실재하지 않습니다."
      },
      {
        t: "듣는 쪽",
        plain: "그 하루가 그렇게 남았다는 것을, 이쪽에 한 줄 받아 둡니다. 먼저 앉은 사람이 남긴 이름 없는 한 문장이 들릴 수도 있습니다.",
        not: "고치지 않습니다. 의미를 붙이지 않습니다. 허무를 달래지 않습니다. 삶을 무가치하다고도 가치 있다고도 대신 판결하지 않습니다. 공명이 성립했는지 판정하지 않습니다. 「불을 켜세요」라고 말하지 않습니다."
      },
      {
        t: "남김",
        plain: "내 말을 다음 사람에게 남길지는 앉은 사람이 정합니다. 남기지 않으면 말은 사라져도 됩니다.",
        not: "모든 삶을 기록해야 하는 것은 아닙니다. 남김은 자랑이 아니며, 기본적 가치의 척도도 아닙니다."
      },
      {
        t: "닫는 말",
        say: ["이 자리는 여기서 닫습니다."],
        not: "구원이 완성되었다거나 허무가 끝났다고 말하지 않습니다. 한 번의 앉음이 공명을 인증하지 않습니다."
      }
    ];
    var risk = {
      t: "위험이 클 때",
      say: ["이 자리는 여기서 듣기를 멈춥니다.", "이 말은 1577-0199와 109가 듣습니다."],
      not: "스스로 해치겠다는 계획, 남을 해치겠다는 말, 당장 손이 필요한 병이 나오면 듣기를 멈춥니다. 의미로 덮고 계속 듣지 않습니다. 사람이 올 때까지 곁에 있습니다.",
      call: "1577-0199 · 109"
    };
    var dots = document.getElementById("stepDots");
    var prev = stepBox.querySelector("[data-step='prev']");
    var next = stepBox.querySelector("[data-step='next']");
    var riskBtn = stepBox.querySelector("[data-step='risk']");
    var body = document.getElementById("stepBody");
    var at = 0, onRisk = false;

    var render = function () {
      var s = onRisk ? risk : steps[at];
      body.className = "step-body" + (onRisk ? " risk" : "");
      var html = "";
      html += "<p class='step-no'>" + (onRisk ? "분기" : (at + 1) + " / " + steps.length) + "</p>";
      html += "<h4 class='step-title'>" + s.t + "</h4>";
      if (s.say) {
        html += "<div class='step-say'>";
        s.say.forEach(function (line) { html += "<p>" + line + "</p>"; });
        html += "</div>";
      }
      if (s.plain) html += "<p class='step-plain'>" + s.plain + "</p>";
      html += "<p class='step-not'><b>이때 하지 않는 일.</b> " + s.not + "</p>";
      if (s.call) html += "<p class='step-call'>" + s.call + "</p>";
      body.innerHTML = html;
      Array.prototype.forEach.call(dots.children, function (li, i) {
        li.classList.toggle("on", !onRisk && i <= at);
      });
      prev.disabled = onRisk ? false : at === 0;
      next.disabled = onRisk ? true : at === steps.length - 1;
      riskBtn.setAttribute("aria-pressed", String(onRisk));
      riskBtn.textContent = onRisk ? "자리로 돌아가기" : "위험이 클 때";
    };
    prev.addEventListener("click", function () {
      if (onRisk) { onRisk = false; } else if (at > 0) { at--; }
      render();
    });
    next.addEventListener("click", function () {
      if (!onRisk && at < steps.length - 1) { at++; render(); }
    });
    riskBtn.addEventListener("click", function () { onRisk = !onRisk; render(); });
    render();
  }

  /* ---------- 실존적 엘크 이론: 네 가지 방어 ---------- */
  var defBox = document.getElementById("defBox");
  if (defBox) {
    var defRead = document.getElementById("defRead");
    var defTexts = [
      "격리는 죽음과 무의미를 떠올리는 생각을 의식 밖으로 밀어 내는 일입니다. 그 이야기를 꺼내지 않는 것이 예의처럼 됩니다. 그래서 하루는 그 생각 없이 지나갑니다. 자각이 없어진 것은 아니고, 보지 않기로 한 것입니다.",
      "고정은 사람에게 생기는 정이 아닙니다. 자페가 말한 anchoring은, 의식을 한 점에 묶어 두는 일입니다. 신, 나라, 도덕, 가족, 해야 할 일. 그 점이 흔들리지 않으면, 삶의 무의미를 매일 마주하지 않아도 됩니다.",
      "분산은 주의를 계속 다른 곳으로 돌리는 일입니다. 소식, 오락, 일, 자극. 볼 것이 끊기지 않으면, 유한함과 무의미를 볼 틈이 없습니다. 멈추지 못하는 중독은, 이 분산이 고착된 모습으로 읽히기도 합니다.",
      "승화는 자각을 막지 않습니다. 비극을 예술이나 사상으로 바꾸어, 거리를 두고 바라보게 합니다. 무의미를 알게 된 상태는 남아 있는데, 그 자리에서 바로 무너지지는 않습니다. 자페는 이 길을 드물다고 보았습니다."
    ];
    var defBtns = defBox.querySelectorAll("[data-def]");
    var showDef = function (i) {
      defBtns.forEach(function (b) {
        b.setAttribute("aria-pressed", String(Number(b.getAttribute("data-def")) === i));
      });
      defRead.textContent = defTexts[i];
    };
    defBtns.forEach(function (b) {
      b.addEventListener("click", function () { showDef(Number(b.getAttribute("data-def"))); });
    });
    showDef(0);
  }

})();