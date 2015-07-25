describe "editor plugin tests", ->

  it "returns the emoji list", ->
    emojis = $.emoji_list()
    expect(emojis[0]).toEqual "+1"