var gulp = require('gulp');
var log = require('fancy-log');
var sass = require('gulp-ruby-sass');
var coffee = require('gulp-coffee');
var sourcemaps = require('gulp-sourcemaps');
var minifyCss = require('gulp-minify-css');
var rename = require("gulp-rename");
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var gulpif = require('gulp-if');
//var babel = require('gulp-babel');
//const jasmine = require('gulp-jasmine');

var assetsPath = 'spirit/core/static/spirit/';
var cssPath = assetsPath + 'stylesheets/';
var jsPath = assetsPath + 'scripts/';


gulp.task('_sass', function () {
  return sass(cssPath + 'src/styles.scss')
    .on('error', sass.logError)
    .pipe(gulp.dest(cssPath))
});


gulp.task('_css-minify', gulp.series('_sass', function() {
  var path = cssPath + 'vendors/';
  return gulp.src([
    path + '*.css',
    cssPath + 'styles.css'
  ])
    .pipe(minifyCss({compatibility: 'ie8', target: cssPath, relativeTo: cssPath}))
    .pipe(concat('styles.all.min.css'))
    .pipe(gulp.dest(cssPath))
}));


gulp.task('css', gulp.series('_sass', '_css-minify'));


gulp.task('coffee', function() {
  var pathVendors = jsPath + 'vendors/';
  var pathCoffee = jsPath + 'src/';
  var pathJs = jsPath + 'js/';
  return gulp.src([
    pathVendors + '**/*.js',
    pathVendors + '**/*.coffee',
    pathCoffee + 'modules.coffee',
    pathCoffee + 'util.coffee',
    pathCoffee + 'tab.coffee',
    pathCoffee + 'editor_file_upload.coffee',
    pathCoffee + '*.coffee'
  ])
    .pipe(sourcemaps.init())
    .pipe(gulpif(/\.coffee$/, rename({suffix: ".no-min"})))
    .pipe(gulpif(/\.coffee$/, coffee({bare: false}).on('error', log.error)))
    .pipe(gulpif(/\.no-min\.js$/, gulp.dest(pathJs)))  // JS Preview
    .pipe(uglify({mangle: false}))
    .pipe(concat('all.min.js'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(jsPath))
});


gulp.task('_coffee-test', function() {
  return gulp.src(jsPath + 'test/suites/*.coffee')
    .pipe(sourcemaps.init())
    .pipe(coffee({bare: false}).on('error', log.error))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(jsPath + 'test/suites/'))
});

gulp.task('test', gulp.series('coffee', '_coffee-test'));
