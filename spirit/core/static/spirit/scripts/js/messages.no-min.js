"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Place the flash message box fixed at the
      top of the window when the url contains a hash
  */
  var Messages, hasHash, utils;
  utils = stModules.utils;

  hasHash = function hasHash() {
    var hash;
    hash = window.location.hash.split("#")[1];
    return hash != null && hash.length > 0;
  };

  Messages = /*#__PURE__*/function () {
    function Messages(el) {
      _classCallCheck(this, Messages);

      this.placeMessages = this.placeMessages.bind(this);
      this.showAllCloseButtons = this.showAllCloseButtons.bind(this);
      this.hideMessage = this.hideMessage.bind(this);
      this.hasVisibleMessages = this.hasVisibleMessages.bind(this);
      this.el = el;
      this.setUp();
    }

    _createClass(Messages, [{
      key: "setUp",
      value: function setUp() {
        var _this = this;

        this.placeMessages();
        this.showAllCloseButtons();
        return Array.from(this.el.querySelectorAll('.js-messages-close-button')).forEach(function (elm) {
          return elm.addEventListener('click', _this.hideMessage);
        });
      }
    }, {
      key: "placeMessages",
      value: function placeMessages() {
        if (!hasHash()) {
          return;
        }

        return this.el.classList.add('is-fixed');
      }
    }, {
      key: "showAllCloseButtons",
      value: function showAllCloseButtons() {
        if (!hasHash()) {
          return;
        }

        return Array.from(this.el.querySelectorAll('.js-messages-close')).forEach(function (elm) {
          return elm.style.display = 'block';
        });
      }
    }, {
      key: "hideMessage",
      value: function hideMessage(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.closest('.js-messages-set').style.display = 'none'; // Hide container when it's empty

        if (!this.hasVisibleMessages()) {
          this.el.style.display = 'none';
          this.el.classList.remove('is-fixed');
        }
      }
    }, {
      key: "hasVisibleMessages",
      value: function hasVisibleMessages() {
        return !utils.isHidden(this.el.querySelectorAll('.js-messages-set'));
      }
    }]);

    return Messages;
  }();

  stModules.messages = function (elms) {
    return Array.from(elms).map(function (elm) {
      return new Messages(elm);
    });
  };

  stModules.Messages = Messages;
}).call(void 0);