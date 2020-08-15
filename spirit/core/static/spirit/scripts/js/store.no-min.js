function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      A storage for form elements (inputs, text-areas, ets)
      It auto-clears on form submission. Also auto-sync across tabs.
  */
  var Storage;

  Storage = /*#__PURE__*/function () {
    function Storage(el, lsKey) {
      _classCallCheck(this, Storage);

      this._updateStorage = this._updateStorage.bind(this);
      this.updateStorage = this.updateStorage.bind(this);
      this.updateField = this.updateField.bind(this);
      this.clearStorage = this.clearStorage.bind(this);
      this.el = el;
      this.lsKey = lsKey;
      this.isUpdating = false;
      this.setUp();
    }

    _createClass(Storage, [{
      key: "setUp",
      value: function setUp() {
        if (typeof localStorage === "undefined" || localStorage === null) {
          console.log('No localStorage support. Bailing out');
          return;
        }

        if (this.lsKey in localStorage) {
          this.updateField();
        }

        window.addEventListener('storage', this.updateField); // On change

        this.el.addEventListener('input', this.updateStorage);
        this.el.addEventListener('change', this.updateStorage);
        this.el.addEventListener('propertychange', this.updateStorage);
        return this.el.closest('form').addEventListener('submit', this.clearStorage);
      }
    }, {
      key: "_updateStorage",
      value: function _updateStorage() {
        var err, value;
        value = this.el.value;

        try {
          // May trigger storage
          localStorage.setItem(this.lsKey, value);
        } catch (error) {
          err = error; // The localStorage is probably full, nothing to do other than clearing it

          if (localStorage.length > 0) {
            localStorage.clear();
          }
        }
      }
    }, {
      key: "updateStorage",
      value: function updateStorage() {
        this.isUpdating = true;

        try {
          this._updateStorage();
        } finally {
          this.isUpdating = false;
        }
      }
    }, {
      key: "updateField",
      value: function updateField() {
        if (this.isUpdating) {
          return;
        }

        this.el.value = localStorage.getItem(this.lsKey);
      }
    }, {
      key: "clearStorage",
      value: function clearStorage() {
        this.isUpdating = true;

        try {
          // Triggers storage
          localStorage.removeItem(this.lsKey);
        } finally {
          this.isUpdating = false;
        }
      }
    }]);

    return Storage;
  }();

  stModules.store = function (elm, lsKey) {
    return new Storage(elm, lsKey);
  };

  stModules.Storage = Storage;
}).call(this);