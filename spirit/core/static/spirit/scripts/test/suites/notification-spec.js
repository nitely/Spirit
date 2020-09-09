(function() {
  describe("notification plugin tests", function() {
    var get, isHidden, responseData, tab;
    responseData = null;
    get = null;
    tab = null;
    isHidden = stModules.utils.isHidden;
    beforeEach(function() {
      document.body.innerHTML = "<div class=\"js-tabs-container\">\n  <ul>\n    <li><a\n      class=\"js-tab-notification js-tab\"\n      href=\"#\"\n      data-related=\".js-notifications-content\"\n      data-content=\".js-notifications-content-list\"\n    >bell</a></li>\n  </ul>\n  <div class=\"js-tab-content js-notifications-content\" style=\"display: none;\">\n    <div class=\"js-notifications-content-list\"></div>\n  </div>\n</div>";
      responseData = {
        n: [
          {
            user: "username",
            action: 1,
            title: "title",
            url: "/foobar/",
            is_read: true
          }
        ]
      };
      get = spyOn(global, 'fetch');
      get.and.callFake(function() {
        return {
          then: function(func) {
            var data;
            data = func({
              ok: true,
              json: function() {
                return responseData;
              }
            });
            return {
              then: function(func) {
                func(data);
                return {
                  "catch": function() {
                    return {
                      then: function(func) {
                        return func();
                      }
                    };
                  }
                };
              }
            };
          }
        };
      });
      tab = document.querySelector('.js-tab-notification');
      return stModules.notification([tab], {
        notificationUrl: "/foo/",
        notificationListUrl: "/foo/list/",
        mentionTxt: "{user} foo you on {topic}",
        commentTxt: "{user} has bar on {topic}",
        showAll: "foo Show all",
        empty: "foo empty",
        unread: "foo unread"
      });
    });
    it("gets the notifications", function() {
      get.calls.reset();
      tab.click();
      expect(get.calls.count()).toEqual(1);
      expect(get.calls.argsFor(0)[0]).toEqual('/foo/');
      get.calls.reset();
      tab.click();
      return expect(get.calls.count()).toEqual(0);
    });
    it("avoids XSS from topic title", function() {
      get.calls.reset();
      responseData = {
        n: [
          {
            user: "username",
            action: 1,
            title: '<bad>"bad"</bad>',
            url: "/foobar/",
            is_read: true
          }
        ]
      };
      tab.click();
      expect(get.calls.count()).toEqual(1);
      return expect(document.querySelector('.js-notifications-content-list').innerHTML).toEqual('<ul><li><a href="/foobar/">username foo you on &lt;bad&gt;"bad"&lt;/bad&gt;</a></li>' + '<li><a href="/foo/list/">foo Show all</a></li></ul>');
    });
    it("shows mention notifications", function() {
      get.calls.reset();
      tab.click();
      expect(get.calls.count()).toEqual(1);
      return expect(document.querySelector('.js-notifications-content-list').innerHTML).toEqual('<ul><li><a href="/foobar/">username foo you on title</a></li>' + '<li><a href="/foo/list/">foo Show all</a></li></ul>');
    });
    it("shows comment notifications", function() {
      responseData.n[0].action = 2;
      tab.click();
      expect(get.calls.count()).toEqual(1);
      return expect(document.querySelector('.js-notifications-content-list').innerHTML).toEqual('<ul><li><a href="/foobar/">username has bar on title</a></li>' + '<li><a href="/foo/list/">foo Show all</a></li></ul>');
    });
    it("marks unread notifications", function() {
      responseData.n[0].is_read = false;
      tab.click();
      expect(get.calls.count()).toEqual(1);
      return expect(document.querySelector('.js-notifications-content-list').innerHTML).toEqual('<ul><li><a href="/foobar/">username foo you on title <span class="unread">foo unread</span></a></li>' + '<li><a href="/foo/list/">foo Show all</a></li></ul>');
    });
    it("shows an error on server error", function() {
      var log;
      log = spyOn(console, 'log');
      log.and.callFake(function() {});
      get.and.callFake(function() {
        return {
          then: function(func) {
            var err;
            try {
              return func({
                ok: false,
                status: 500,
                statusText: 'server error'
              });
            } catch (error) {
              err = error;
              return {
                then: function() {
                  return {
                    "catch": function(func) {
                      func(err);
                      return {
                        then: function(func) {
                          return func();
                        }
                      };
                    }
                  };
                }
              };
            }
          }
        };
      });
      tab.click();
      expect(get.calls.count()).toEqual(1);
      return expect(document.querySelector('.js-notifications-content-list').innerHTML).toEqual('<div>error: 500 server error</div>');
    });
    return it("prevents the default click behaviour", function() {
      var evt, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      tab.dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=notification-spec.js.map
