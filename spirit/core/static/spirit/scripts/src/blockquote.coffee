###
    Expand blockquote instead of showing a scrollbar
###

# This is not re-calculated on resize, so
# in case the blockquote grows, the regular
# scrollbar will show; in case it shrinks, the
# expand will still show
stModules.blockquoteExpand = (elms) ->
  Array.from(elms).forEach((elm) ->
    # there's a polyfill, but I don't care about IE
    if not elm.after?
      return
    pos = elm.scrollTop
    elm.scrollTop += 1
    if pos != elm.scrollTop
      elm.scrollTop = pos
      elm.style.overflowY = 'hidden'
      expandButton = document.createElement('a')
      expandButton.href = '#'
      expandButton.innerHTML = '<i class="fa fa-chevron-down"></i>'
      expandButton.addEventListener('click', (e) =>
        e.preventDefault()
        e.stopPropagation()
        elm.style.maxHeight = 'none'
        expand.remove()
      )
      expand = document.createElement('div')
      expand.className = 'blockquote_expand'
      expand.appendChild(expandButton)
      elm.after(expand);
  )
  return
