(function() {
  var $, Storage,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  Storage = (function() {
    function Storage(el, lsKey) {
      this.clearStorage = bind(this.clearStorage, this);
      this.updateField = bind(this.updateField, this);
      this.updateStorage = bind(this.updateStorage, this);
      this.el = $(el);
      this.lsKey = lsKey;
      this.setUp();
    }

    Storage.prototype.setUp = function() {
      var $form;
      if (typeof localStorage === "undefined" || localStorage === null) {
        return;
      }
      if (this.lsKey in localStorage) {
        this.updateField();
      }
      $(window).on('storage', this.updateField);
      this.el.on('input change propertychange', (function(_this) {
        return function() {
          $(window).off('storage', _this.updateField);
          _this.updateStorage();
          $(window).on('storage', _this.updateField);
        };
      })(this));
      $form = this.el.closest("form");
      return $form.on('submit', this.clearStorage);
    };

    Storage.prototype.updateStorage = function() {
      var err, value;
      value = this.el.val();
      try {
        localStorage[this.lsKey] = value;
      } catch (error) {
        err = error;
        localStorage.clear();
      }
    };

    Storage.prototype.updateField = function() {
      this.el.val(localStorage[this.lsKey]);
    };

    Storage.prototype.clearStorage = function() {
      delete localStorage[this.lsKey];
    };

    return Storage;

  })();

  $.fn.extend({
    store: function(lsKey) {
      return this.each(function() {
        if (!$(this).data('plugin_store')) {
          return $(this).data('plugin_store', new Storage(this, lsKey));
        }
      });
    }
  });

  $.fn.store.Storage = Storage;

}).call(this);
