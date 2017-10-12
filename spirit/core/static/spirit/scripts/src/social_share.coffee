###
    Social share popup
###


class SocialShare

    constructor: (el) ->
        @el = el
        @dialog = document.querySelector(@el.dataset.dialog)
        @allDialogs = document.querySelectorAll('.share')
        @setUp()

    setUp: ->
        @el.addEventListener('click', @showDialog)
        @dialog.querySelector('.share-close').addEventListener('click', @closeDialog)

        shareInput = @dialog.querySelector('.share-url')
        shareInput.addEventListener('focus', @select)
        # Hijack click, so it gets always selected
        shareInput.addEventListener('mouseup', @stopEvent)

    showDialog: (e) =>
        e.preventDefault()
        e.stopPropagation()

        Array.from(@allDialogs).forEach((elm) ->
            elm.style.display = 'none'
        )
        @dialog.style.display = 'block'
        return

    closeDialog: (e) =>
        e.preventDefault()
        e.stopPropagation()

        @dialog.style.display = 'none'
        return

    select: (e) ->
        e.preventDefault()
        e.stopPropagation()

        @.setSelectionRange(0, @.value.length - 1)
        return

    stopEvent: (e) ->
        e.preventDefault()
        e.stopPropagation()
        return


stModules.socialShare = (elms) ->
    return Array.from(elms).map((elm) -> new SocialShare(elm))

stModules.SocialShare = SocialShare
