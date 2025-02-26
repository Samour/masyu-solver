# masyu-solver

## Setup

It's highly recommended to set up a virtual environment

```
python3 -m venv venv
```

Then to activate the virtual env

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

## Linting

Style linting:

```
# Report on style violations without changing the files
black --check solver

# Auto-fix style violations
black solver
```

## Run app

From root directory

```
python3 -m solver.main
```
