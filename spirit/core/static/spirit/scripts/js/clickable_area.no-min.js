
/*
  Makes a parent element clickable,
  based on a child anchor element
 */

(function() {
  var defaults, styles;

  defaults = {
    areaClass: '.js-clickable-area',
    areaTargetClass: '.js-clickable-area-target',
    targetColor: 'blue'
  };

  styles = function(opts) {
    return opts.areaClass + ":hover " + opts.areaTargetClass + " {\n  color: " + opts.targetColor + ";\n}\n" + opts.areaClass + " {\n  cursor: pointer;\n}";
  };

  stModules.clickableArea = function(opts) {
    var elms;
    opts = Object.assign({}, defaults, opts);
    document.head.insertAdjacentHTML("beforeend", "<style>" + (styles(opts)) + "</style>");
    elms = document.querySelectorAll(opts.areaClass);
    Array.from(elms).forEach(function(elm) {
      var anchor, url;
      anchor = elm.querySelector(opts.areaTargetClass);
      if ((anchor != null ? anchor.href : void 0) == null) {
        console.log('Anchor not found; skipping');
        return;
      }
      url = anchor.href;
      elm.addEventListener('click', (function(_this) {
        return function(e) {
          e.preventDefault();
          e.stopPropagation();
          return window.location.href = url;
        };
      })(this));
    });
  };

}).call(this);
