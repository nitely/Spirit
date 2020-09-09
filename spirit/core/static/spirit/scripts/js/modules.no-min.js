
/*
    Simple module system
 */

(function() {
  window.stModules = {};

  if (typeof global !== "undefined" && global !== null) {
    global.stModules = window.stModules;
  }

}).call(this);
