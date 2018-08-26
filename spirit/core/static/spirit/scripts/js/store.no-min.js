
/*
    A storage for form elements (inputs, text-areas, ets)
    It auto-clears on form submission. Also auto-sync across tabs.
 */

(function() {
  var Storage,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  Storage = (function() {
    function Storage(el, lsKey) {
      this.clearStorage = bind(this.clearStorage, this);
      this.updateField = bind(this.updateField, this);
      this.updateStorage = bind(this.updateStorage, this);
      this._updateStorage = bind(this._updateStorage, this);
      this.el = el;
      this.lsKey = lsKey;
      this.isUpdating = false;
      this.setUp();
    }

    Storage.prototype.setUp = function() {
      if (typeof localStorage === "undefined" || localStorage === null) {
        console.log('No localStorage support. Bailing out');
        return;
      }
      if (this.lsKey in localStorage) {
        this.updateField();
      }
      window.addEventListener('storage', this.updateField);
      this.el.addEventListener('input', this.updateStorage);
      this.el.addEventListener('change', this.updateStorage);
      this.el.addEventListener('propertychange', this.updateStorage);
      return this.el.closest('form').addEventListener('submit', this.clearStorage);
    };

    Storage.prototype._updateStorage = function() {
      var err, value;
      value = this.el.value;
      try {
        localStorage.setItem(this.lsKey, value);
      } catch (error) {
        err = error;
        if (localStorage.length > 0) {
          localStorage.clear();
        }
      }
    };

    Storage.prototype.updateStorage = function() {
      this.isUpdating = true;
      try {
        this._updateStorage();
      } finally {
        this.isUpdating = false;
      }
    };

    Storage.prototype.updateField = function() {
      if (this.isUpdating) {
        return;
      }
      this.el.value = localStorage.getItem(this.lsKey);
    };

    Storage.prototype.clearStorage = function() {
      this.isUpdating = true;
      try {
        localStorage.removeItem(this.lsKey);
      } finally {
        this.isUpdating = false;
      }
    };

    return Storage;

  })();

  stModules.store = function(elm, lsKey) {
    return new Storage(elm, lsKey);
  };

  stModules.Storage = Storage;

}).call(this);
