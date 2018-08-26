###
    HTML diff for the comment history
    requires modules, htmldiff
###

stModules.commentDiff = (elms) ->
    prev = null
    curr = null
    return Array.from(elms).forEach((elm) ->
        curr = elm.innerHTML

        if prev?
            elm.innerHTML = htmldiff(prev, curr)

        prev = curr;
    )
