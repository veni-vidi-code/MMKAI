# MMKAI
This repository contains the Code to the Bachelorthesis Operationsplanung als Rucksackproblem: Komplexität und Algorithmen für mehrere Rucksäcke (english title: Surgical planning as a Knapsackproblem: Complexity and Algorithms for multiple 
Knapsacks)

It contains one Algorithm for the multiple knapsackproblem with assignment restrictions (MTM EXTENDED) aswell as one for the multiple knapsackproblem with assignment restrictions and identical Profits (MMKAI).

To use either of the two algorithms import them from the src directory. The classes for the input are in src/models. It is recommended to install the requirements first, however gurobi is only needed to solve the general MKPA or to run some of the tests. 

Some tests to do some basic functionallity checking are available in unit_tests. 
To do runtime testing refer to runtime_tester/run_tests.py, it is recommended to delete the results from the original test in runtime_tester/test_results/. 
To turn the collected results into some basic Latex tables run evaluator.py. Running this requires pandas~=1.5.0. The required Latex packages are documented in https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html
