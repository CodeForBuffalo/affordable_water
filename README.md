# GetBuffaloWater
![GitHub release (latest by date)](https://img.shields.io/github/v/release/CodeForBuffalo/affordable_water)
[![Build Status](https://travis-ci.com/CodeForBuffalo/affordable_water.svg?branch=master)](https://travis-ci.com/CodeForBuffalo/affordable_water)
[![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/CodeForBuffalo/affordable_water?logo=Code%20Climate)](https://codeclimate.com/github/CodeForBuffalo/affordable_water)
[![Code Climate coverage](https://img.shields.io/codeclimate/coverage/CodeForBuffalo/affordable_water?label=test%20coverage&logo=Code%20Climate)](https://codeclimate.com/github/CodeForBuffalo/affordable_water)
![GitHub](https://img.shields.io/github/license/CodeForBuffalo/affordable_water)

This site allows Buffalo residents to apply for the [Residential Affordable Water Program](https://buffalowater.org/wp-content/uploads/2019/03/ResidentialAffordabilityProgram.pdf).

This project is being developed as part of the [2019 Code for America Community Fellowship](https://www.codeforamerica.org/programs/fellowship/meet-the-fellows).

## Development

### Requirements
Make sure these are installed on your machine.
- [Python](https://www.python.org/downloads/release/python-374/) (3.7+)
- [Node.js](https://nodejs.org/en/) (12.13.0+)

#### Windows users
- [Visual C++ Build Tools](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16). Read [Issue #11](https://github.com/CodeForBuffalo/affordable_water/issues/11) for instructions. Required for some Python packages on Windows.

### Instructions
We use **npm scripts** to speed up development. Manual instructions are also provided.

#### Clone repository and open terminal in project's root directory.
```
$ PATH\TO\REPO\affordable_water>
```

#### Setup environment automatically
```
npm run setup
```
This script automatically:
1. Installs [pipenv](https://github.com/pypa/pipenv) to manage Python virtual environment and dependencies. [Learn more about pipenv.](https://realpython.com/pipenv-guide/)
    - `pip install pipenv`
2. Creates a Python virtual environment using pipenv and installs dependencies in Pipfile
    - `pipenv install` 
3. Installs node modules using npm
    - `npm install`

#### Build assets
```
npm run build
```
This script automatically:
- Uses [gulp.js](https://gulpjs.com/) to copy assets from `node_modules` to `_vendor` folder.
    - `gulp`
- Collects Django `static` files, including the copied assets from `_vendor`
    - `pipenv run manage.py collectstatic`

#### Start local server
```
npm start
```
This script runs `pipenv run manage.py runserver`

#### Visit local server
Open server in browser at [http://localhost:8000/](http://localhost:8000/)

#### Run tests
If you make changes to the code, you'll want to run the test suite to make sure existing functionality didn't break. You should also write tests for any new or modified code.
```
npm test
```
This script runs the testing suite along with a code coverage analysis using [Coverage.py](https://coverage.readthedocs.io/en/stable/). If the current tests pass, a new folder called `htmlcov` will be generated. If you open `htmlcov/index.html` in a browser, you can interactively see how much of the source code is covered by tests.

## License

The project is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

## Code of Conduct

Everyone interacting in this project’s codebase, issue trackers, chat rooms and mailing lists is expected to follow the Code for America [code of conduct](https://brigade.codeforamerica.org/about/code-of-conduct).
