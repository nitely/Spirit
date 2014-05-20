/*
    A library to tell the server how far you have scrolled down.
    requires: waypoints
*/

	(function ( $ ) {

        var comment_number = window.location.hash.split( "#c" )[ 1 ];
        comment_number = parseInt( comment_number, 10 );  // base 10

        if ( !comment_number )
		{
			comment_number = 0;
		}
		else
		{
			// workaround to override the default comment number setted on topic_viewed (server side)
			comment_number -= 1;
		}


		$.fn.bookmark = function( options ) {

            var settings = $.extend( {
				csrf_token: "csrf_token",
                target: "target url",
			}, options ),
				$this = $( this );
			
			
			var post = function() {

				$this.waypoint( 'disable' );

				$.post( settings.target, { 'csrfmiddlewaretoken': settings.csrf_token,
                                           'comment_number': comment_number })
					.always(function() {
					
						$this.waypoint( 'enable' );
						
					});
			
			}
			

			$this.waypoint(function() {

				var new_comment_number = $( this ).data( 'number' );  // HTML5 <... data-number=""> custom attr

				if ( new_comment_number > comment_number ) {
                    comment_number = new_comment_number;

                    post();

				}

			}, { offset: '100%', });


			return this;

		};

	}( jQuery ));