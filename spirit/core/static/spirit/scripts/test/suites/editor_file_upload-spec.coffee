describe "editor file upload plugin tests", ->
    textarea = null
    post = null
    editor = null
    dialog = null
    responseData = null

    triggerFakeUpload = (name='foo.doc') ->
        inputFileOrg = editor.inputFile
        try
            editor.inputFile = {files: [{name: name}]}
            evt = document.createEvent("HTMLEvents")
            evt.initEvent("change", false, true)
            inputFileOrg.dispatchEvent(evt)
        finally
            editor.inputFile = inputFileOrg

    beforeEach ->
        document.body.innerHTML = """
        <form class="js-reply" action=".">
            <textarea id="id_comment"></textarea>
            <div class="js-box-preview-content" style="display:none;"></div>
            <ul>
                <li><a class="js-box-bold" href="#" title="Bold"></a></li>
                <li><a class="js-box-italic" href="#" title="Italic"></a></li>
                <li><a class="js-box-list" href="#" title="List"></a></li>
                <li><a class="js-box-url" href="#" title="URL"></a></li>
                <li><a class="js-box-image" href="#" title="Image"></a></li>
                <li><a class="js-box-file" href="#" title="File"></a></li>
                <li><a class="js-box-poll" href="#" title="Poll"></a></li>
                <li><a class="js-box-preview" href="#" title="Preview"></a></li>
            </ul>
        </form>
        """

        responseData = {url: '/path/foo'}

        post = spyOn(global, 'fetch')
        post.and.callFake( -> {
            then: (func) ->
                data = func({ok: true, json: -> responseData})
                return {
                    then: (func) ->
                        func(data)
                        return {
                            catch: -> return
                        }
                }
        })

        editor = stModules.editorFileUpload(document.querySelectorAll('.js-reply'), {
            csrfToken: "foo csrf_token",
            target: "/foo/",
            placeholderText: "foo uploading {name}",
            allowedFileMedia: ".doc,.docx,.pdf"
        })[0]
        textarea = document.querySelector('textarea')

        # Prevent popup
        dialog = spyOn(editor.inputFile, 'click')
        dialog.and.callFake( -> return)

    it "opens the file choose dialog", ->
        dialog.calls.reset()
        document.querySelector('.js-box-file').click()
        expect(dialog).toHaveBeenCalled()

    it "uploads the file", ->
        post.calls.reset()

        formDataMock = jasmine.createSpyObj('formDataMock', ['append', ])
        spyOn(global, "FormData").and.returnValue(formDataMock)

        triggerFakeUpload('foo.doc')
        expect(post.calls.any()).toEqual(true)
        expect(post.calls.argsFor(0)[0]).toEqual('/foo/')
        expect(post.calls.argsFor(0)[1].body).toEqual(formDataMock)
        expect(formDataMock.append).toHaveBeenCalledWith('csrfmiddlewaretoken', 'foo csrf_token')
        expect(formDataMock.append).toHaveBeenCalledWith('file', {name : 'foo.doc'})

    it "changes the placeholder on upload success", ->
        textarea.value = "foobar"
        triggerFakeUpload('foo.doc')
        expect(textarea.value).toEqual("foobar[foo.doc](/path/foo)")

    it "changes the placeholder on upload error", ->
        textarea.value = "foobar"
        responseData = {error: {foo: 'foo error'}}
        triggerFakeUpload('foo.doc')
        expect(textarea.value).toEqual('foobar[{"foo":"foo error"}]()')

    it "changes the placeholder on upload failure", ->
        post.calls.reset()
        textarea.value = "foobar"

        post.and.callFake( -> {
            then: (func) ->
                try
                    func({ok: false, status: 500, statusText: 'foo error'})
                catch err
                    return {
                        then: -> {
                            catch: (func) -> func(err)
                        }
                    }
        })
        log = spyOn(console, 'log')
        log.and.callFake( -> )

        triggerFakeUpload('foo.doc')
        expect(post.calls.any()).toEqual(true)
        expect(textarea.value).toEqual("foobar[error: 500 foo error]()")
        expect(log.calls.argsFor(0)[0]).toEqual('error: 500 foo error')

    it "checks for default media file extensions if none are provided", ->
        expect(editor.inputFile.accept).toEqual(".doc,.docx,.pdf")

    it "checks for custom media file extensions if they are provided", ->
        editor = stModules.editorFileUpload(document.querySelectorAll('.js-reply'), {
            allowedFileMedia: ".superdoc"
        })[0]
        expect(editor.inputFile.accept).toEqual(".superdoc")

    it "has correct meta data", ->
        expect(editor.meta).toEqual({
            fieldName: "file",
            tag: "[{text}]({url})",
            elm: ".js-box-file"
        })
