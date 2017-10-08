describe "editor image upload plugin tests", ->

    it "has correct meta data", ->
        ## Everything else is tested on editor_file_upload-spec
        fixtures = jasmine.getFixtures()
        fixtures.fixturesPath = 'base/test/fixtures/'
        loadFixtures('editor.html')

        editor = stModules.editorImageUpload(document.querySelectorAll('.js-reply'))[0]

        expect(editor.meta).toEqual({
            fieldName: "image",
            tag: "![{text}]({url})",
            elm: ".js-box-image"
        })
