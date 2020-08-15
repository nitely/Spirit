"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Make post on anchor click
  */
  var Postify;

  Postify = function () {
    var Postify = /*#__PURE__*/function () {
      function Postify(el, options) {
        _classCallCheck(this, Postify);

        this.makePost = this.makePost.bind(this);
        this.el = el;
        this.options = Object.assign({}, this.defaults, options);
        this.setUp();
      }

      _createClass(Postify, [{
        key: "setUp",
        value: function setUp() {
          return this.el.addEventListener('click', this.makePost);
        }
      }, {
        key: "makePost",
        value: function makePost(e) {
          var formElm, inputCSRFElm;
          e.preventDefault();
          e.stopPropagation();
          formElm = document.createElement('form');
          formElm.className = 'js-postify-form';
          formElm.action = this.el.getAttribute('href');
          formElm.method = 'POST';
          formElm.style.display = 'none';
          document.body.appendChild(formElm);
          inputCSRFElm = document.createElement('input');
          inputCSRFElm.name = 'csrfmiddlewaretoken';
          inputCSRFElm.type = 'hidden';
          inputCSRFElm.value = this.options.csrfToken;
          formElm.appendChild(inputCSRFElm);
          formElm.submit();
        }
      }]);

      return Postify;
    }();

    ;
    Postify.prototype.defaults = {
      csrfToken: "csrf_token"
    };
    return Postify;
  }.call(this);

  stModules.postify = function (elms, options) {
    return Array.from(elms).map(function (elm) {
      return new Postify(elm, options);
    });
  };

  stModules.Postify = Postify;
}).call(void 0);