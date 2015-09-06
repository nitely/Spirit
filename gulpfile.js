var gulp = require('gulp');
var sass = require('gulp-ruby-sass');

var assetsPath = 'spirit/core/static/spirit/';
var cssPath = assetsPath + 'stylesheets/';


gulp.task('sass', function () {
  return sass(cssPath + 'src/styles.scss')
    .on('error', sass.logError)
    .pipe(gulp.dest(cssPath));
});
