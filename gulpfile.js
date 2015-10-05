var gulp = require('gulp');
var gutil = require('gulp-util');
var sass = require('gulp-ruby-sass');
var coffee = require('gulp-coffee');
var sourcemaps = require('gulp-sourcemaps');

var assetsPath = 'spirit/core/static/spirit/';
var cssPath = assetsPath + 'stylesheets/';
var jsPath = assetsPath + 'scripts/';


gulp.task('sass', function () {
    return sass(cssPath + 'src/styles.scss')
        .on('error', sass.logError)
        .pipe(gulp.dest(cssPath));
});


gulp.task('coffee', function() {
    gulp.src(jsPath + 'src/*.coffee')
        .pipe(sourcemaps.init())
        .pipe(coffee({bare: false}).on('error', gutil.log))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(jsPath))
});
