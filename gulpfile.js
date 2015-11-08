var gulp = require('gulp');
var gutil = require('gulp-util');
var sass = require('gulp-ruby-sass');
var coffee = require('gulp-coffee');
var sourcemaps = require('gulp-sourcemaps');
var Server = require('karma').Server;
var minifyCss = require('gulp-minify-css');
var rename = require("gulp-rename");
var concat = require('gulp-concat');

var assetsPath = 'spirit/core/static/spirit/';
var cssPath = assetsPath + 'stylesheets/';
var jsPath = assetsPath + 'scripts/';


gulp.task('_sass', function () {
    return sass(cssPath + 'src/styles.scss')
        .on('error', sass.logError)
        .pipe(gulp.dest(cssPath));
});


gulp.task('_css-minify', ['_sass'], function () {
    return gulp.src(cssPath + 'styles.css')
        .pipe(minifyCss({compatibility: 'ie8'}))
        .pipe(rename({suffix: ".min"}))
        .pipe(gulp.dest(cssPath));
});


gulp.task('_css-concat', ['_css-minify'], function() {
    var path = cssPath + 'vendors/'
    return gulp.src([
            path + 'font-awesome.min.css',
            path + 'github.min.css',
            path + 'jquery.atwho.min.css',
            cssPath + 'styles.min.css',
        ])
        .pipe(concat('styles.all.min.css'))
        .pipe(gulp.dest(cssPath));
});


gulp.task('css', ['_css-concat']);


var coffeeTask = function coffeeTask(opts) {
    opts = opts || {srcPath: './*.coffee', destPath: './'};
    return gulp.src(opts.srcPath)
        .pipe(sourcemaps.init())
        .pipe(coffee({bare: false}).on('error', gutil.log))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(opts.destPath))
}


gulp.task('coffee', function(done) {
    coffeeTask({
        srcPath: jsPath + 'src/*.coffee',
        destPath: jsPath,
    }).on('end', done)
});


/* Do not run this directly */
gulp.task('_coffee-test', function(done) {
    coffeeTask({
        srcPath: jsPath + 'test/suites/*.coffee',
        destPath: jsPath + 'test/suites/',
    }).on('end', done)
});


/* Do not run this directly */
gulp.task('_test', ['coffee', '_coffee-test'], function (done) {
    new Server({
        configFile: __dirname + '/' + jsPath + 'test/karma.conf.js',
        singleRun: true
    }, done).start();
});


gulp.task('test', ['coffee', '_coffee-test', '_test']);
