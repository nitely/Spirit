###
  A bunch of generic functions, this are used by other plugins.
###

$ = jQuery


$.extend
  format: (str, kwargs) ->
    for key, value of kwargs
      str = str.replace "{#{key}}", String value

    return str