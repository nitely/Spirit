describe "editor file upload plugin tests", ->
    textarea = null
    editorFileUpload = null
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
            url: "/path/file.pdf"
        file =
            name: "foo.pdf"

        textarea = $('#id_comment').editor_file_upload {
            csrfToken: "foo csrf_token",
            target: "/foo/",
            placeholderText: "foo uploading {name}",
            allowedFileMedia: ".doc,.docx,.pdf"
        }
        editorFileUpload = textarea.first().data 'plugin_editor_file_upload'
        inputFile = editorFileUpload.inputFile

    it "doesnt break selector chaining", ->
        expect(textarea).toEqual $('#id_comment')
        expect(textarea.length).toEqual 1

    it "does nothing if the browser is not supported", ->
        org_formData = window.FormData
        window.FormData = null
        try
            # remove event from beforeEach editor to prevent popup
            $(".js-box-file").off 'click'

            textarea2 = $('#id_comment2').editor_file_upload()
            inputFile2 = textarea2.data('plugin_editor_file_upload').inputFile

            trigger = spyOn inputFile2, 'trigger'
            $(".js-box-file").trigger 'click'
            expect(trigger).not.toHaveBeenCalled()
        finally
            window.FormData = org_formData

    it "opens the file choose dialog", ->
        trigger = spyOn inputFile, 'trigger'
        $(".js-box-file").trigger 'click'
        expect(trigger).toHaveBeenCalled()

    it "uploads the file", ->
        expect($.ajax.calls.any()).toEqual false

        formDataMock = jasmine.createSpyObj('formDataMock', ['append', ])
        spyOn(window, "FormData").and.returnValue formDataMock
        spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
        inputFile.trigger 'change'
        expect($.ajax.calls.any()).toEqual true
        expect($.ajax.calls.argsFor(0)).toEqual [ { url: '/foo/', data: formDataMock, processData: false, contentType: false, type: 'POST' } ]
        expect(formDataMock.append).toHaveBeenCalledWith('csrfmiddlewaretoken', 'foo csrf_token')
        expect(formDataMock.append).toHaveBeenCalledWith('file', { name : 'foo.pdf' })

    it "changes the placeholder on upload success", ->
        textarea.val "foobar"

        spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
        inputFile.trigger 'change'
        expect(textarea.val()).toEqual "foobar[foo.pdf](/path/file.pdf)"

    it "changes the placeholder on upload error", ->
        textarea.val "foobar"

        data =
            error: {foo: "foo error", }

        spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
        inputFile.trigger 'change'
        expect(textarea.val()).toEqual "foobar[{\"error\":{\"foo\":\"foo error\"}}]()"

    it "changes the placeholder on upload failure", ->
        textarea.val "foobar"

        d = $.Deferred()
        post.and.callFake (req) ->
            d.reject(null, "foo statusError", "bar error")  # failure
            return d.promise()

        spyOn(inputFile, 'get').and.returnValue {files: [file, ]}
        inputFile.trigger 'change'
        expect(textarea.val()).toEqual "foobar[error: foo statusError bar error]()"

    it "checks for default media file extensions if none are provided", ->
        expect(inputFile[0].outerHTML).toContain(".doc,.docx,.pdf")

    it "checks for custom media file extensions if they are provided", ->
        textarea3 = $('#id_comment3').editor_file_upload {
            csrfToken: "foo csrf_token",
            target: "/foo/",
            placeholderText: "foo uploading {file_name}"
            allowedFileMedia: [".superdoc"]
        }
        editorFileUpload3 = textarea3.first().data 'plugin_editor_file_upload'
        inputFile3 = editorFileUpload3.inputFile
        expect(inputFile3[0].outerHTML).not.toContain(".doc,.docx,.pdf")
        expect(inputFile3[0].outerHTML).toContain(".superdoc")
