
/*
    Place the flash message box fixed at the
    top of the window when the url contains a hash
 */

(function() {
  var Messages, hasHash,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  hasHash = function() {
    var hash;
    hash = window.location.hash.split("#")[1];
    return (hash != null) && hash.length > 0;
  };

  Messages = (function() {
    function Messages(el) {
      this.hasVisibleMessages = bind(this.hasVisibleMessages, this);
      this.hideMessage = bind(this.hideMessage, this);
      this.showAllCloseButtons = bind(this.showAllCloseButtons, this);
      this.placeMessages = bind(this.placeMessages, this);
      this.el = el;
      this.setUp();
    }

    Messages.prototype.setUp = function() {
      this.placeMessages();
      this.showAllCloseButtons();
      return Array.from(this.el.querySelectorAll('.js-messages-close-button')).forEach((function(_this) {
        return function(elm) {
          return elm.addEventListener('click', _this.hideMessage);
        };
      })(this));
    };

    Messages.prototype.placeMessages = function() {
      if (!hasHash()) {
        return;
      }
      return this.el.classList.add('is-fixed');
    };

    Messages.prototype.showAllCloseButtons = function() {
      if (!hasHash()) {
        return;
      }
      return Array.from(this.el.querySelectorAll('.js-messages-close')).forEach(function(elm) {
        return elm.style.display = 'block';
      });
    };

    Messages.prototype.hideMessage = function(e) {
      e.preventDefault();
      e.stopPropagation();
      e.currentTarget.closest('.js-messages-set').style.display = 'none';
      if (!this.hasVisibleMessages()) {
        this.el.style.display = 'none';
        this.el.classList.remove('is-fixed');
      }
    };

    Messages.prototype.hasVisibleMessages = function() {
      return Array.from(this.el.querySelectorAll('.js-messages-set')).filter(function(elm) {
        return elm.style.display !== 'none';
      }).length > 0;
    };

    return Messages;

  })();

  stModules.messages = function(elms) {
    return Array.from(elms).map(function(elm) {
      return new Messages(elm);
    });
  };

  stModules.Messages = Messages;

}).call(this);
