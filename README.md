# MMKAI
This repository contains the Code to the Bachelorthesis Operationsplanung als Rucksackproblem: Komplexität und Algorithmen für mehrere Rucksäcke (english title: Surgical planning as a Knapsackproblem: Complexity and Algorithms for multiple 
Knapsacks). Different from the Thesis a lot is written in english. The Output of several functions is however still in German.

It contains one Algorithm for the multiple knapsackproblem with assignment restrictions (MTM EXTENDED) aswell as a matching based algorithm for the multiple knapsackproblem with assignment restrictions and identical Profits (MMKAI).


# Installation and Running

1. Install python 3.10 or a higher python 3 version together with pip from https://www.python.org/downloads/
2. During the install make sure to check the box to add python to the PATH and restart your computer afterwards
3. Validate the installation by opening a terminal and running `python3 --version` (depending on the installation you
   might need to use python instead of python3)
4. Open a terminal and navigate to the folder of this repository (the folder above runtime_visualization, src, etc.) (
   under Windows CMD is recommended)
5. Create a virtual environment with `python3 -m venv venv` (depending on the installation you might need to use python
   instead of python3)
6. Activate the virtual environment with `source venv/bin/activate` under Unix or `venv\Scripts\activate.bat` under
   Windows if using CMD and `venv\Scripts\activate.ps1` under Windows if using Powershell
7. There should now be a `(venv)` in front of your terminal prompt
8. Install the requirements with `pip install -r requirements.txt`
9. To install the additional requirements for the runtime visualisation
   run `pip install -r runtime_visualization/requirements.txt`
10. Choose one of the following options and proceed from there. Important: All of these assume you did the installation
    correctly and you must still be in a terminal in the correct folder with the venv enabled.

Steps 4, 6, 7 need to be repeated every time you want to run the app.

## Run the unit tests

This will run the unit tests to check the basic functionality of the algorithms.

1. Run `python3 -m unit_tests_MMKAI.__init__` or `python -m unit_tests_MMKAI.__init__` depending on your installation
2. All unit tests should pass and you should see something like `Ran 70 tests in 23.000s OK`

## Collect runtime results on your own system

This will run the tests on your own system and collect the results. Please note that this will take a long time (several
hours to days) and you should not use your system for anything else during this time. This will also require several
cores and a lot of RAM. If it runs out of RAM it will crash with weird errors. You might consider adjusting the code to
run different tests.

1. Delete the results from the original test in runtime_tester/test_results/
2. Run `python3 -m runtime_tester.run_tests` or `python -m runtime_tester.run_tests` depending on your installation
3. This will also attempt to run against gurobi. As the instances will likely be quite large for the free version of
   gurobi this will likely fail. You might want to consider commenting out the gurobi tests in the code. The gurobi
   output will be redirected into its own file

You should consider adding the `-u` and possibly the `-OO` flag to the command. This will disable the output buffering
and optimize the code. 

## Create Latex tables from the collected results

This will create Latex tables from the collected results. They will be saved in MMKAI.tex and
MTM_EXTENDED.tex.

1. Run `python3 -m runtime_tester.evaluator` or `python -m runtime_tester.evaluator` depending on your installation
2. The tables should be created
3. You can now copy the tables into your Latex document. For a list of required packages
   see https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html
4. You will need to adjust the headers of the tables to be in one line

## Running the webserver for graphs

This will run a webserver to visualize the results as graphs.
If you are using a Unix system you might prefer gunicorn. The following however will only run the server using flask
directly (which is not recommended for production use).

1. Run `python3 wsgi.py` or `python wsgi.py` depending on your installation
2. It should print something like `Running on http://...` and you can open the link in your browser
3. In your browser you can now select the visualization.
4. To stop the server press `Ctrl+C` in the terminal

For usage instructions of the webpages please refer to the text on the pages.


## Using the algorithms in your own code

This assumes you do know how to use python. As a way of entry take a look at src/test.py. It contains a simple example
of how to create an instance and run the algorithm. Additionally it also validates the results using gurobi, this is 
however only for testing purposes and not required to run the algorithm. 

1. Import the algorithm you want to use from src
2. Create an instance of the algorithms solver class providing the input
3. call the `solve` method on the solver instance
4. It will return a tuple containg the optimal value and the optimal solution (dict mapping a list of items to each
   knapsack)

Please note that if you are importing the algorithm from a different folder you might need to adjust the imports in the
algorithm itself. As an alternative you can also add the folder to the python path.


