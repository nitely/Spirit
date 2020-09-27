###
    Markdown editor
    requires: modules, marked.js
###


class Editor

    defaults: {
        replyButtons: [],
        boldedText: "bolded text",
        italicisedText: "italicised text",
        listItemText: "list item",
        linkText: "link text",
        linkUrlText: "link url",
        imageText: "image text",
        imageUrlText: "image url",
        pollTitleText: "Title",
        pollChoiceText: "Description"
    }

    constructor: (el, options) ->
        @el = el
        @options = Object.assign({}, @defaults, options)
        @textBox = el.querySelector('textarea')
        @preview = el.querySelector('.js-box-preview-content')
        @pollCounter = 1
        @isPreviewOn = false
        @setUp()

    setUp: ->
        @el.querySelector('.js-box-bold').addEventListener('click', @addBold)
        @el.querySelector('.js-box-italic').addEventListener('click', @addItalic)
        @el.querySelector('.js-box-list').addEventListener('click', @addList)
        @el.querySelector('.js-box-url').addEventListener('click', @addUrl)
        @el.querySelector('.js-box-image').addEventListener('click', @addImage)
        @el.querySelector('.js-box-poll').addEventListener('click', @addPoll)
        @el.querySelector('.js-box-preview').addEventListener('click', @togglePreview)
        for elm in @options.replyButtons
            elm.addEventListener('click', @replyButton)

    wrapSelection: (preTxt, postTxt, defaultTxt) =>
        preSelection = @textBox.value.substring(0, @textBox.selectionStart)
        selection = @textBox.value.substring(@textBox.selectionStart, @textBox.selectionEnd)
        postSelection = @textBox.value.substring(@textBox.selectionEnd)

        if not selection
            selection = defaultTxt

        @textBox.value = preSelection + preTxt + selection + postTxt + postSelection

        # Set pointer location and give focus back
        # Works well on mobile Chrome and Firefox
        pointerLocation = @textBox.value.length - postSelection.length
        @textBox.setSelectionRange(pointerLocation, pointerLocation)
        @textBox.focus()

    addBold: (e) =>
        @wrapSelection("**", "**", @options.boldedText)
        @stopClick(e)

    addItalic: (e) =>
        @wrapSelection("*", "*", @options.italicisedText)
        @stopClick(e)

    addList: (e) =>
        @wrapSelection("\n* ", "", @options.listItemText)
        @stopClick(e)

    addUrl: (e) =>
        @wrapSelection("[", "](#{ @options.linkUrlText })", @options.linkText)
        @stopClick(e)

    addImage: (e) =>
        @wrapSelection("![", "](#{ @options.imageUrlText })", @options.imageText)
        @stopClick(e)

    addPoll: (e) =>
        poll = "\n\n[poll name=#{@pollCounter}]\n" +
            "# #{@options.pollTitleText}\n" +
            "1. #{@options.pollChoiceText}\n" +
            "2. #{@options.pollChoiceText}\n" +
            "[/poll]\n"
        @wrapSelection("", poll, "")  # todo: append to current pointer position
        @pollCounter++
        @stopClick(e)

    togglePreview: (e) =>
        if @isPreviewOn
            @isPreviewOn = false
            @textBox.style.display = 'block'
            @preview.style.display = 'none'
        else
            @isPreviewOn = true
            @textBox.style.display = 'none'
            @preview.style.display = 'block'
            @preview.innerHTML = marked(@textBox.value)

        @stopClick(e)

    replyButton: (e) =>
        window.location.hash = 'reply'
        @wrapSelection("", ", ", e.currentTarget.getAttribute('data'))
        @stopClick(e)

    stopClick: (e) ->
        e.preventDefault()
        e.stopPropagation()


stModules.editor = (elms, options) ->
    return Array.from(elms).map((elm) -> new Editor(elm, options))

stModules.Editor = Editor
