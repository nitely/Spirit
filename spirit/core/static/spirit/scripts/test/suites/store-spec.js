(function() {
  describe("store plugin tests", function() {
    var storage, textarea;
    textarea = null;
    storage = null;
    beforeEach(function() {
      document.body.innerHTML = "<form action=\".\">\n  <textarea id=\"my-fixture\"></textarea>\n  <textarea id=\"my-fixture-2\"></textarea>\n</form>";
      localStorage.clear();
      textarea = document.querySelector('#my-fixture');
      return storage = stModules.store(textarea, 'unique-id');
    });
    it("loads previous stored value", function() {
      localStorage.setItem('unique-id', "text");
      textarea = document.querySelector('#my-fixture-2');
      stModules.store(textarea, 'unique-id');
      return expect(textarea.value).toEqual("text");
    });
    it("updates the field on storage change", function() {
      var evt;
      localStorage.setItem('unique-id', "text");
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("storage", false, true);
      window.dispatchEvent(evt);
      return expect(textarea.value).toEqual("text");
    });
    it("saves value to localStorage on input", function() {
      var evt;
      textarea.value = "foobar";
      expect(localStorage.getItem('unique-id')).toEqual(null);
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("input", false, true);
      textarea.dispatchEvent(evt);
      return expect(localStorage.getItem('unique-id')).toEqual("foobar");
    });
    it("wont (re)update the field on input", function() {
      var evt, setItem;
      localStorage.setItem('unique-id', "no-foobar");
      textarea.value = "foobar";
      setItem = spyOn(window.Storage.prototype, 'setItem');
      setItem.and.callFake(function() {
        var evt;
        evt = document.createEvent("HTMLEvents");
        evt.initEvent("storage", false, true);
        return window.dispatchEvent(evt);
      });
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("input", false, true);
      textarea.dispatchEvent(evt);
      expect(setItem.calls.count()).toEqual(1);
      expect(localStorage.getItem('unique-id')).toEqual("no-foobar");
      return expect(textarea.value).toEqual("foobar");
    });
    return it("gets cleared on submit", function() {
      var evt, form;
      localStorage.setItem('unique-id', "text");
      form = document.querySelector('form');
      form.addEventListener('submit', function(e) {
        return e.preventDefault();
      });
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("submit", false, true);
      form.dispatchEvent(evt);
      return expect(localStorage.getItem('unique-id')).toEqual(null);
    });
  });

}).call(this);

//# sourceMappingURL=store-spec.js.map
