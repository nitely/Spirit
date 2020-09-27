
/*
    Generic tabs
 */

(function() {
  var Tab,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  Tab = (function() {
    function Tab(el) {
      this.showTabContent = bind(this.showTabContent, this);
      this.selectTab = bind(this.selectTab, this);
      this.unselectAllTabs = bind(this.unselectAllTabs, this);
      this.hideAllTabsContent = bind(this.hideAllTabsContent, this);
      this.tabSwitch = bind(this.tabSwitch, this);
      this.el = el;
      this.containerElm = this.el.closest(".js-tabs-container");
      this.setUp();
    }

    Tab.prototype.setUp = function() {
      return this.el.addEventListener('click', this.tabSwitch);
    };

    Tab.prototype.tabSwitch = function(e) {
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
    };

    Tab.prototype.hideAllTabsContent = function() {
      var tabContentElms;
      tabContentElms = this.containerElm.querySelectorAll(".js-tab-content");
      return Array.from(tabContentElms).forEach(function(elm) {
        return elm.style.display = 'none';
      });
    };

    Tab.prototype.unselectAllTabs = function() {
      var tabElms;
      tabElms = this.containerElm.querySelectorAll(".js-tab");
      return Array.from(tabElms).forEach(function(elm) {
        return elm.classList.remove('is-selected');
      });
    };

    Tab.prototype.selectTab = function() {
      return this.el.classList.add('is-selected');
    };

    Tab.prototype.showTabContent = function() {
      var ref;
      this.containerElm.querySelector(this.el.dataset.related).style.removeProperty('display');
      return (ref = this.containerElm.querySelector(this.el.dataset.related).querySelector('input')) != null ? ref.focus() : void 0;
    };

    return Tab;

  })();

  stModules.tab = function(elms) {
    return Array.from(elms).map(function(elm) {
      return new Tab(elm);
    });
  };

  stModules.Tab = Tab;

}).call(this);
