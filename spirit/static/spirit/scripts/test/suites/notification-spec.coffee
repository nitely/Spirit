describe "notification plugin tests", ->
  tab = null
  notification = null
  Notification = null
  get = null
  data = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'notification.html'

    get = spyOn $, 'getJSON'
    get.and.callFake (req) ->
      d = $.Deferred()
      d.resolve(data)  # success
      #d.reject()  # failure
      return d.promise()

    data =
      n: [{
        user: "username",
        action: 1,
        title: "title",
        url: "/foobar/",
        is_read: true
      }]

    tab = $.notification {
      notificationUrl: "/foo/",
      notificationListUrl: "/foo/list/",
      mentionTxt: "{user} foo you on {topic}",
      commentTxt: "{user} has bar on {topic}",
      showAll: "foo Show all",
      empty: "foo empty",
      unread: "foo unread"
    }
    notification = tab.first().data 'plugin_notification'
    Notification = $.notification.Notification

  it "doesnt break selector chaining", ->
    expect(tab).toEqual $('.js-tab-notification')

  it "gets the notifications", ->
    expect(get.calls.any()).toEqual false

    tab.first().trigger "click"
    expect(get.calls.any()).toEqual true
    expect(get.calls.count()).toEqual 1
    expect(get.calls.argsFor(0)).toEqual ['/foo/']

    # making multiple clicks do nothing
    tab.first().trigger "click"
    expect(get.calls.count()).toEqual 1

  it "shows the notifications, mentions", ->
    tab.first().trigger "click"
    expect(get.calls.any()).toEqual true
    expect($(".js-notifications-content").html()).toEqual '<div>username foo you on <a href="/foobar/">title</a></div><div><a href="/foo/list/">foo Show all</a></div>'

  it "shows the notifications, comments", ->
    data.n[0].action = 2

    tab.first().trigger "click"
    expect(get.calls.any()).toEqual true
    expect($(".js-notifications-content").html()).toEqual '<div>username has bar on <a href="/foobar/">title</a></div><div><a href="/foo/list/">foo Show all</a></div>'

  it "shows the notifications, unread", ->
    data.n[0].is_read = false

    tab.first().trigger "click"
    expect(get.calls.any()).toEqual true
    expect($(".js-notifications-content").html()).toEqual '<div>username foo you on <a href="/foobar/">title</a> <span class="row-unread">foo unread</span></div><div><a href="/foo/list/">foo Show all</a></div>'

  it "shows the notifications, error", ->
    get.and.callFake (req) ->
      d = $.Deferred()
      d.reject("foobar", "200", "foo error")  # failure
      return d.promise()

    tab.first().trigger "click"
    expect(get.calls.any()).toEqual true
    expect($(".js-notifications-content").html()).toEqual '<div>Error: 200, foo error</div>'

  it "shows tab content and is selected on click", ->
    expect(tab.first().hasClass "is-selected").toEqual false
    expect($(".js-notifications-content").is ":visible").toEqual false

    tab.first().trigger "click"
    expect(tab.first().hasClass "is-selected").toEqual true
    expect($(".js-notifications-content").is ":visible").toEqual true

  it "prevents the default click behaviour", ->
    event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    tab.first().trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()