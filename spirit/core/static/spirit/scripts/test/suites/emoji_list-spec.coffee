describe "editor plugin tests", ->

    it "returns the emoji list", ->
        expect(stModules.emojiList[0]).toEqual("+1")
