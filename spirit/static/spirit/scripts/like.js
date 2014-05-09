/*

Post likes via Ajax.
requires: utils.js

*/


    (function ( $ ) {
	
		$.like = function( options ) {
		
			var settings = $.extend( {
				csrf_token: "csrf_token",
				like_text: "like ({count})",
				remove_like_text: "remove like ({count})",
			}, options );


            var post = function() {

                $this = $( this );

                $this.off( "click", post );

                var href = $this.attr( 'href' );

                $.post( href, { 'csrfmiddlewaretoken': settings.csrf_token, })
                    .done(function( data ) {

                        var count = $this.data( 'count' );

                        if ( data.url_delete )
                        {
                            $this.attr( 'href', data.url_delete );
                            count += 1;
                            $this.data( 'count', count );
                            $this.text( $.format( settings.remove_like_text, {'count': count, } ) );
                        }

                        if ( data.url_create )
                        {
                            $this.attr( 'href', data.url_create );
                            count -= 1;
                            $this.data( 'count', count );
                            $this.text( $.format( settings.like_text, {'count': count, } ) );
                        }
                    })
                    .always(function() {

                        $this.on( "click", post );

                    });

            }


            $likes = $( ".js-like" );

            $likes.on( 'click', post );

            $likes.on( 'click', function() {

                return false;

            });
			
		};
	
	}( jQuery ));