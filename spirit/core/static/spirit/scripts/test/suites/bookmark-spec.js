(function() {
  describe("bookmark plugin tests", function() {
    var Bookmark, Mark, bookmarks, comments, mark, post;
    comments = null;
    bookmarks = null;
    mark = null;
    Bookmark = null;
    Mark = null;
    post = null;
    beforeEach(function() {
      document.body.innerHTML = "<div class=\"comment\" data-number=\"1\"></div>\n<div class=\"comment\" data-number=\"2\"></div>";
      post = spyOn(global, 'fetch');
      post.and.callFake(function() {
        return {
          then: function(func) {
            func({
              ok: true
            });
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
      });
      comments = document.querySelectorAll('.comment');
      bookmarks = stModules.bookmark(comments, {
        csrfToken: "foobar",
        target: "/foo/"
      });
      mark = bookmarks[0].mark;
      Bookmark = stModules.Bookmark;
      Mark = stModules.Mark;
      return bookmarks.forEach(function(bm) {
        return bm.onWaypoint();
      });
    });
    it("sends the first comment number", function() {
      expect(post.calls.any()).toEqual(true);
      expect(post.calls.argsFor(0)[0]).toEqual('/foo/');
      expect(post.calls.argsFor(0)[1].body.get('csrfmiddlewaretoken')).toEqual("foobar");
      return expect(post.calls.argsFor(0)[1].body.get('comment_number')).toEqual('1');
    });
    it("stores the last comment number", function() {
      return expect(mark.commentNumber).toEqual(2);
    });
    it("stores the same mark in every comment", function() {
      var bookmark_1, bookmark_2;
      bookmark_1 = bookmarks[0];
      bookmark_2 = bookmarks[bookmarks.length - 1];
      return expect(bookmark_1.mark).toEqual(bookmark_2.mark);
    });
    it("does not post on scroll up", function() {
      var bookmark_1;
      post.calls.reset();
      bookmark_1 = bookmarks[0];
      bookmark_1.onWaypoint();
      expect(mark.commentNumber).toEqual(2);
      return expect(post.calls.any()).toEqual(false);
    });
    it("does post on scroll down", function() {
      var bookmark_2;
      post.calls.reset();
      bookmark_2 = bookmarks[bookmarks.length - 1];
      bookmark_2.number = 999;
      bookmark_2.onWaypoint();
      expect(mark.commentNumber).toEqual(999);
      return expect(post.calls.any()).toEqual(true);
    });
    it("gets the comment number from the address bar", function() {
      var newMark, org_location_hash;
      org_location_hash = window.location.hash;
      window.location.hash = "";
      try {
        window.location.hash = "http://example.com/foo/#c5";
        newMark = new Mark();
        expect(newMark.commentNumber).toEqual(4);
        window.location.hash = "http://example.com/foo/";
        newMark = new Mark();
        expect(newMark.commentNumber).toEqual(0);
        window.location.hash = "http://example.com/foo/#foobar5";
        newMark = new Mark();
        return expect(newMark.commentNumber).toEqual(0);
      } finally {
        window.location.hash = org_location_hash;
      }
    });
    it("sends only one comment number in a given time", function() {
      var bookmark_2;
      post.calls.reset();
      expect(post.calls.any()).toEqual(false);
      mark.commentNumber = 0;
      bookmark_2 = bookmarks[bookmarks.length - 1];
      mark.isSending = true;
      bookmark_2.onWaypoint();
      expect(post.calls.any()).toEqual(false);
      mark.commentNumber = 0;
      post.calls.reset();
      mark.isSending = false;
      bookmark_2.onWaypoint();
      expect(post.calls.any()).toEqual(true);
      return expect(mark.isSending).toEqual(false);
    });
    it("sends current comment number after sending previous when current > previous", function() {
      var bookmark_1;
      post.calls.reset();
      expect(post.calls.any()).toEqual(false);
      post.and.callFake(function() {
        return {
          then: function(func) {
            var bookmark_2;
            bookmark_2 = bookmarks[bookmarks.length - 1];
            bookmark_2.onWaypoint();
            func({
              ok: true
            });
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
      });
      mark.commentNumber = -1;
      bookmark_1 = bookmarks[0];
      bookmark_1.onWaypoint();
      expect(post.calls.count()).toEqual(2);
      expect(post.calls.argsFor(0)[1].body.get('comment_number')).toEqual('1');
      expect(post.calls.argsFor(1)[1].body.get('comment_number')).toEqual('2');
      post.calls.reset();
      bookmark_1.onWaypoint();
      return expect(post.calls.any()).toEqual(false);
    });
    return it("sends next after server error", function() {
      var bookmark_1, log;
      post.calls.reset();
      expect(post.calls.any()).toEqual(false);
      post.and.callFake(function() {
        return {
          then: function() {
            var bookmark_2;
            bookmark_2 = bookmarks[bookmarks.length - 1];
            bookmark_2.onWaypoint();
            return {
              "catch": function(func) {
                func({
                  message: 'connection error'
                });
                return {
                  then: function(func) {
                    return func();
                  }
                };
              }
            };
          }
        };
      });
      log = spyOn(console, 'log');
      log.and.callFake(function() {});
      mark.commentNumber = -1;
      bookmark_1 = bookmarks[0];
      bookmark_1.onWaypoint();
      expect(post.calls.count()).toEqual(2);
      expect(post.calls.argsFor(0)[1].body.get('comment_number')).toEqual('1');
      expect(post.calls.argsFor(1)[1].body.get('comment_number')).toEqual('2');
      expect(log.calls.count()).toEqual(2);
      expect(log.calls.argsFor(0)[0]).toEqual('connection error');
      return expect(log.calls.argsFor(1)[0]).toEqual('connection error');
    });
  });

}).call(this);

//# sourceMappingURL=bookmark-spec.js.map
