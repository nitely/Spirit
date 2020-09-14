###
  Makes a parent element clickable,
  based on a child anchor element
###

defaults = {
  areaClass: '.js-clickable-area',
  areaTargetClass: '.js-clickable-area-target',
  targetColor: 'blue'
}

styles = (opts) ->
  """
  #{opts.areaClass}:hover #{opts.areaTargetClass} {
    color: #{opts.targetColor};
  }
  #{opts.areaClass} {
    cursor: pointer;
  }
  """

stModules.clickableArea = (opts) ->
  opts = Object.assign({}, defaults, opts)
  document.head.insertAdjacentHTML(
    "beforeend", "<style>#{styles(opts)}</style>")
  elms = document.querySelectorAll(opts.areaClass)
  Array.from(elms).forEach((elm) ->
    anchor = elm.querySelector(opts.areaTargetClass)
    if not anchor?.href?
      console.log('Anchor not found; skipping')
      return
    url = anchor.href
    elm.addEventListener('click', (e) =>
      e.preventDefault()
      e.stopPropagation()
      window.location.href = url
    )
    return
  )
  return
