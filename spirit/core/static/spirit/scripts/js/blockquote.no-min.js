
/*
    Expand blockquote instead of showing a scrollbar
 */

(function() {
  stModules.blockquoteExpand = function(elms) {
    Array.from(elms).forEach(function(elm) {
      var expand, expandButton, pos;
      if (elm.after == null) {
        return;
      }
      pos = elm.scrollTop;
      elm.scrollTop += 1;
      if (pos !== elm.scrollTop) {
        elm.scrollTop = pos;
        elm.style.overflowY = 'hidden';
        expandButton = document.createElement('a');
        expandButton.href = '#';
        expandButton.innerHTML = '<i class="fa fa-chevron-down"></i>';
        expandButton.addEventListener('click', (function(_this) {
          return function(e) {
            e.preventDefault();
            e.stopPropagation();
            elm.style.maxHeight = 'none';
            return expand.remove();
          };
        })(this));
        expand = document.createElement('div');
        expand.className = 'blockquote_expand';
        expand.appendChild(expandButton);
        return elm.after(expand);
      }
    });
  };

}).call(this);
