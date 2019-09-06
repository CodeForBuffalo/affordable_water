# Pathways to Affordable Water
This site allows Buffalo residents to apply for the [Residential Affordable Water Program](https://buffalowater.org/wp-content/uploads/2019/03/ResidentialAffordabilityProgram.pdf).

This project is being developed as part of the [2019 Code for America Community Fellowship](https://www.codeforamerica.org/programs/fellowship/meet-the-fellows).

## To test and develop locally
- Install [pipenv](https://github.com/pypa/pipenv) to manage virtual environment and dependencies. [Learn more about pipenv.](https://realpython.com/pipenv-guide/)
    - Run ``pip install pipenv``
- In the repository location, use **pipenv** to automatically create a new virtual environment and install the dependencies listed in the Pipfile
    - Run ``pipenv install``
- Start local [Django](https://www.djangoproject.com/) server
    - Run `pipenv shell` and then run `python manage.py runserver`.
    - Alternatively, you can run the command inside the virtualenv with: `pipenv run manage.py runserver`.
- Open web browser and navigate to `http://localhost:8000/`
