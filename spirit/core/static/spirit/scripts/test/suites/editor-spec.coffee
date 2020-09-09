describe "editor plugin tests", ->
    textarea = null
    editor = null

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

        editor = stModules.editor(document.querySelectorAll('.js-reply'), {
            boldedText: "foo bolded text",
            italicisedText: "foo italicised text",
            listItemText: "foo list item",
            linkText: "foo link text",
            linkUrlText: "foo link url",
            imageText: "foo image text",
            imageUrlText: "foo image url"
        })[0]
        textarea = document.querySelector('textarea')

    it "adds bold", ->
        document.querySelector('.js-box-bold').click()
        expect(textarea.value).toEqual("**foo bolded text**")

    it "adds italic", ->
        document.querySelector('.js-box-italic').click()
        expect(textarea.value).toEqual("*foo italicised text*")

    it "adds list", ->
        document.querySelector('.js-box-list').click()
        expect(textarea.value).toEqual("\n* foo list item")

    it "adds url", ->
        document.querySelector('.js-box-url').click()
        expect(textarea.value).toEqual("[foo link text](foo link url)")

    it "adds poll", ->
        document.querySelector('.js-box-poll').click()
        expected = "\n\n[poll name=1]\n# Title\n1. Description\n2. Description\n[/poll]\n"
        expect(textarea.value).toEqual(expected)

        # Increase name
        document.querySelector('.js-box-poll').click()
        expect(textarea.value).toEqual(
          expected + "\n\n[poll name=2]\n# Title\n1. Description\n2. Description\n[/poll]\n")

    it "adds image", ->
        document.querySelector('.js-box-image').click()
        expect(textarea.value).toEqual("![foo image text](foo image url)")

    it "adds all", ->
        document.querySelector('.js-box-bold').click()
        document.querySelector('.js-box-italic').click()
        document.querySelector('.js-box-list').click()
        document.querySelector('.js-box-url').click()
        document.querySelector('.js-box-image').click()
        document.querySelector('.js-box-file').click()
        expect(textarea.value).toEqual(
            "**foo bolded text***foo italicised text*" +
            "\n* foo list item[foo link text](foo link url)![foo image text](foo image url)")

    it "wraps the selected text, bold", ->
        textarea.value = "birfoobar"
        textarea.selectionStart = 3
        textarea.selectionEnd = 6

        document.querySelector('.js-box-bold').click()
        expect(textarea.value).toEqual("bir**foo**bar")

    it "wraps the selected text, italic", ->
        textarea.value = "birfoobar"
        textarea.selectionStart = 3
        textarea.selectionEnd = 6

        document.querySelector('.js-box-italic').click()
        expect(textarea.value).toEqual("bir*foo*bar")

    it "wraps the selected text, list", ->
        textarea.value = "birfoobar"
        textarea.selectionStart = 3
        textarea.selectionEnd = 6

        document.querySelector('.js-box-list').click()
        expect(textarea.value).toEqual("bir\n* foobar")

    it "wraps the selected text, url", ->
        textarea.value = "birfoobar"
        textarea.selectionStart = 3
        textarea.selectionEnd = 6

        document.querySelector('.js-box-url').click()
        expect(textarea.value).toEqual("bir[foo](foo link url)bar")

    it "wraps the selected text, image", ->
        textarea.value = "birfoobar"
        textarea.selectionStart = 3
        textarea.selectionEnd = 6

        document.querySelector('.js-box-image').click()
        expect(textarea.value).toEqual("bir![foo](foo image url)bar")

    # XXX marked uses module.export
    #     instead of global/window when defined
    ###
    it "shows html preview", ->
        textarea.value = "*foo*"
        document.querySelector('.js-box-preview').click()
        expect(textarea.style.display).toEqual('none')
        expect(document.querySelector('.js-box-preview-content').style.display).toEqual('block')
        expect(document.querySelector('.js-box-preview-content').innerHTML).toEqual(
          "<p><em>foo</em></p>\n")

        # clicking again should hide the preview and show the textarea
        document.querySelector('.js-box-preview').click()
        expect(textarea.style.display).toEqual('block')
        expect(document.querySelector('.js-box-preview-content').style.display).toEqual('none')
    ###
    # todo: test pointer location
