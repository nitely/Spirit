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
    // todo: load the all.min.js instead of individual files
    files: [
      'vendors/jquery.min.js',
      'vendors/**/*.js',
      'test/jasmine-jquery.js',
      'test/suites/*-spec.js',
      '!js/*.min.js',  // Exclude
      'js/*.js',


      {
        pattern: 'test/fixtures/*.html',
        watched: true,
        included: false,
        served: true
      },
    ]

  });
};
