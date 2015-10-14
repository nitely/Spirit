describe "messages plugin tests", ->
  Messages = null

  beforeEach ->
    fixtures = jasmine.getFixtures()
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures('messages.html')

    Messages = $.fn.messages.Messages

  it "doesnt break selector chaining", ->
    messages = $('.js-messages-dummy').messages()
    expect(messages).toEqual($('.js-messages-dummy'))
    expect(messages.length).toEqual(2)

  it "does nothing when no hash", ->
    messages = $('.js-messages').messages()
    expect(messages.hasClass('is-fixed')).toEqual(false)
    expect($('.js-message-close').is(":hidden")).toEqual(true)

  it "places the messages when there is a hash", ->
    org_location_hash = window.location.hash
    try
      window.location.hash = "#p1"
      messages = $('.js-messages').messages()
      expect(messages.hasClass('is-fixed')).toEqual(true)
    finally
      window.location.hash = org_location_hash
