describe "postify plugin tests", ->
  a_post = null
  plugin_postify = null
  Postify = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'postify.html'

    a_post = $('a.js-post').postify {csrfToken: "foobar", }
    plugin_postify = a_post.first().data 'plugin_postify'
    Postify = $.fn.postify.Postify

  it "doesnt break selector chaining", ->
    expect(a_post).toEqual $('.js-post')
    expect(a_post.length).toEqual 2

  it "prevents the default click behaviour on click", ->
    event = {type: 'click', stopPropagation: (->), preventDefault: (->)}
    stopPropagation = spyOn event, 'stopPropagation'
    preventDefault = spyOn event, 'preventDefault'

    spyOn plugin_postify, 'formSubmit'
    $(".js-post").first().trigger event
    expect(stopPropagation).toHaveBeenCalled()
    expect(preventDefault).toHaveBeenCalled()

  it "submits the form", ->
    formSubmit = spyOn plugin_postify, 'formSubmit'

    $('.js-post').first().trigger 'click'
    expect(formSubmit).toHaveBeenCalled()
    expect($("form").last().attr('action')).toEqual "/link1/"
    expect($("form").last().is ":visible").toEqual false
    expect($("input[name=csrfmiddlewaretoken]").val()).toEqual "foobar"