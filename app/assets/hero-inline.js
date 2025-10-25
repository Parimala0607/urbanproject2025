document.addEventListener("DOMContentLoaded", function () {
  const v = document.getElementById("hero-bg") || document.querySelector("video.hero-video");
  if (!v) return;
  v.setAttribute("playsinline", "");
  v.setAttribute("webkit-playsinline", "");
  const p = v.play && v.play();
  if (p && typeof p.catch === "function") p.catch(() => {});
});
