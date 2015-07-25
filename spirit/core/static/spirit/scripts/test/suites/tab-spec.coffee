describe "tab plugin tests", ->
  tabs = null
  Tab = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'tab.html'

    tabs = $.tab()
    Tab = $.tab.Tab

  it "doesnt break selector chaining", ->
    expect(tabs).toEqual $('.js-tab')
    expect(tabs.length).toEqual 3

  it "selects the clicked tab", ->
    tabs.first().trigger 'click'
    expect(tabs.first().hasClass "is-selected").toEqual true

    tabs.last().trigger 'click'
    expect(tabs.last().hasClass "is-selected").toEqual true
    expect(tabs.first().hasClass "is-selected").toEqual false

  it "unselects the clicked tab if is selected", ->
    tabs.first().trigger 'click'
    expect(tabs.first().hasClass "is-selected").toEqual true

    tabs.first().trigger 'click'
    expect(tabs.first().hasClass "is-selected").toEqual false

  it "shows the clicked tab content", ->
    tab_content_first = tabs.first().data "related"
    expect($(tab_content_first).is ":visible").toEqual false

    tabs.first().trigger 'click'
    expect($(tab_content_first).is ":visible").toEqual true

    tab_content_last = tabs.last().data "related"
    expect($(tab_content_last).is ":visible").toEqual false

    tabs.last().trigger 'click'
    expect($(tab_content_last).is ":visible").toEqual true
    expect($(tab_content_first).is ":visible").toEqual false

  it "hides the clicked tab content if is selected", ->
    tab_content_first = tabs.first().data "related"
    expect($(tab_content_first).is ":visible").toEqual false

    tabs.first().trigger 'click'
    expect($(tab_content_first).is ":visible").toEqual true

    tabs.first().trigger 'click'
    expect($(tab_content_first).is ":visible").toEqual false

  it "prevents the default click behaviour", ->
    event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    tabs.first().trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()