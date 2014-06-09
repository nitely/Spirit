/* load after editor.js */
/* requires utils.js */
	(function ( $ ) {
	
		$.editor_image_upload = function( options ) {
		
			// Check if browser supports FormData
			if ( !window.FormData )
			{
				return;
			}
		
			var settings = $.extend( {
					csrf_token: "csrf_token",
					target: "target url",
					placeholder_text: "uploading {image_name}",
				}, options ),
				$input_file = $("<input/>", {
					'type': "file",
					'accept': "image/*",
				}),
				$textarea = $( '.js-reply' ).find( 'textarea' );
			
			
			$input_file.change( function() {
			
				var file = $( this ).get( 0 ).files[ 0 ];
				
				post( file );
				
			});
			
			
			$( ".js-box-image" ).click( function() {
				
				$input_file.trigger( 'click' );
				
				return false;
				
			});
			
			
			var post = function( file ) {
			
				var placeholder = $.format( "![" + settings.placeholder_text + "]()", {'image_name': file.name, } ),
					form_data = new FormData();
				
				$textarea.val( $textarea.val() + placeholder );
				
				form_data.append( 'csrfmiddlewaretoken', settings.csrf_token );
				form_data.append( 'image', file );
				
				$.ajax({
					url: settings.target,
					data: form_data,
					processData: false,
					contentType: false,
					type: 'POST',
					success: function( data ) {
						
						if ( "url" in data )
						{
							$textarea.val( $textarea.val().replace( placeholder, $.format( "![{name}]({url})", {'name': file.name, 'url': data.url} ) ) );
						}
						
						if ( "error" in data )
						{
							// TODO: Should we print the error somewhere else and remove the placeholder ?
							$textarea.val( $textarea.val().replace( placeholder, "![" + JSON.stringify( data ) + "]()" ) );
						}
					
					},
					error: function( xhr, status_text, error_text ) {
						
						$textarea.val( $textarea.val().replace( placeholder, $.format( "![error: {code} {error}]()", {'code': xhr.status, 'error': error_text} ) ) );
						
					}
				});
			
			}
		
		}
	
	}( jQuery ));