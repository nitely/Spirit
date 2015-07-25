describe "editor image upload plugin tests", ->
  textarea = null
  editorImageUpload = null
  data = null
  inputFile = null
  file = null
  post = null

  beforeEach ->
    fixtures = do jasmine.getFixtures
    fixtures.fixturesPath = 'base/test/fixtures/'
    loadFixtures 'editor.html'

    post = spyOn $, 'ajax'
    post.and.callFake (req) ->
      d = $.Deferred()
      d.resolve(data)  # success
      #d.reject()  # failure
      return d.promise()

    data =
      url: "/path/image.jpg"
    file =
      name: "foo.jpg"

    textarea = $('#id_comment').editor_image_upload {
      csrfToken: "foo csrf_token",
      target: "/foo/",
      placeholderText: "foo uploading {image_name}"
    }
    editorImageUpload = textarea.first().data 'plugin_editor_image_upload'
    inputFile = editorImageUpload.inputFile

  it "doesnt break selector chaining", ->
    expect(textarea).toEqual $('#id_comment')
    expect(textarea.length).toEqual 1

  it "does nothing if the browser is not supported", ->
    org_formData = window.FormData
    window.FormData = null
    try
      # remove event from beforeEach editor to prevent popup
      $(".js-box-image").off 'click'

      textarea2 = $('#id_comment2').editor_image_upload()
      inputFile2 = textarea2.data('plugin_editor_image_upload').inputFile

      trigger = spyOn inputFile2, 'trigger'
      $(".js-box-image").trigger 'click'
      expect(trigger).not.toHaveBeenCalled()
    finally
      window.FormData = org_formData

  it "opens the file choose dialog", ->
    trigger = spyOn inputFile, 'trigger'
    $(".js-box-image").trigger 'click'
    expect(trigger).toHaveBeenCalled()

  it "uploads the image", ->
    expect($.ajax.calls.any()).toEqual false

    formDataMock = jasmine.createSpyObj('formDataMock', ['append', ])
    spyOn(window, "FormData").and.returnValue formDataMock
    spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
    inputFile.trigger 'change'
    expect($.ajax.calls.any()).toEqual true
    expect($.ajax.calls.argsFor(0)).toEqual [ { url: '/foo/', data: formDataMock, processData: false, contentType: false, type: 'POST' } ]
    expect(formDataMock.append).toHaveBeenCalledWith('csrfmiddlewaretoken', 'foo csrf_token')
    expect(formDataMock.append).toHaveBeenCalledWith('image', { name : 'foo.jpg' })

  it "adds the placeholder", ->
    textarea.val "foobar"

    ajaxMock = jasmine.createSpyObj('ajax', ['done', 'fail'])
    post.and.returnValue ajaxMock

    spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
    inputFile.trigger 'change'
    expect(textarea.val()).toEqual "foobar![foo uploading foo.jpg]()"

  it "changes the placeholder on upload success", ->
    textarea.val "foobar"

    spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
    inputFile.trigger 'change'
    expect(textarea.val()).toEqual "foobar![foo.jpg](/path/image.jpg)"

  it "changes the placeholder on upload error", ->
    textarea.val "foobar"

    data =
      error: {foo: "foo error", }

    spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
    inputFile.trigger 'change'
    expect(textarea.val()).toEqual "foobar![{\"error\":{\"foo\":\"foo error\"}}]()"

  it "changes the placeholder on upload failure", ->
    textarea.val "foobar"

    d = $.Deferred()
    post.and.callFake (req) ->
      d.reject(null, "foo statusError", "bar error")  # failure
      return d.promise()

    spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
    inputFile.trigger 'change'
    expect(textarea.val()).toEqual "foobar![error: foo statusError bar error]()"