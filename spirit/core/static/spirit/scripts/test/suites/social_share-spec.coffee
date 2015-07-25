describe "social-share plugin tests", ->
  social_share = null
  SocialShare = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'social_share.html'

    social_share = $('.js-share').social_share()
    SocialShare = $.fn.social_share.SocialShare

  it "doesnt break selector chaining", ->
    expect(social_share).toEqual $('.js-share')
    expect(social_share.length).toEqual 2

  it "shows the share dialog", ->
    expect($('.test-1').is ":visible").toEqual false
    social_share.first().trigger 'click'
    expect($('.test-1').is ":visible").toEqual true
    expect($('.test-2').is ":visible").toEqual false

    social_share.last().trigger 'click'
    expect($('.test-2').is ":visible").toEqual true
    expect($('.test-1').is ":visible").toEqual false

  it "prevents the default click behaviour on share click", ->
    event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    social_share.first().trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()

  it "closes the dialog", ->
    social_share.first().trigger 'click'
    expect($('.test-1').is ":visible").toEqual true

    $('.test-1').find('.share-close').trigger 'click'
    expect($('.test-1').is ":visible").toEqual false

  it "prevents the default click behaviour on close dialog", ->
    event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    $('.test-1').find('.share-close').trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()

  it "auto selects the share link on focus", ->
    social_share.first().trigger 'click'
    $shareInput = $('.test-1').find('.share-url')
    $shareInput.trigger 'focus'

    #selection = $shareInput.val().substring $shareInput[0].selectionStart, $shareInput[0].selectionEnd

    #expect(selection).toEqual "link"
    #TODO: test, override SocialShare.select

  it "prevents the default behaviour on input mouseup", ->
    event = {type: 'mouseup', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    $('.test-1').find('.share-url').trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()