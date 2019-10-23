const { series, src, dest } = require('gulp');

// Task 1: copy 'bourbon' assets to /_vendor/
function bourbon() {
  const files = [
    'node_modules/bourbon/**/*',
  ]
  return src(files).pipe(dest('_vendor/bourbon'))
}

// Task 2: copy 'normalize.css' assets to /_vendor/
function normalize() {
  const files = [
    'node_modules/normalize.css/**/*'
  ]
  return src(files).pipe(dest('_vendor/normalize.css'))
}

// Task 3: copy 'getbuffalowater-bourbon-neat' assets to /_vendor/
function neat() {
    const files = [
      'node_modules/getbuffalowater-bourbon-neat/**/*'
    ]
    return src(files).pipe(dest('_vendor/neat'))
  }

// Task 4: copy 'getbuffalowater-cfa-styleguide' assets to /_vendor/
function cfa_styleguide() {
  const files = [
    'node_modules/getbuffalowater-cfa-styleguide/**/*'
  ]
  return src(files).pipe(dest('_vendor/cfa-styleguide'))
}

exports.default = series(bourbon, normalize, neat, cfa_styleguide)