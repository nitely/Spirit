describe "store plugin tests", ->
  textarea = null
  storage = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'store.html'

    do localStorage.clear
    textarea = $('#my-fixture').store 'unique-id'
    storage = textarea.data 'plugin_store'

  it "doesnt break selector chaining", ->
    expect(textarea).toEqual $('#my-fixture')

  it "loads previous stored value", ->
    localStorage['unique-id'] = "text"
    textarea = $('#my-fixture-2').store 'unique-id'
    expect(textarea).toHaveValue "text"

  it "updates the field on storage change", ->
    localStorage['unique-id'] = "text"
    $(window).trigger "storage"
    expect(textarea).toHaveValue "text"

  it "saves value to localStorage on input", ->
    textarea.val "foobar"
    textarea.trigger 'input'
    expect(localStorage['unique-id']).toEqual "foobar"

  it "wont (re)update the field on input", ->
    spyOn storage, 'updateField'
    textarea.trigger 'input'
    expect(storage.updateField.calls.count()).toEqual 0

  it "gets cleared on submit", ->
    localStorage['unique-id'] = "foo"
    submitCallback = jasmine.createSpy('submitCallback').and.returnValue false
    $form = $('form')
    $form.on 'submit', submitCallback
    $form.trigger "submit"
    expect('unique-id' of localStorage).toBe false
    expect(submitCallback).toHaveBeenCalled()