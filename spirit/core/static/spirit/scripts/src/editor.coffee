###
    Markdown editor
    requires: marked.js
###

$ = jQuery


class Editor

    defaults: {
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
        @el = $(el)
        @options = $.extend({}, @defaults, options)
        @pollCounter = 1
        @setUp()

    setUp: ->
        # TODO: fixme, having multiple editor
        # in the same page will trigger button
        # click on every editor
        $('.js-box-bold').on('click', @addBold)
        $('.js-box-italic').on('click', @addItalic)
        $('.js-box-list').on('click', @addList)
        $('.js-box-url').on('click', @addUrl)
        $('.js-box-image').on('click', @addImage)
        $('.js-box-poll').on('click', @addPoll)
        $('.js-box-preview').on('click', @togglePreview)
        $('.js-reply-button').on('click', @replyButton)

    wrapSelection: (preTxt, postTxt, defaultTxt) =>
        preSelection = @el
            .val()
            .substring(0, @el[0].selectionStart)
        selection = @el
            .val()
            .substring(@el[0].selectionStart, @el[0].selectionEnd)
        postSelection = @el
            .val()
            .substring(@el[0].selectionEnd)

        if not selection
            selection = defaultTxt

        @el.val(preSelection + preTxt + selection + postTxt + postSelection)

    addBold: =>
        @wrapSelection("**", "**", @options.boldedText)
        $('#id_comment').focus()
        return false

    addItalic: =>
        @wrapSelection("*", "*", @options.italicisedText)
        $('#id_comment').focus()
        return false

    addList: =>
        @wrapSelection("\n* ", "", @options.listItemText)
        $('#id_comment').focus()
        return false

    addUrl: =>
        @wrapSelection("[", "](#{ @options.linkUrlText })", @options.linkText)
        $('#id_comment').focus()
        return false

    addImage: =>
        @wrapSelection("![", "](#{ @options.imageUrlText })", @options.imageText)
        $('#id_comment').focus()
        return false

    addPoll: =>
        poll = "\n\n[poll name=#{@pollCounter}]\n" +
            "# #{@options.pollTitleText}\n" +
            "1. #{@options.pollChoiceText}\n" +
            "2. #{@options.pollChoiceText}\n" +
            "[/poll]\n"
        @wrapSelection("", poll, "")  # todo: append to current pointer position
        @pollCounter++
        $('#id_comment').focus()
        return false

    togglePreview: =>
        $preview = $('.js-box-preview-content')

        @el.toggle()
        $preview.toggle()
        $preview.html(marked(@el.val()))

        return false

    replyButton: (e) =>
        @wrapSelection(" ", " ", $(e.currentTarget).attr("data"))
        $('#id_comment').focus()
        return false


$.fn.extend
    editor: (options) ->
        @each( ->
            if not $(@).data('plugin_editor')
                $(@).data('plugin_editor', new Editor(@, options))
        )

$.fn.editor.Editor = Editor
