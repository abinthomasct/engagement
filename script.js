(function () {
  "use strict";

  // Mark page as JS-enabled so reveal animations activate. Without JS,
  // content stays visible via the default (non-.js-enabled) styles.
  document.documentElement.classList.add("js-enabled");

  // ===== Countdown =====
  var target = new Date("2026-08-08T12:00:00+05:30").getTime();
  var grid = document.getElementById("countdown");
  var done = document.getElementById("countdown-done");
  var els = {
    days: document.querySelector("[data-days]"),
    hours: document.querySelector("[data-hours]"),
    minutes: document.querySelector("[data-minutes]"),
    seconds: document.querySelector("[data-seconds]"),
  };

  function pad(n) {
    return n < 10 ? "0" + n : "" + n;
  }

  function tick() {
    var diff = target - Date.now();

    if (diff <= 0) {
      if (grid) grid.hidden = true;
      if (done) done.hidden = false;
      clearInterval(timer);
      return;
    }

    var s = Math.floor(diff / 1000);
    var days = Math.floor(s / 86400);
    var hours = Math.floor((s % 86400) / 3600);
    var minutes = Math.floor((s % 3600) / 60);
    var seconds = s % 60;

    if (els.days) els.days.textContent = days;
    if (els.hours) els.hours.textContent = pad(hours);
    if (els.minutes) els.minutes.textContent = pad(minutes);
    if (els.seconds) els.seconds.textContent = pad(seconds);
  }

  tick();
  var timer = setInterval(tick, 1000);

  // ===== Scroll reveal =====
  var revealables = document.querySelectorAll(".reveal");

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    revealables.forEach(function (el) {
      observer.observe(el);
    });

    // Safety net: ensure nothing stays hidden if the observer never fires.
    setTimeout(function () {
      revealables.forEach(function (el) {
        el.classList.add("is-visible");
      });
    }, 2500);
  } else {
    revealables.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  // ===== Floating petals =====
  var petalsWrap = document.querySelector(".petals");
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (petalsWrap && !reduceMotion) {
    var COUNT = 12;
    for (var i = 0; i < COUNT; i++) {
      var petal = document.createElement("span");
      var size = 6 + Math.random() * 10;
      petal.style.left = Math.random() * 100 + "vw";
      petal.style.width = size + "px";
      petal.style.height = size + "px";
      petal.style.animationDuration = 9 + Math.random() * 9 + "s";
      petal.style.animationDelay = Math.random() * 10 + "s";
      petal.style.opacity = 0.35 + Math.random() * 0.35;
      petalsWrap.appendChild(petal);
    }
  }
})();
