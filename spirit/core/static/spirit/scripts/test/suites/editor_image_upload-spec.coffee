describe "editor image upload plugin tests", ->

    it "has correct meta data", ->
        ## Everything else is tested on editor_file_upload-spec
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

        editor = stModules.editorImageUpload(document.querySelectorAll('.js-reply'))[0]

        expect(editor.meta).toEqual({
            fieldName: "image",
            tag: "![{text}]({url})",
            elm: ".js-box-image"
        })
