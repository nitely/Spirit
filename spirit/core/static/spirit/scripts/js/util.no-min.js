"use strict";

(function () {
  /*
    A bunch of generic functions, this are used by other plugins.
  */
  stModules.utils = {
    format: function format(str, kwargs) {
      var key, value;

      for (key in kwargs) {
        value = kwargs[key];
        str = str.replace("{".concat(key, "}"), String(value));
      }

      return str;
    },
    isHidden: function isHidden(elms) {
      return Array.from(elms).filter(function (elm) {
        return elm.style.display !== 'none';
      }).length === 0;
    }
  };
}).call(void 0);