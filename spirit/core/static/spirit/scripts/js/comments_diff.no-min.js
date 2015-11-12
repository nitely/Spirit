
/*
    HTML diff for the comment history
    requires htmldiff
 */

(function() {
  var $;

  $ = jQuery;

  $.fn.extend({
    comment_diff: function() {
      var curr, prev;
      prev = null;
      curr = null;
      return this.each(function() {
        var diff;
        curr = $(this).html();
        if (prev != null) {
          diff = htmldiff(prev, curr);
          $(this).html(diff);
        }
        return prev = curr;
      });
    }
  });

}).call(this);
