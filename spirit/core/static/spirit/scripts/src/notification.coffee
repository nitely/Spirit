###
    Notifications ajax tab
    requires: util.js, tab.js
###

utils = stModules.utils
Tab = stModules.Tab

# todo: short-polling (with back-off) and fetch notifications every time


class Notification

    defaults: {
        notificationUrl: "#ajax",
        notificationListUrl: "#show-all",
        mentionTxt: "{user} mention you on {topic}",
        commentTxt: "{user} has commented on {topic}",
        showAll: "Show all",
        empty: "Nothing to show",
        unread: "unread"
    }

    constructor: (el, options) ->
        @el = el
        @options = Object.assign({}, @defaults, options)
        @contentElm = document.querySelector(el.dataset.related)
        @setUp()

    setUp: ->
        @el.addEventListener('click', @tabSwitch)

    tabSwitch: (e) =>
        e.preventDefault()
        e.stopPropagation()

        # Detach the event so notification are fetched just once,
        # following clicks will show the cached notifications
        @el.removeEventListener('click', @tabSwitch)

        headers = new Headers()
        headers.append("X-Requested-With", "XMLHttpRequest")

        fetch(@options.notificationUrl, {
            method: "GET",
            headers: headers,
            credentials: 'same-origin'
        })
        .then((response) =>
            if not response.ok
                throw new Error("error: #{response.status} #{response.statusText}")

            return response.json()  # Promise
        )
        .then((data) =>
            if data.n.length > 0
                @addNotifications(data.n)
                @addShowMoreLink()
            else
                @addIsEmptyTxt()
        )
        .catch((error) =>
            console.log(error.message)
            @addErrorTxt(error.message)
        )
        .then( =>
            @ajaxDone()
        )

        return

    addNotifications: (notifications) =>
        notifications.forEach((n) =>
            # todo: actions should be pass in options as an object map
            if n.action is 1
                txt = @options.mentionTxt
            else
                txt = @options.commentTxt

            linkElm = document.createElement('a')
            linkElm.setAttribute('href', n.url)
            linkElm.textContent = n.title  # Untrusted

            txtElm = document.createElement('div')
            txtElm.innerHTML = utils.format(txt, {user: n.user, topic: linkElm.outerHTML})

            if not n.is_read
                unreadElm = document.createElement('span')
                unreadElm.className = 'row-unread'
                unreadElm.innerHTML = @options.unread

                txtElm.innerHTML += " "
                txtElm.appendChild(unreadElm)

            @contentElm.appendChild(txtElm)
            return
        )

    addShowMoreLink: =>
        showAllContainerElm = document.createElement('div')

        showAllLinkElm = document.createElement('a')
        showAllLinkElm.setAttribute('href', @options.notificationListUrl)
        showAllLinkElm.innerHTML = @options.showAll
        showAllContainerElm.appendChild(showAllLinkElm)

        @contentElm.appendChild(showAllContainerElm)

    addIsEmptyTxt: =>
        emptyElm = document.createElement('div')
        emptyElm.innerHTML = @options.empty
        @contentElm.appendChild(emptyElm)

    addErrorTxt: (message) =>
        ErrorElm = document.createElement('div')
        ErrorElm.textContent = message
        @contentElm.appendChild(ErrorElm)

    ajaxDone: =>
        @el.classList.add('js-tab')
        new Tab(@el)
        @el.click()


stModules.notification = (elms, options) ->
    return Array.from(elms).map((elm) -> new Notification(elm, options))

stModules.Notification = Notification
