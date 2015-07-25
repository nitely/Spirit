describe "util format tests", ->

  it "formats a string", ->
    result = $.format "{foo} foobar {bar} {bad}", {foo: "foo text", bar: "bar text"}
    expect(result).toEqual "foo text foobar bar text {bad}"