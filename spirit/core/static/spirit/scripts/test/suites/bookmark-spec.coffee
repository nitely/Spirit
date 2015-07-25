describe "bookmark plugin tests", ->
  comments = null
  mark = null
  Bookmark = null
  Mark = null
  post = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'bookmark.html'

    post = spyOn $, 'post'
    post.and.callFake (req) ->
      d = $.Deferred()
      d.resolve()  # success
      #d.reject(data)  # failure
      return d.promise()

    comments = $('.comment').bookmark {csrfToken: "foobar", target: "/foo/"}
    mark = comments.first().data('plugin_bookmark').mark
    Bookmark = $.fn.bookmark.Bookmark
    Mark = $.fn.bookmark.Mark

  it "doesnt break selector chaining", ->
    expect(comments).toEqual $('.comment')
    expect(comments.length).toEqual 2

  it "sends the first comment number", ->
    expect($.post.calls.any()).toEqual true
    expect($.post.calls.argsFor(0)).toEqual ['/foo/', {csrfmiddlewaretoken: "foobar", comment_number: 1}]

  it "stores the last comment number", ->
    bookmark = comments.first().data 'plugin_bookmark'
    expect(bookmark.mark.commentNumber).toEqual 2

  it "stores the same mark in every comment", ->
    bookmark_1 = comments.first().data 'plugin_bookmark'
    bookmark_2 = comments.last().data 'plugin_bookmark'
    expect(bookmark_1.mark).toEqual bookmark_2.mark

  it "does not post on scroll up", ->
    bookmark_1 = comments.first().data 'plugin_bookmark'
    sendCommentNumber = spyOn bookmark_1, 'sendCommentNumber'
    bookmark_1.onWaypoint()
    expect(mark.commentNumber).toEqual 2
    expect(sendCommentNumber).not.toHaveBeenCalled()

  it "does post on scroll down", ->
    comments.last().data 'number', 999
    bookmark_2 = comments.last().data 'plugin_bookmark'
    sendCommentNumber = spyOn bookmark_2, 'sendCommentNumber'
    bookmark_2.onWaypoint()
    expect(mark.commentNumber).toEqual 999
    expect(sendCommentNumber).toHaveBeenCalled()

  it "gets the comment number from the address bar", ->
    org_location_hash = window.location.hash
    window.location.hash = ""
    try
      window.location.hash = "http://example.com/foo/#c5"
      newMark = new Mark()
      # it substract 1 from the real comment number
      expect(newMark.commentNumber).toEqual 4

      window.location.hash = "http://example.com/foo/"
      newMark = new Mark()
      expect(newMark.commentNumber).toEqual -1

      window.location.hash = "http://example.com/foo/#foobar5"
      newMark = new Mark()
      expect(newMark.commentNumber).toEqual -1
    finally
      window.location.hash = org_location_hash

  it "sends only one comment number in a given time", ->
    post.calls.reset()
    expect($.post.calls.any()).toEqual false

    # won't post if already sending
    bookmark_2 = comments.last().data 'plugin_bookmark'
    mark.isSending = true
    bookmark_2.sendCommentNumber()
    expect($.post.calls.any()).toEqual false

    # will prevent from others to post
    d = $.Deferred()
    post.and.callFake (req) =>
      d.resolve()
      return d.promise()

    always = spyOn post(), 'always'
    post.calls.reset()
    mark.isSending = false
    bookmark_2.sendCommentNumber()
    expect($.post.calls.any()).toEqual true
    expect(always.calls.any()).toEqual true
    expect(mark.isSending).toEqual true