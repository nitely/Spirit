/*

Move comments to other topic

*/


    (function ( $ ) {
	
		$.move_comments = function( options ) {
		
			var settings = $.extend( {
				csrf_token: "csrf_token",
				target: "#post_url",
			}, options );

            $( ".js-show-move-comments" ).on( 'click', function() {
			
				var $li;
			
				if ( $( ".move-comments" ).is( ":hidden" ) )
				{
					$( ".move-comments" ).show();
					
					$li = $("<li/>").appendTo( ".comment-info" );
					
					$("<input/>", {
						'class': "move-comment-checkbox",
						'name': "comments",
						'type': "checkbox",
						'value': ""
					}).appendTo( $li );
				}
				
				return false;
			});
			
			
			$( ".js-move-comments" ).on( 'click', function() {
				// dynamic form
				
				var $form = $("<form/>", {
					'action': settings.target,
					'method': "post"
				}),
					topic_id = $( "#id_move_comments_topic" ).val(),
					$comment_id;
				
				$("<input/>", {
					'name': "csrfmiddlewaretoken",
					'type': "hidden",
					'value': settings.csrf_token
				}).appendTo( $form );
				
				$("<input/>", {
					'name': "topic",
					'type': "text",
					'value': topic_id
				}).appendTo( $form );
				
				// comment_id to input value
				$( ".move-comment-checkbox" ).each(function() {
					
					$comment_id = $( this ).closest( ".comment" ).data( "pk" );
					$( this ).val( $comment_id );
					
				}).clone().appendTo( $form );
				
				$form.hide().appendTo( document.body ).submit();

				return false;
			});
			
		};
	
	}( jQuery ));