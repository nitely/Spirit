(function() {
  describe("postify plugin tests", function() {
    var Postify, a_post, plugin_postify;
    a_post = null;
    plugin_postify = null;
    Postify = null;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('postify.html');
      a_post = $('a.js-post').postify({
        csrfToken: "foobar"
      });
      plugin_postify = a_post.first().data('plugin_postify');
      return Postify = $.fn.postify.Postify;
    });
    it("doesnt break selector chaining", function() {
      expect(a_post).toEqual($('.js-post'));
      return expect(a_post.length).toEqual(2);
    });
    it("prevents the default click behaviour on click", function() {
      var event, preventDefault, stopPropagation;
      event = {
        type: 'click',
        stopPropagation: (function() {}),
        preventDefault: (function() {})
      };
      stopPropagation = spyOn(event, 'stopPropagation');
      preventDefault = spyOn(event, 'preventDefault');
      spyOn(plugin_postify, 'formSubmit');
      $(".js-post").first().trigger(event);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
    return it("submits the form", function() {
      var formSubmit;
      formSubmit = spyOn(plugin_postify, 'formSubmit');
      $('.js-post').first().trigger('click');
      expect(formSubmit).toHaveBeenCalled();
      expect($("form").last().attr('action')).toEqual("/link1/");
      expect($("form").last().is(":visible")).toEqual(false);
      return expect($("input[name=csrfmiddlewaretoken]").val()).toEqual("foobar");
    });
  });

}).call(this);

//# sourceMappingURL=postify-spec.js.map
