/*

Generic dropdown + notifications ajax drop down
requires: utils.js

*/

	(function ( $ ) {
	
		$.dropdown = function( options ) {
		
			var settings = $.extend( {
				notification_url: "#ajax",
				notification_list_url: "#show-all",
				mention_txt: "{user} mention you on {topic}",
				comment_txt: "{user} has commented on {topic}",
				show_all: "Show all",
				empty: "Nothing to show",
				unread: "unread",
			}, options );
			
			
			var switch_tab = function( tab ) {
			
				$tabs_container = tab.closest( ".js-tabs-container" );
				$tabs_container.find( ".js-tab-content" ).hide();
				
				if ( tab.hasClass( "is-selected" ) )
				{
					tab.removeClass( "is-selected" );
				}
				else
				{
					$tabs_container.find( ".js-tab" ).removeClass( "is-selected" );
					tab.addClass( "is-selected" );
					$( tab.data( "related" ) ).show();
				}
				
			}
			
			
			$( ".js-tab" ).click(function( e ) {
				
				switch_tab( $( this ) );
				
			});
			
			
			// on first click
			$( ".js-tab-notification" ).one("click", function( e ) {
			
				$tab_notification = $( this );
				$tab_notification_content = $( $tab_notification.data( "related" ) );
			
				$.getJSON( settings.notification_url )
					.done( function( data, status, jqXHR ) {
						/* alert(jqXHR.responseText); */

						if ( data.n.length > 0 )
						{
							$.each( data.n, function( i, obj ) {
								$link = '<a href="' + obj.url + '">' + obj.title + '</a>';
								
								if ( obj.action == "Mention" )
								{
									$txt = settings.mention_txt;
								}
								else
								{
									$txt = settings.comment_txt;
								}
								
								if ( !obj.is_read ) {
									$txt += ' <span class="row-unread">' + settings.unread + '</span>'
								}
								
								$txt = $.format( $txt, {'user': obj.user, 'topic': $link} );
								$tab_notification_content.append( '<div>' + $txt + '</div>' );
							});
							
							$txt = '<a href="' + settings.notification_list_url + '">' + settings.show_all + '</a>';
							$tab_notification_content.append( '<div>' + $txt + '</div>' );
						}
						else
						{
							$tab_notification_content.append( '<div>' + settings.empty + '</div>' );
						}

					})
					.fail( function() {
					
						$txt = 'error';
						$tab_notification_content.append( '<p>' + $txt + '</p>' );
					
					})
					.always( function() {
						
						$( $tab_notification ).click(function( e ) {
				
							switch_tab( $( this ) );
							
						});
						
						$tab_notification.addClass( "js-tab" );
						$tab_notification.trigger( 'click' );
						
					});

			});
			
			
			// prevent default click action
			$( ".js-tab, .js-tab-notification" ).click(function( e ) {
				e.preventDefault();
				e.stopPropagation();
			});
			
		};
	
	}( jQuery ));