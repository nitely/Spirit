// Karma configuration
// Generated on Sat Jun 21 2014 21:55:34 GMT-0300 (Hora estándar de Argentina)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '../',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'all.min.js',
      'test/jquery.min.js',
      'test/jasmine-jquery.js',
      'test/suites/*-spec.js',

      {
        pattern: 'test/fixtures/*.html',
        watched: true,
        included: false,
        served: true
      },
    ]

  });
};
