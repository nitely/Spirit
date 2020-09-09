
/*
    Notifications ajax tab
    requires: util.js, tab.js
 */

(function() {
  var Notification, Tab, utils,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  utils = stModules.utils;

  Tab = stModules.Tab;

  Notification = (function() {
    Notification.prototype.defaults = {
      notificationUrl: "#ajax",
      notificationListUrl: "#show-all",
      mentionTxt: "{user} mention you on {topic}",
      commentTxt: "{user} has commented on {topic}",
      showAll: "Show all",
      empty: "Nothing to show",
      unread: "unread"
    };

    function Notification(el, options) {
      this.ajaxDone = bind(this.ajaxDone, this);
      this.addErrorTxt = bind(this.addErrorTxt, this);
      this.addIsEmptyTxt = bind(this.addIsEmptyTxt, this);
      this.addShowMoreLink = bind(this.addShowMoreLink, this);
      this.addNotifications = bind(this.addNotifications, this);
      this.tabSwitch = bind(this.tabSwitch, this);
      this.el = el;
      this.options = Object.assign({}, this.defaults, options);
      this.contentElm = document.querySelector(el.dataset.content);
      this.NotificationsElm = document.createElement('ul');
      this.setUp();
    }

    Notification.prototype.setUp = function() {
      return this.el.addEventListener('click', this.tabSwitch);
    };

    Notification.prototype.tabSwitch = function(e) {
      var headers;
      e.preventDefault();
      e.stopPropagation();
      this.el.removeEventListener('click', this.tabSwitch);
      headers = new Headers();
      headers.append("X-Requested-With", "XMLHttpRequest");
      fetch(this.options.notificationUrl, {
        method: "GET",
        headers: headers,
        credentials: 'same-origin'
      }).then((function(_this) {
        return function(response) {
          if (!response.ok) {
            throw new Error("error: " + response.status + " " + response.statusText);
          }
          return response.json();
        };
      })(this)).then((function(_this) {
        return function(data) {
          if (data.n.length > 0) {
            _this.addNotifications(data.n);
            _this.addShowMoreLink();
            return _this.contentElm.appendChild(_this.NotificationsElm);
          } else {
            return _this.addIsEmptyTxt();
          }
        };
      })(this))["catch"]((function(_this) {
        return function(error) {
          console.log(error.message);
          return _this.addErrorTxt(error.message);
        };
      })(this)).then((function(_this) {
        return function() {
          return _this.ajaxDone();
        };
      })(this));
    };

    Notification.prototype.addNotifications = function(notifications) {
      return notifications.forEach((function(_this) {
        return function(n) {
          var linkElm, txt, txtElm, unreadElm;
          if (n.action === 1) {
            txt = _this.options.mentionTxt;
          } else {
            txt = _this.options.commentTxt;
          }
          linkElm = document.createElement('a');
          linkElm.setAttribute('href', n.url);
          linkElm.textContent = utils.format(txt, {
            user: n.user,
            topic: n.title
          });
          if (!n.is_read) {
            unreadElm = document.createElement('span');
            unreadElm.className = 'unread';
            unreadElm.innerHTML = _this.options.unread;
            linkElm.innerHTML += " ";
            linkElm.appendChild(unreadElm);
          }
          txtElm = document.createElement('li');
          txtElm.innerHTML = linkElm.outerHTML;
          _this.NotificationsElm.appendChild(txtElm);
        };
      })(this));
    };

    Notification.prototype.addShowMoreLink = function() {
      var showAllContainerElm, showAllLinkElm;
      showAllContainerElm = document.createElement('li');
      showAllLinkElm = document.createElement('a');
      showAllLinkElm.setAttribute('href', this.options.notificationListUrl);
      showAllLinkElm.innerHTML = this.options.showAll;
      showAllContainerElm.appendChild(showAllLinkElm);
      return this.NotificationsElm.appendChild(showAllContainerElm);
    };

    Notification.prototype.addIsEmptyTxt = function() {
      var emptyElm;
      emptyElm = document.createElement('div');
      emptyElm.innerHTML = this.options.empty;
      return this.contentElm.appendChild(emptyElm);
    };

    Notification.prototype.addErrorTxt = function(message) {
      var ErrorElm;
      ErrorElm = document.createElement('div');
      ErrorElm.textContent = message;
      return this.contentElm.appendChild(ErrorElm);
    };

    Notification.prototype.ajaxDone = function() {
      this.el.classList.add('js-tab');
      new Tab(this.el);
      return this.el.click();
    };

    return Notification;

  })();

  stModules.notification = function(elms, options) {
    return Array.from(elms).map(function(elm) {
      return new Notification(elm, options);
    });
  };

  stModules.Notification = Notification;

}).call(this);
