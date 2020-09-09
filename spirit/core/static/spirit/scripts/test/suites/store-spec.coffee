describe "store plugin tests", ->
    textarea = null
    storage = null

    beforeEach ->
        document.body.innerHTML = """
        <form action=".">
          <textarea id="my-fixture"></textarea>
          <textarea id="my-fixture-2"></textarea>
        </form>
        """

        localStorage.clear()
        textarea = document.querySelector('#my-fixture')
        storage = stModules.store(textarea, 'unique-id')

    it "loads previous stored value", ->
        localStorage.setItem('unique-id', "text")
        textarea = document.querySelector('#my-fixture-2')
        stModules.store(textarea, 'unique-id')
        expect(textarea.value).toEqual("text")

    it "updates the field on storage change", ->
        # Some browsers won't trigger "storage" on assignments
        localStorage.setItem('unique-id', "text")

        evt = document.createEvent("HTMLEvents")
        evt.initEvent("storage", false, true)
        window.dispatchEvent(evt)

        expect(textarea.value).toEqual("text")

    it "saves value to localStorage on input", ->
        textarea.value = "foobar"
        expect(localStorage.getItem('unique-id')).toEqual(null)

        evt = document.createEvent("HTMLEvents")
        evt.initEvent("input", false, true)
        textarea.dispatchEvent(evt)

        expect(localStorage.getItem('unique-id')).toEqual("foobar")

    it "wont (re)update the field on input", ->
        # "storage" gets triggered (maybe) while updating the Storage,
        # however this should not (re)update the text-area

        localStorage.setItem('unique-id', "no-foobar")
        textarea.value = "foobar"

        setItem = spyOn(window.Storage.prototype, 'setItem')
        setItem.and.callFake( ->
            # Force storage event
            evt = document.createEvent("HTMLEvents")
            evt.initEvent("storage", false, true)
            window.dispatchEvent(evt)
        )

        evt = document.createEvent("HTMLEvents")
        evt.initEvent("input", false, true)
        textarea.dispatchEvent(evt)

        expect(setItem.calls.count()).toEqual(1)
        expect(localStorage.getItem('unique-id')).toEqual("no-foobar")
        expect(textarea.value).toEqual("foobar")

    it "gets cleared on submit", ->
        localStorage.setItem('unique-id', "text")

        form = document.querySelector('form')
        form.addEventListener('submit', (e) -> e.preventDefault())
        evt = document.createEvent("HTMLEvents")
        evt.initEvent("submit", false, true)
        form.dispatchEvent(evt)

        expect(localStorage.getItem('unique-id')).toEqual(null)
