const JSDOM = require('jsdom').JSDOM;

const dom = new JSDOM('<html><body></body></html>', {
  url: 'https://localhost'
});
global.document = dom.window.document;
global.window = dom.window;
global.FormData = dom.window.FormData;
global.navigator = dom.window.navigator;
global.localStorage = dom.window.localStorage;
global.fetch = require('node-fetch');
global.Headers = require('node-fetch').Headers;
/*
global.jQuery = require('jquery')(dom.window);
global.$ = jQuery;
global.window.$ = jQuery;
global.window.jQuery = jQuery;
global.window.jasmine = jasmine;
*/
