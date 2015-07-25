describe "like plugin tests", ->
  likes = null
  like = null
  Like = null
  post = null
  data = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'like.html'

    post = spyOn $, 'post'
    post.and.callFake (req) ->
      d = $.Deferred()
      d.resolve(data)  # success
      #d.reject()  # failure
      return d.promise()

    data =
      url_delete: "/foo/delete/"

    likes = $('.js-like').like {
      csrfToken: "foobar",
      likeText: "foo like ({count})",
      removeLikeText: "foo remove like ({count})"
    }
    like = likes.first().data 'plugin_like'
    Like = $.fn.like.Like

  it "doesnt break selector chaining", ->
    expect(likes).toEqual $('.js-like')
    expect(likes.length).toEqual 2

  it "can create the like", ->
    expect($.post.calls.any()).toEqual false

    likes.first().trigger 'click'
    expect($.post.calls.any()).toEqual true
    expect($.post.calls.argsFor(0)).toEqual ['/foo/create/', {csrfmiddlewaretoken: "foobar", }]

  it "can create and remove the like", ->
    # create
    data =
      url_delete: "/foo/delete/"
    likes.first().trigger 'click'
    expect($.post.calls.argsFor(0)).toEqual ['/foo/create/', {csrfmiddlewaretoken: "foobar", }]
    expect(likes.first().text()).toEqual "foo remove like (1)"

    # remove
    data =
      url_create: "/foo/create/"
    likes.first().trigger 'click'
    expect($.post.calls.argsFor(1)).toEqual ['/foo/delete/', {csrfmiddlewaretoken: "foobar", }]
    expect(likes.first().text()).toEqual "foo like (0)"

    # create again... and so on...
    data =
      url_delete: "/foo/delete/"
    likes.first().trigger 'click'
    expect($.post.calls.argsFor(2)).toEqual ['/foo/create/', {csrfmiddlewaretoken: "foobar", }]
    expect(likes.first().text()).toEqual "foo remove like (1)"

  it "will tell about an api change", ->
    data =
      unknown: null

    likes.first().trigger 'click'
    expect(likes.first().text()).toEqual "api error"

  it "prevents from multiple posts while sending", ->
    expect($.post.calls.any()).toEqual false

    d = $.Deferred()
    post.and.callFake (req) =>
      d.resolve(data)
      return d.promise()

    always = spyOn post(), 'always'
    post.calls.reset()
    likes.first().trigger 'click'
    expect($.post.calls.any()).toEqual true
    expect(always.calls.any()).toEqual true

    # next click should do nothing
    post.calls.reset()
    likes.first().trigger 'click'
    expect($.post.calls.any()).toEqual false

  it "prevents the default click behaviour", ->
    event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    likes.first().trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()