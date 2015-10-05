$ = jQuery


class Storage

  constructor: (el, lsKey) ->
    @el = $(el)
    @lsKey = lsKey
    do @setUp

  setUp: ->
    if not localStorage?
      return

    if @lsKey of localStorage
      do @updateField

    # localStorage on change
    $(window).on 'storage', @updateField

    @el.on 'input change propertychange', =>
      # storage gets triggered in the current tab/window in some browsers
      $(window).off 'storage', @updateField

      do @updateStorage

      $(window).on 'storage', @updateField
      return

    # This gets called for every el,
    # even if they belong to the same form,
    # it's ok though.
    $form = @el.closest "form"
    $form.on 'submit', @clearStorage

  updateStorage: =>
    value = do @el.val

    try
      # May trigger storage
      localStorage[@lsKey] = value
    catch err
      # The localStorage is probably full, nothing to do other than clear it
      do localStorage.clear

    return

  updateField: =>
    @el.val localStorage[@lsKey]
    return

  clearStorage: =>
    # Triggers storage
    delete localStorage[@lsKey]
    return


$.fn.extend
  store: (lsKey) ->
    @each ->
      if not $(@).data 'plugin_store'
        $(@).data 'plugin_store', new Storage(@, lsKey)

$.fn.store.Storage = Storage