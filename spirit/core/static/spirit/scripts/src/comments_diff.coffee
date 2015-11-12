###
    HTML diff for the comment history
    requires htmldiff
###

$ = jQuery


$.fn.extend
    comment_diff: ->
        prev = null
        curr = null

        @each( ->
            curr = $(@).html()

            if prev?
                diff = htmldiff(prev, curr)
                $(@).html(diff)

            prev = curr;
        )
