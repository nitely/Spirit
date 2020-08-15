function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Social share popup
  */
  var SocialShare;

  SocialShare = /*#__PURE__*/function () {
    function SocialShare(el) {
      _classCallCheck(this, SocialShare);

      this.showDialog = this.showDialog.bind(this);
      this.closeDialog = this.closeDialog.bind(this);
      this.el = el;
      this.dialog = document.querySelector(this.el.dataset.dialog);
      this.allDialogs = document.querySelectorAll('.share');
      this.setUp();
    }

    _createClass(SocialShare, [{
      key: "setUp",
      value: function setUp() {
        var shareInput;
        this.el.addEventListener('click', this.showDialog);
        this.dialog.querySelector('.share-close').addEventListener('click', this.closeDialog);
        shareInput = this.dialog.querySelector('.share-url');
        shareInput.addEventListener('focus', this.select); // Hijack click, so it gets always selected

        return shareInput.addEventListener('mouseup', this.stopEvent);
      }
    }, {
      key: "showDialog",
      value: function showDialog(e) {
        e.preventDefault();
        e.stopPropagation();
        Array.from(this.allDialogs).forEach(function (elm) {
          return elm.style.display = 'none';
        });
        this.dialog.style.display = 'block';
      }
    }, {
      key: "closeDialog",
      value: function closeDialog(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dialog.style.display = 'none';
      }
    }, {
      key: "select",
      value: function select(e) {
        e.preventDefault();
        e.stopPropagation();
        this.setSelectionRange(0, this.value.length - 1);
      }
    }, {
      key: "stopEvent",
      value: function stopEvent(e) {
        e.preventDefault();
        e.stopPropagation();
      }
    }]);

    return SocialShare;
  }();

  stModules.socialShare = function (elms) {
    return Array.from(elms).map(function (elm) {
      return new SocialShare(elm);
    });
  };

  stModules.SocialShare = SocialShare;
}).call(this);