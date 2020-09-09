(function() {
  describe("like plugin tests", function() {
    var likeElms, likes, post, responseData;
    likeElms = null;
    likes = null;
    post = null;
    responseData = null;
    beforeEach(function() {
      document.body.innerHTML = "<div>\n  <ul>\n    <li><a class=\"js-like\" href=\"/foo/create/\" data-count=\"0\"><i class=\"fa fa-heart\"></i> like</a></li>\n  </ul>\n</div>\n<div>\n  <ul>\n    <li><a class=\"js-like\" href=\"foo/delete/\" data-count=\"1\"><i class=\"fa fa-heart\"></i> remove like</a></li>\n  </ul>\n</div>";
      responseData = {
        url_create: '/create/foo'
      };
      post = spyOn(global, 'fetch');
      post.and.callFake(function() {
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
      likeElms = document.querySelectorAll('.js-like');
      return likes = stModules.like(likeElms, {
        csrfToken: "foobar",
        likeText: "foo like ({count})",
        removeLikeText: "foo remove like ({count})"
      });
    });
    it("can create the like", function() {
      post.calls.reset();
      likeElms[0].click();
      expect(post.calls.any()).toEqual(true);
      expect(post.calls.argsFor(0)[0]).toEqual('/foo/create/');
      return expect(post.calls.argsFor(0)[1].body.get('csrfmiddlewaretoken')).toEqual("foobar");
    });
    it("can create and remove the like", function() {
      post.calls.reset();
      responseData = {
        url_delete: "/foo/delete/"
      };
      likeElms[0].click();
      expect(post.calls.argsFor(0)[0]).toEqual('/foo/create/');
      expect(likeElms[0].textContent).toEqual("foo remove like (1)");
      post.calls.reset();
      responseData = {
        url_create: "/foo/create/"
      };
      likeElms[0].click();
      expect(post.calls.argsFor(0)[0]).toEqual('/foo/delete/');
      expect(likeElms[0].textContent).toEqual("foo like (0)");
      post.calls.reset();
      responseData = {
        url_delete: "/foo/delete/"
      };
      likeElms[0].click();
      expect(post.calls.argsFor(0)[0]).toEqual('/foo/create/');
      return expect(likeElms[0].textContent).toEqual("foo remove like (1)");
    });
    it("will tell about an api change", function() {
      responseData = {
        unknown: null
      };
      likeElms[0].click();
      return expect(likeElms[0].textContent).toEqual("api error");
    });
    it("prevents from multiple posts while sending", function() {
      post.and.callFake(function() {
        return {
          then: function() {
            return {
              then: function() {
                return {
                  "catch": function() {
                    return {
                      then: function() {}
                    };
                  }
                };
              }
            };
          }
        };
      });
      likeElms[0].click();
      post.calls.reset();
      likeElms[0].click();
      return expect(post.calls.any()).toEqual(false);
    });
    return it("prevents the default click behaviour", function() {
      var evt, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      likeElms[0].dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=like-spec.js.map
