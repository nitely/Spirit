var gulp = require('gulp');
var gutil = require('gulp-util');
var sass = require('gulp-ruby-sass');
var coffee = require('gulp-coffee');
var sourcemaps = require('gulp-sourcemaps');
var Server = require('karma').Server;
var minifyCss = require('gulp-minify-css');
var rename = require("gulp-rename");
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var gulpif = require('gulp-if');

var assetsPath = 'spirit/core/static/spirit/';
var cssPath = assetsPath + 'stylesheets/';
var jsPath = assetsPath + 'scripts/';


gulp.task('_sass', function () {
    return sass(cssPath + 'src/styles.scss')
        .on('error', sass.logError)
        .pipe(gulp.dest(cssPath))
});


gulp.task('_css-minify', ['_sass'], function() {
    var path = cssPath + 'vendors/';
    return gulp.src([
            path + '*.css',
            cssPath + 'styles.css'
        ])
        .pipe(minifyCss({compatibility: 'ie8', target: cssPath, relativeTo: cssPath}))
        .pipe(concat('styles.all.min.css'))
        .pipe(gulp.dest(cssPath))
});


gulp.task('css', ['_sass', '_css-minify']);


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
            .pipe(gulpif(/\.coffee$/, coffee({bare: false}).on('error', gutil.log)))
            .pipe(gulpif(/\.no-min\.js$/, gulp.dest(pathJs)))  // JS Preview
            .pipe(gulpif(/\.no-min\.js$/, uglify({mangle: false})))
            .pipe(concat('all.min.js'))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(jsPath))
});


gulp.task('_coffee-test', function() {
    return gulp.src(jsPath + 'test/suites/*.coffee')
        .pipe(sourcemaps.init())
            .pipe(coffee({bare: false}).on('error', gutil.log))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(jsPath + 'test/suites/'))
});


gulp.task('_test', ['coffee', '_coffee-test'], function (done) {
    new Server({
        configFile: __dirname + '/' + jsPath + 'test/karma.conf.js',
        singleRun: true
    }, done).start();
});


gulp.task('test', ['coffee', '_coffee-test', '_test']);
