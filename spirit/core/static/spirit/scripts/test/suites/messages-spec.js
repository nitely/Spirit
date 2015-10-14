(function() {
  describe("messages plugin tests", function() {
    var Messages;
    Messages = null;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('messages.html');
      return Messages = $.fn.messages.Messages;
    });
    it("doesnt break selector chaining", function() {
      var messages;
      messages = $('.js-messages-dummy').messages();
      expect(messages).toEqual($('.js-messages-dummy'));
      return expect(messages.length).toEqual(2);
    });
    it("does nothing when no hash", function() {
      var messages;
      messages = $('.js-messages').messages();
      expect(messages.hasClass('is-fixed')).toEqual(false);
      return expect($('.js-message-close').is(":hidden")).toEqual(true);
    });
    return it("places the messages when there is a hash", function() {
      var messages, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        messages = $('.js-messages').messages();
        return expect(messages.hasClass('is-fixed')).toEqual(true);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
  });

}).call(this);

//# sourceMappingURL=messages-spec.js.map
