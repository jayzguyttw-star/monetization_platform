window.addEventListener('load', function(){
  setTimeout(function(){
    var nodes = document.querySelectorAll('.goog-te-banner-frame, .goog-te-gadget');
    nodes.forEach(function(n){ n.style.display='none'; });
  }, 700);
});
