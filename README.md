# portfolio-blog-api
Portfolio and personal blog api source code

#### Main Branch Status:
[![Build Status](https://app.travis-ci.com/andrewtdunn/portfolio-blog-api.svg?branch=main)](https://app.travis-ci.com/andrewtdunn/portfolio-blog-api)

1. pytest (unit tests with coverage):

    `dc exec backend pytest -p no:warnings --cov=.`
 
2. flake8 (linting):
    
    `dc exec backend flake8 .`

3. black (code quality):
    - check: `dc exec backend black --check --exclude=migrations .`
    - diff: `dc exec backend black --diff --exclude=migrations .`
    - run: `dc exec backend black --exclude=migrations .`
    
4. isort (sort includes):
    - check: `dc exec backend /bin/sh -c "isort ./*/*.py" --check-only`
    - run: `dc exec backend /bin/sh -c "isort ./*/*.py"`