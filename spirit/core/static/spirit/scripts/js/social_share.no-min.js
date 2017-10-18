
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
      var shareInput;
      this.el.addEventListener('click', this.showDialog);
      this.dialog.querySelector('.share-close').addEventListener('click', this.closeDialog);
      shareInput = this.dialog.querySelector('.share-url');
      shareInput.addEventListener('focus', this.select);
      return shareInput.addEventListener('mouseup', this.stopEvent);
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

    SocialShare.prototype.stopEvent = function(e) {
      e.preventDefault();
      e.stopPropagation();
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
