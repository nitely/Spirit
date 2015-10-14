(function() {
  describe("social-share plugin tests", function() {
    var SocialShare, social_share;
    social_share = null;
    SocialShare = null;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('social_share.html');
      social_share = $('.js-share').social_share();
      return SocialShare = $.fn.social_share.SocialShare;
    });
    it("doesnt break selector chaining", function() {
      expect(social_share).toEqual($('.js-share'));
      return expect(social_share.length).toEqual(2);
    });
    it("shows the share dialog", function() {
      expect($('.test-1').is(":visible")).toEqual(false);
      social_share.first().trigger('click');
      expect($('.test-1').is(":visible")).toEqual(true);
      expect($('.test-2').is(":visible")).toEqual(false);
      social_share.last().trigger('click');
      expect($('.test-2').is(":visible")).toEqual(true);
      return expect($('.test-1').is(":visible")).toEqual(false);
    });
    it("prevents the default click behaviour on share click", function() {
      var event, preventDefault, stopPropagation;
      event = {
        type: 'click',
        stopPropagation: (function() {}),
        preventDefault: (function() {})
      };
      stopPropagation = spyOn(event, 'stopPropagation');
      preventDefault = spyOn(event, 'preventDefault');
      social_share.first().trigger(event);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
    it("closes the dialog", function() {
      social_share.first().trigger('click');
      expect($('.test-1').is(":visible")).toEqual(true);
      $('.test-1').find('.share-close').trigger('click');
      return expect($('.test-1').is(":visible")).toEqual(false);
    });
    it("prevents the default click behaviour on close dialog", function() {
      var event, preventDefault, stopPropagation;
      event = {
        type: 'click',
        stopPropagation: (function() {}),
        preventDefault: (function() {})
      };
      stopPropagation = spyOn(event, 'stopPropagation');
      preventDefault = spyOn(event, 'preventDefault');
      $('.test-1').find('.share-close').trigger(event);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
    it("auto selects the share link on focus", function() {
      var $shareInput;
      social_share.first().trigger('click');
      $shareInput = $('.test-1').find('.share-url');
      return $shareInput.trigger('focus');
    });
    return it("prevents the default behaviour on input mouseup", function() {
      var event, preventDefault, stopPropagation;
      event = {
        type: 'mouseup',
        stopPropagation: (function() {}),
        preventDefault: (function() {})
      };
      stopPropagation = spyOn(event, 'stopPropagation');
      preventDefault = spyOn(event, 'preventDefault');
      $('.test-1').find('.share-url').trigger(event);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=social_share-spec.js.map
