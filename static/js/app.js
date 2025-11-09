window.addEventListener('load', function(){
  setTimeout(function(){
    var nodes = document.querySelectorAll('.goog-te-banner-frame, .goog-te-gadget');
    nodes.forEach(function(n){ n.style.display='none'; });
  }, 700);
});
// --- Persistent Branding Header ---
(function(){
  function saveHeader(){
    var hdr = document.querySelector('.platform-header');
    if (hdr) {
      try { localStorage.setItem('brandHeaderHTML', hdr.outerHTML); } catch(e){}
    }
  }

  function injectHeader(){
    var exists = document.querySelector('.platform-header');
    if (exists) return;

    var html = null;
    try { html = localStorage.getItem('brandHeaderHTML'); } catch(e){ html = null; }
    if (!html) return;

    var container = document.createElement('div');
    container.innerHTML = html.trim();

    var headerEl = container.firstElementChild;
    if (!headerEl) return;

    var target = document.querySelector('.card') || document.querySelector('.wrap');
    if (target) {
      target.insertBefore(headerEl, target.firstChild);
    } else {
      document.body.insertBefore(headerEl, document.body.firstChild);
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    saveHeader();
    injectHeader();
  });
})();
// --- End Persistent Branding Header ---
