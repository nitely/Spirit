
/*
    Place the flash message box fixed at the
    top of the window when the url contains a hash
 */

(function() {
  var $, Messages,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  Messages = (function() {
    function Messages(el) {
      this.hasVisibleMessages = bind(this.hasVisibleMessages, this);
      this.hideMessage = bind(this.hideMessage, this);
      this.showAllCloseButtons = bind(this.showAllCloseButtons, this);
      this.placeMessages = bind(this.placeMessages, this);
      this.el = $(el);
      this.allCloseButtons = this.el.find('.js-messages-close-button');
      this.setUp();
    }

    Messages.prototype.setUp = function() {
      this.placeMessages();
      this.showAllCloseButtons();
      this.allCloseButtons.on('click', this.hideMessage);
      return this.allCloseButtons.on('click', this.stopClick);
    };

    Messages.prototype.placeMessages = function() {
      if (!this.hasHash()) {
        return;
      }
      return this.el.addClass('is-fixed');
    };

    Messages.prototype.showAllCloseButtons = function() {
      if (!this.hasHash()) {
        return;
      }
      return this.el.find('.js-messages-close').show();
    };

    Messages.prototype.hideMessage = function(e) {
      $(e.currentTarget).closest('.js-messages-set').hide();
      if (!this.hasVisibleMessages()) {
        this.el.hide();
        this.el.removeClass('is-fixed');
      }
    };

    Messages.prototype.hasVisibleMessages = function() {
      return this.el.find('.js-messages-set').is(":visible");
    };

    Messages.prototype.stopClick = function(e) {
      e.preventDefault();
      e.stopPropagation();
    };

    Messages.prototype.hasHash = function() {
      var hash;
      hash = window.location.hash.split("#")[1];
      return (hash != null) && hash.length > 0;
    };

    return Messages;

  })();

  $.fn.extend({
    messages: function() {
      return this.each(function() {
        if (!$(this).data('plugin_messages')) {
          return $(this).data('plugin_messages', new Messages(this));
        }
      });
    }
  });

  $.fn.messages.Messages = Messages;

}).call(this);
