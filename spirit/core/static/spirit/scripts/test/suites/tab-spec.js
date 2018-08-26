(function() {
  describe("tab plugin tests", function() {
    var Tab, tabElms, tabs;
    tabElms = null;
    tabs = null;
    Tab = null;
    beforeEach(function() {
      var fixtures;
      fixtures = jasmine.getFixtures();
      fixtures.fixturesPath = 'base/test/fixtures/';
      loadFixtures('tab.html');
      tabElms = document.querySelectorAll('.js-tab');
      tabs = stModules.tab(tabElms);
      return Tab = stModules.Tab;
    });
    it("selects the clicked tab", function() {
      tabElms[0].click();
      expect(tabElms[0].classList.contains('is-selected')).toEqual(true);
      tabElms[tabElms.length - 1].click();
      expect(tabElms[tabElms.length - 1].classList.contains('is-selected')).toEqual(true);
      return expect(tabElms[0].classList.contains('is-selected')).toEqual(false);
    });
    it("unselects the clicked tab if is selected", function() {
      tabElms[0].click();
      expect(tabElms[0].classList.contains('is-selected')).toEqual(true);
      tabElms[0].click();
      return expect(tabElms[0].classList.contains('is-selected')).toEqual(false);
    });
    it("shows the clicked tab content", function() {
      var tab_content_first, tab_content_last;
      tab_content_first = document.querySelector(tabElms[0].dataset.related);
      expect(tab_content_first.style.display).toEqual('none');
      tabElms[0].click();
      expect(tab_content_first.style.display).toEqual('block');
      tab_content_last = document.querySelector(tabElms[tabElms.length - 1].dataset.related);
      expect(tab_content_last.style.display).toEqual('none');
      tabElms[tabElms.length - 1].click();
      expect(tab_content_last.style.display).toEqual('block');
      return expect(tab_content_first.style.display).toEqual('none');
    });
    it("hides the clicked tab content if is selected", function() {
      var tab_content_first;
      tab_content_first = document.querySelector(tabElms[0].dataset.related);
      expect(tab_content_first.style.display).toEqual('none');
      tabElms[0].click();
      expect(tab_content_first.style.display).toEqual('block');
      tabElms[0].click();
      return expect(tab_content_first.style.display).toEqual('none');
    });
    return it("prevents the default click behaviour", function() {
      var evt, preventDefault, stopPropagation;
      evt = document.createEvent("HTMLEvents");
      evt.initEvent("click", false, true);
      stopPropagation = spyOn(evt, 'stopPropagation');
      preventDefault = spyOn(evt, 'preventDefault');
      tabElms[0].dispatchEvent(evt);
      expect(stopPropagation).toHaveBeenCalled();
      return expect(preventDefault).toHaveBeenCalled();
    });
  });

}).call(this);

//# sourceMappingURL=tab-spec.js.map
