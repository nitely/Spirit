(function() {
  describe("social-share plugin tests", function() {
    var isHidden, social_share;
    social_share = null;
    isHidden = stModules.utils.isHidden;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('social_share.html');
      social_share = document.querySelectorAll('.js-share');
      return stModules.socialShare(social_share);
    });
    it("shows the share dialog", function() {
      expect(isHidden([document.querySelector('.test-1')])).toEqual(true);
      social_share[0].click();
      expect(isHidden([document.querySelector('.test-1')])).toEqual(false);
      expect(isHidden([document.querySelector('.test-2')])).toEqual(true);
      social_share[1].click();
      expect(isHidden([document.querySelector('.test-1')])).toEqual(true);
      return expect(isHidden([document.querySelector('.test-2')])).toEqual(false);
    });
    it("prevents the default click behaviour on share click", function() {
      var evt, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      social_share[0].dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
    it("closes the dialog", function() {
      social_share[0].click();
      expect(isHidden([document.querySelector('.test-1')])).toEqual(false);
      document.querySelector('.test-1').querySelector('.share-close').click();
      return expect(isHidden([document.querySelector('.test-1')])).toEqual(true);
    });
    it("prevents the default click behaviour on close dialog", function() {
      var evt, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      document.querySelector('.test-1').querySelector('.share-close').dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
    it("auto selects the share link on focus", function() {
      var shareInput;
      social_share[0].click();
      shareInput = document.querySelector('.test-1').querySelector('.share-url');
      return shareInput.focus();
    });
    return it("prevents the default behaviour on input mouseup", function() {
      var evt, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("mouseup", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      document.querySelector('.test-1').querySelector('.share-url').dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=social_share-spec.js.map
