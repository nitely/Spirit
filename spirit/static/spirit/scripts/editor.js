/* requires marked.js */
	(function ( $ ) {
	
		$.editor = function( options ) {
		
			var settings = $.extend( {
				bolded_text: "bolded text",
				italicised_text: "italicised text",
				list_item_text: "list item",
				link_text: "link text",
				link_url_text: "link url",
				image_text: "image text",
				image_url_text: "image url"
			}, options );
			
			
			$textarea = $( '.js-reply' ).find( 'textarea' );
			
			
			var wrapSelection = function( pre_txt, post_txt, default_txt ) {
				
				var pre_selection = $textarea.val().substring( 0, $textarea[0].selectionStart );
				var selection = $textarea.val().substring( $textarea[0].selectionStart, $textarea[0].selectionEnd );
				var post_selection = $textarea.val().substring( $textarea[0].selectionEnd );
				
				if ( !selection ) {
					selection = default_txt;
				}
				
				$textarea.val( pre_selection + pre_txt + selection + post_txt + post_selection );
				
			}
			
			
			$( '.js-box-bold' ).click(function() {
				
				wrapSelection( "**", "**", settings.bolded_text );
				
				return false;
				
			});
			
			
			$( '.js-box-italic' ).click(function() {
				
				wrapSelection( "*", "*", settings.italicised_text );
				
				return false;
				
			});
			
			
			$( '.js-box-list' ).click(function() {
				
				wrapSelection( "\n\n* ", "", settings.list_item_text );
				
				return false;
				
			});
			
			
			$( '.js-box-url' ).click(function() {
				
				wrapSelection( "[", "](" + settings.link_url_text + ")", settings.link_text );
				
				return false;
				
			});
			
			$( '.js-box-image' ).click(function() {
				
				wrapSelection( "![", "](" + settings.image_url_text + ")", settings.image_text );
				
				return false;
				
			});
			
			
			$( '.js-box-preview' ).click(function() {
				
				$preview = $( '.js-box-preview-content' );
				$textarea.toggle();
				$preview.toggle();
				$preview.html( marked( $textarea.val() ) );
				
				return false;
				
			});
			
		};
	
	}( jQuery ));