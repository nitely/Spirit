"use strict";

(function () {
  /*
      HTML diff for the comment history
      requires modules, htmldiff
  */
  stModules.commentDiff = function (elms) {
    var curr, prev;
    prev = null;
    curr = null;
    return Array.from(elms).forEach(function (elm) {
      curr = elm.innerHTML;

      if (prev != null) {
        elm.innerHTML = htmldiff(prev, curr);
      }

      return prev = curr;
    });
  };
}).call(void 0);