(function() {
  describe("tab plugin tests", function() {
    var Tab, tabElms, tabs;
    tabElms = null;
    tabs = null;
    Tab = null;
    beforeEach(function() {
      document.body.innerHTML = "<div class=\"js-tabs-container\">\n  <ul>\n    <li><a class=\"js-tab\" href=\"#\" data-related=\".js-search-content\">t1</a></li>\n    <li><a class=\"js-tab\" href=\"#\" data-related=\".js-notifications-content\">t2</a></li>\n    <li><a class=\"js-tab\" href=\"#\" data-related=\".js-user-content\">t3</a></li>\n  </ul>\n  <div class=\"js-tab-content js-user-content\" style=\"display:none;\"></div>\n  <div class=\"js-tab-content js-notifications-content\" style=\"display:none;\"></div>\n  <div class=\"js-tab-content js-search-content\" style=\"display:none;\"></div>\n</div>";
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
      expect(tab_content_first.style.display).toEqual('');
      tab_content_last = document.querySelector(tabElms[tabElms.length - 1].dataset.related);
      expect(tab_content_last.style.display).toEqual('none');
      tabElms[tabElms.length - 1].click();
      expect(tab_content_last.style.display).toEqual('');
      return expect(tab_content_first.style.display).toEqual('none');
    });
    it("hides the clicked tab content if is selected", function() {
      var tab_content_first;
      tab_content_first = document.querySelector(tabElms[0].dataset.related);
      expect(tab_content_first.style.display).toEqual('none');
      tabElms[0].click();
      expect(tab_content_first.style.display).toEqual('');
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
