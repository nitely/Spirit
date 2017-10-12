
/*
    Social share popup
 */

(function() {
  var SocialShare,
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  SocialShare = (function() {
    function SocialShare(el) {
      this.closeDialog = bind(this.closeDialog, this);
      this.showDialog = bind(this.showDialog, this);
      this.el = el;
      this.dialog = document.querySelector(this.el.dataset.dialog);
      this.allDialogs = document.querySelectorAll('.share');
      this.setUp();
    }

    SocialShare.prototype.setUp = function() {
      this.el.addEventListener('click', this.showDialog);
      this.dialog.querySelector('.share-close').addEventListener('click', this.closeDialog);
      this.dialog.querySelector('.share-url').addEventListener('focus', this.select);
      return this.dialog.querySelector('.share-url').addEventListener('click', this.stopClick);
    };

    SocialShare.prototype.showDialog = function(e) {
      e.preventDefault();
      e.stopPropagation();
      Array.from(this.allDialogs).forEach(function(elm) {
        return elm.style.display = 'none';
      });
      this.dialog.style.display = 'block';
    };

    SocialShare.prototype.closeDialog = function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.dialog.style.display = 'none';
    };

    SocialShare.prototype.select = function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.setSelectionRange(0, this.value.length - 1);
    };

    SocialShare.prototype.stopClick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      this.focus();
    };

    return SocialShare;

  })();

  stModules.socialShare = function(elms) {
    return Array.from(elms).map(function(elm) {
      return new SocialShare(elm);
    });
  };

  stModules.SocialShare = SocialShare;

}).call(this);
