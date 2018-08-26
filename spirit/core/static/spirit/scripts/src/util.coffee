###
  A bunch of generic functions, this are used by other plugins.
###


stModules.utils = {
    format: (str, kwargs) ->
        for key, value of kwargs
            str = str.replace("{#{key}}", String(value))

        return str
    isHidden: (elms) ->
        return Array.from(elms).filter((elm) -> elm.style.display != 'none').length == 0
}
