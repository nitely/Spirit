/*

A bunch of generic functions, this are used by other plugins.

*/

    (function ( $ ) {

		$.format = function( str, args ) {

            for ( var key in args ) {
                str = str.replace( '{' + key + '}', String( args[ key ] ) );
            }

            return str;

        }


        //$.other = ...

	}( jQuery ));