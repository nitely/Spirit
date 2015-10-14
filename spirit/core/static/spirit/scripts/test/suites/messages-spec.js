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
      return expect($('.js-messages-close').is(":hidden")).toEqual(true);
    });
    it("places the messages when there is a hash", function() {
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
    it("shows all the close buttons", function() {
      var messages, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        messages = $('.js-messages').messages();
        return expect($('.js-messages-close').is(":hidden")).toEqual(false);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    it("closes/hides the message", function() {
      var first_set, messages, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        messages = $('.js-messages').messages();
        first_set = messages.find('.js-messages-set').first();
        first_set.find('.js-messages-close-button').trigger('click');
        expect(first_set.is(":hidden")).toEqual(true);
        return expect(messages.is(":hidden")).toEqual(false);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    it("closes/hides the container when no more visible messages", function() {
      var messages, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        messages = $('.js-messages').messages();
        messages.find('.js-messages-close-button').trigger('click');
        expect(messages.is(":hidden")).toEqual(true);
        return expect(messages.hasClass('is-fixed')).toEqual(false);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    return it("prevents the default click behaviour on close message", function() {
      var event, messages, preventDefault, stopPropagation;
      event = {
        type: 'click',
        stopPropagation: (function() {}),
        preventDefault: (function() {})
      };
      stopPropagation = spyOn(event, 'stopPropagation');
      preventDefault = spyOn(event, 'preventDefault');
      messages = $('.js-messages').messages();
      messages.find('.js-messages-close-button').first().trigger(event);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=messages-spec.js.map
