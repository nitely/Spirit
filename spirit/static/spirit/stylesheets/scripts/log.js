///fix
<script type="text/javascript">
    window.onerror = function(e) {
      try {
        $.ajax({
          type: 'GET',
          url: 'https://www.url.com/log_error',
          data: 'error='+e+'&url='+window.location
        });     
      } catch(err) {}
      return false;
    }
    </script>