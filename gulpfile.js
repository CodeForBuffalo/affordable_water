const { series, src, dest } = require('gulp');

// Task 1: copy bourbon's assets to /_vendor/
function bourbon() {
  const files = [
    'node_modules/bourbon/**',
  ]
  return src(files).pipe(dest('_vendor/bourbon'))
}

// Task 2: copy normalize.css's assets to /_vendor/
function normalize() {
  const files = [
    'node_modules/normalize.css/**'
  ]
  return src(files).pipe(dest('_vendor/normalize.css'))
}

// Task 3: copy neat@1.8.0.css's assets to /_vendor/
function neat() {
    const files = [
      'neat-1.8.0/**'
    ]
    return src(files).pipe(dest('_vendor/neat-1.8.0'))
  }

exports.default = series(bourbon, normalize, neat)