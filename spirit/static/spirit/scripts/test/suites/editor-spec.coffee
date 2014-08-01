describe "editor plugin tests", ->
  textarea = null
  editor = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'editor.html'

    textarea = $('#id_comment').editor {
      boldedText: "foo bolded text",
      italicisedText: "foo italicised text",
      listItemText: "foo list item",
      linkText: "foo link text",
      linkUrlText: "foo link url",
      imageText: "foo image text",
      imageUrlText: "foo image url"
    }
    editor = textarea.data 'plugin_editor'

  it "doesnt break selector chaining", ->
    expect(textarea).toEqual $('#id_comment')
    expect(textarea.length).toEqual 1

  it "adds bold", ->
    $('.js-box-bold').trigger 'click'
    expect(textarea.val()).toEqual "**foo bolded text**"

  it "adds italic", ->
    $('.js-box-italic').trigger 'click'
    expect(textarea.val()).toEqual "*foo italicised text*"

  it "adds list", ->
    $('.js-box-list').trigger 'click'
    expect(textarea.val()).toEqual "\n* foo list item"

  it "adds url", ->
    $('.js-box-url').trigger 'click'
    expect(textarea.val()).toEqual "[foo link text](foo link url)"

  it "adds image", ->
    $('.js-box-image').trigger 'click'
    expect(textarea.val()).toEqual "![foo image text](foo image url)"

  it "adds all", ->
    $('.js-box-bold').trigger 'click'
    $('.js-box-italic').trigger 'click'
    $('.js-box-list').trigger 'click'
    $('.js-box-url').trigger 'click'
    $('.js-box-image').trigger 'click'
    expect(textarea.val()).toEqual "![foo image text](foo image url)[foo link text](foo link url)\n* foo list item*foo italicised text***foo bolded text**"

  it "wraps the selected text, bold", ->
    textarea.val "birfoobar"
    textarea.first()[0].selectionStart = 3
    textarea.first()[0].selectionEnd = 6

    $('.js-box-bold').trigger 'click'
    expect(textarea.val()).toEqual "bir**foo**bar"

  it "wraps the selected text, italic", ->
    textarea.val "birfoobar"
    textarea.first()[0].selectionStart = 3
    textarea.first()[0].selectionEnd = 6

    $('.js-box-italic').trigger 'click'
    expect(textarea.val()).toEqual "bir*foo*bar"

  it "wraps the selected text, list", ->
    textarea.val "birfoobar"
    textarea.first()[0].selectionStart = 3
    textarea.first()[0].selectionEnd = 6

    $('.js-box-list').trigger 'click'
    expect(textarea.val()).toEqual "bir\n* foobar"

  it "wraps the selected text, url", ->
    textarea.val "birfoobar"
    textarea.first()[0].selectionStart = 3
    textarea.first()[0].selectionEnd = 6

    $('.js-box-url').trigger 'click'
    expect(textarea.val()).toEqual "bir[foo](foo link url)bar"

  it "wraps the selected text, image", ->
    textarea.val "birfoobar"
    textarea.first()[0].selectionStart = 3
    textarea.first()[0].selectionEnd = 6

    $('.js-box-image').trigger 'click'
    expect(textarea.val()).toEqual "bir![foo](foo image url)bar"

  it "shows html preview", ->
    textarea.val "*foo*"
    $('.js-box-preview').trigger 'click'
    expect(textarea.is ":visible").toEqual false
    expect($(".js-box-preview-content").is ":visible").toEqual true
    expect($(".js-box-preview-content").html()).toEqual "<p><em>foo</em></p>\n"

    # clicking again should hide the preview and show the textarea
    $('.js-box-preview').trigger 'click'
    expect(textarea.is ":visible").toEqual true
    expect($(".js-box-preview-content").is ":visible").toEqual false