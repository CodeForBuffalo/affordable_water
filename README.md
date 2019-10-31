# GetBuffaloWater
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

## License

The project is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

## Code of Conduct

Everyone interacting in this project’s codebase, issue trackers, chat rooms and mailing lists is expected to follow the Code for America [code of conduct](https://brigade.codeforamerica.org/about/code-of-conduct).
