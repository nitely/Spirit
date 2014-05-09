	(function ( $ ) {
	
		$.fn.store = function( ls_key ) {
		
			$this = this;
			$form = $this.closest( "form" );
			
			if ( !localStorage ) {
				return $this;
			}
			
			
			var updateField = function() {
				/* does not triggers "input propertychange" */
				$this.val( localStorage[ ls_key ] );
			}
			
			
			if ( ls_key in localStorage ) {
				updateField();
			}
			
			
			/* comment on change */
			$this.on( 'input propertychange', function() {
				/* storage gets triggered in the current tab/window on some browsers */
				$( window ).off( 'storage' );
				
				try 
				{
					localStorage[ ls_key ] = $this.val();
				}
				catch ( error )
				{
					/* The localStorage is probably full, nothing to do other than clear it */
					localStorage.clear();
				}
				
				$( window ).on( 'storage', updateField );
				//alert("called");
			});
			
			
			/* localStorage on change */
			$( window ).on( 'storage', updateField );
			
			
			/* clear storage on form submission */
			$form.submit(function() {
				/* triggers storage change */
				delete localStorage[ ls_key ];
			});
			
			
			return $this;
			
		};
	
	}( jQuery ));