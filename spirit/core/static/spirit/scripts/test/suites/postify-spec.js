(function() {
  describe("postify plugin tests", function() {
    var a_post, isHidden, plugin_postify;
    a_post = null;
    plugin_postify = null;
    isHidden = stModules.utils.isHidden;
    beforeEach(function() {
      document.body.innerHTML = "<a class=\"js-post\" href=\"/link1/\">link</a>\n<a class=\"js-post\" href=\"/link2/\">link 2</a>";
      a_post = document.querySelectorAll('.js-post');
      return plugin_postify = stModules.postify(a_post, {
        csrfToken: "foobar"
      });
    });
    afterEach(function() {
      return Array.from(document.querySelectorAll('.js-postify-form')).forEach(function(elm) {
        return elm.parentNode.removeChild(elm);
      });
    });
    it("prevents the default click behaviour on click", function() {
      var evt, preventDefault, stopPropagation, submit;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      submit = spyOn(window.HTMLFormElement.prototype, 'submit');
      submit.and.callFake(function() {});
      a_post[0].dispatchEvent(evt);
      expect(submit.calls.count()).toEqual(1);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
    return it("submits the form", function() {
      var form, submit;
      submit = spyOn(window.HTMLFormElement.prototype, 'submit');
      submit.and.callFake(function() {});
      a_post[0].click();
      form = document.querySelector('.js-postify-form');
      expect(submit.calls.count()).toEqual(1);
      expect(form.getAttribute('action')).toEqual("/link1/");
      expect(isHidden([form])).toEqual(true);
      return expect(document.querySelector('input[name=csrfmiddlewaretoken]').value).toEqual("foobar");
    });
  });

}).call(this);

//# sourceMappingURL=postify-spec.js.map
