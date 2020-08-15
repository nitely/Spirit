
/*
    Make post on anchor click
 */

(function() {
  var Postify,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  Postify = (function() {
    Postify.prototype.defaults = {
      csrfToken: "csrf_token"
    };

    function Postify(el, options) {
      this.makePost = bind(this.makePost, this);
      this.el = el;
      this.options = Object.assign({}, this.defaults, options);
      this.setUp();
    }

    Postify.prototype.setUp = function() {
      return this.el.addEventListener('click', this.makePost);
    };

    Postify.prototype.makePost = function(e) {
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
    };

    return Postify;

  })();

  stModules.postify = function(elms, options) {
    return Array.from(elms).map(function(elm) {
      return new Postify(elm, options);
    });
  };

  stModules.Postify = Postify;

}).call(this);
