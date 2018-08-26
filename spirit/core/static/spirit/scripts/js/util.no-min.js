
/*
  A bunch of generic functions, this are used by other plugins.
 */

(function() {
  stModules.utils = {
    format: function(str, kwargs) {
      var key, value;
      for (key in kwargs) {
        value = kwargs[key];
        str = str.replace("{" + key + "}", String(value));
      }
      return str;
    },
    isHidden: function(elms) {
      return Array.from(elms).filter(function(elm) {
        return elm.style.display !== 'none';
      }).length === 0;
    }
  };

}).call(this);
