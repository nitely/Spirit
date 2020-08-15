"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

(function () {
  /*
      Generic tabs
  */
  var Tab;

  Tab = /*#__PURE__*/function () {
    function Tab(el) {
      _classCallCheck(this, Tab);

      this.tabSwitch = this.tabSwitch.bind(this);
      this.hideAllTabsContent = this.hideAllTabsContent.bind(this);
      this.unselectAllTabs = this.unselectAllTabs.bind(this);
      this.selectTab = this.selectTab.bind(this);
      this.showTabContent = this.showTabContent.bind(this);
      this.el = el;
      this.containerElm = this.el.closest(".js-tabs-container");
      this.setUp();
    }

    _createClass(Tab, [{
      key: "setUp",
      value: function setUp() {
        return this.el.addEventListener('click', this.tabSwitch);
      }
    }, {
      key: "tabSwitch",
      value: function tabSwitch(e) {
        e.preventDefault();
        e.stopPropagation();
        this.hideAllTabsContent();

        if (this.el.classList.contains('is-selected')) {
          this.el.classList.remove('is-selected');
        } else {
          this.unselectAllTabs();
          this.selectTab();
          this.showTabContent();
        }
      }
    }, {
      key: "hideAllTabsContent",
      value: function hideAllTabsContent() {
        var tabContentElms;
        tabContentElms = this.containerElm.querySelectorAll(".js-tab-content");
        return Array.from(tabContentElms).forEach(function (elm) {
          return elm.style.display = 'none';
        });
      }
    }, {
      key: "unselectAllTabs",
      value: function unselectAllTabs() {
        var tabElms;
        tabElms = this.containerElm.querySelectorAll(".js-tab");
        return Array.from(tabElms).forEach(function (elm) {
          return elm.classList.remove('is-selected');
        });
      }
    }, {
      key: "selectTab",
      value: function selectTab() {
        return this.el.classList.add('is-selected');
      }
    }, {
      key: "showTabContent",
      value: function showTabContent() {
        return this.containerElm.querySelector(this.el.dataset.related).style.display = 'block';
      }
    }]);

    return Tab;
  }();

  stModules.tab = function (elms) {
    return Array.from(elms).map(function (elm) {
      return new Tab(elm);
    });
  };

  stModules.Tab = Tab;
}).call(void 0);