
/*
    Social share popup
 */

(function() {
  var $, SocialShare,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  SocialShare = (function() {
    function SocialShare(el) {
      this.closeDialog = bind(this.closeDialog, this);
      this.showDialog = bind(this.showDialog, this);
      this.el = $(el);
      this.dialog = $(this.el.data("dialog"));
      this.setUp();
    }

    SocialShare.prototype.setUp = function() {
      var $shareClose, $shareInput;
      this.el.on('click', this.showDialog);
      this.el.on('click', this.stopClick);
      $shareClose = this.dialog.find('.share-close');
      $shareClose.on('click', this.closeDialog);
      $shareClose.on('click', this.stopClick);
      $shareInput = this.dialog.find('.share-url');
      $shareInput.on('focus', this.select);
      return $shareInput.on('mouseup', this.stopClick);
    };

    SocialShare.prototype.showDialog = function() {
      $('.share').hide();
      this.dialog.show();
    };

    SocialShare.prototype.closeDialog = function() {
      this.dialog.hide();
    };

    SocialShare.prototype.select = function() {
      $(this).select();
    };

    SocialShare.prototype.stopClick = function(e) {
      e.preventDefault();
      e.stopPropagation();
    };

    return SocialShare;

  })();

  $.fn.extend({
    social_share: function() {
      return this.each(function() {
        if (!$(this).data('plugin_social_share')) {
          return $(this).data('plugin_social_share', new SocialShare(this));
        }
      });
    }
  });

  $.fn.social_share.SocialShare = SocialShare;

}).call(this);
