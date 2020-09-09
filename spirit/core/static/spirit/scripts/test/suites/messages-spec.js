(function() {
  describe("messages plugin tests", function() {
    var isHidden;
    isHidden = stModules.utils.isHidden;
    beforeEach(function() {
      return document.body.innerHTML = "<div class=\"js-messages\">\n  <div class=\"js-messages-set\">\n    <ul>\n      <li>success 1</li>\n      <li>success 2</li>\n    </ul>\n    <div class=\"js-messages-close\" style=\"display: none\">\n      <i class=\"js-messages-close-button\"></i>\n    </div>\n  </div>\n  <div class=\"js-messages-set\">\n    <ul>\n      <li>error 1</li>\n      <li>error 2</li>\n    </ul>\n    <div class=\"js-messages-close\" style=\"display: none\">\n      <i class=\"js-messages-close-button\"></i>\n    </div>\n  </div>\n</div>\n<div class=\"js-messages-dummy\"></div>\n<div class=\"js-messages-dummy\"></div>";
    });
    it("attaches all messages", function() {
      var messages;
      messages = stModules.messages(document.querySelectorAll('.js-messages-dummy'));
      return expect(messages.length).toEqual(2);
    });
    it("does nothing when no hash", function() {
      var message;
      message = document.querySelector('.js-messages-dummy');
      stModules.messages([message]);
      expect(message.classList.contains('is-fixed')).toEqual(false);
      return expect(isHidden(document.querySelectorAll('.js-messages-close'))).toEqual(true);
    });
    it("places the messages when there is a hash", function() {
      var message, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        message = document.querySelector('.js-messages');
        stModules.messages([message]);
        return expect(message.classList.contains('is-fixed')).toEqual(true);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    it("shows all the close buttons", function() {
      var org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        stModules.messages(document.querySelectorAll('.js-messages'));
        return expect(isHidden(document.querySelectorAll('.js-messages-close'))).toEqual(false);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    it("closes/hides the message", function() {
      var first_set, messages, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        messages = document.querySelectorAll('.js-messages');
        stModules.messages(messages);
        first_set = document.querySelector('.js-messages').querySelector('.js-messages-set');
        first_set.querySelector('.js-messages-close-button').click();
        expect(isHidden([first_set])).toEqual(true);
        return expect(isHidden(messages)).toEqual(false);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    it("closes/hides the container when no more visible messages", function() {
      var message, org_location_hash;
      org_location_hash = window.location.hash;
      try {
        window.location.hash = "#p1";
        message = document.querySelector('.js-messages');
        stModules.messages([message]);
        Array.from(message.querySelectorAll('.js-messages-close-button')).forEach(function(elm) {
          return elm.click();
        });
        expect(isHidden([message])).toEqual(true);
        return expect(message.classList.contains('is-fixed')).toEqual(false);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    return it("prevents the default click behaviour on close message", function() {
      var evt, message, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      message = document.querySelector('.js-messages');
      stModules.messages([message]);
      message.querySelector('.js-messages-close-button').dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=messages-spec.js.map
