# Copyright (c) 2023 Tom Mucke

"""
Test results are stored in the folder test_results. This script evaluates the results and creates a latex table
containing the average runtime for each combination of variables. The table is written to the files tmkpa.tex and
mtm_extended.tex.

Always delete the results of the first test run to ensure that the results are not influenced by warmup.

The provided test results were run under the following conditions:
Edition	Windows 11 Pro
Version	22H2
OS Build	22621.2283
Performace	Windows Feature Experience Pack 1000.22662.1000.0

Processor	12th Gen Intel(R) Core(TM) i7-12700   2.10 GHz
RAM	32,0 GB (31,7 GB usable)
Systemtype	64-Bit, x64 Processor

Python 3.10.7 from python.org using a venv
attrs==22.1.0
gurobipy==9.5.2
gurobipy-stubs==1.0.1
networkx==3.1
numpy==1.23.4
pandas==1.5.0

PYTHONUNBUFFERED=1
Flag -OO set

Run from
PyCharm 2023.1.4 (Professional Edition)
Build #PY-231.9225.15
Runtime version: 17.0.7+10-b829.16 amd64
VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
Windows 11.0
GC: G1 Young Generation, G1 Old Generation
Memory: 2048M
Cores: 20
"""

import json
import os

from runtime_tester.Testrecord import Testrecord

import pandas as pd

minimum_number_of_items = 1000
minimum_number_of_knapsacks = 2


def get_tests(base_dir="./test_results"):
    for filename in os.listdir(base_dir):
        with open(f"{base_dir}/{filename}", "r") as f:
            y = json.load(f)
            for x in y:
                if isinstance(x, list):
                    x: list[Testrecord]
                    for test in x:
                        yield test
                else:
                    x: Testrecord
                    yield x


def get_average_times_for_variables():
    results_tmkpa: dict[tuple[int, int, int], tuple[float, int, int]] = {}
    results_mtm_extended: dict[tuple[int, int, int], tuple[float, int, int]] = {}
    for test in get_tests():
        if test["number_of_items"] < minimum_number_of_items:
            continue

        if test["number_of_knapsacks"] < minimum_number_of_knapsacks:
            continue

        key = (test["number_of_knapsacks"], test["number_of_weightclasses"], test["number_of_items"])

        if "required_time_tmkpa" in test:
            prev_result_tmkpa = results_tmkpa.get(key, (0, 0, 0))
            if test["required_time_tmkpa"] >= 3 * 60 or test["required_time_tmkpa"] < -0.5:
                results_tmkpa[key] = (prev_result_tmkpa[0], int(prev_result_tmkpa[1] + 1),
                                      int(prev_result_tmkpa[2]))
            else:
                results_tmkpa[key] = (prev_result_tmkpa[0] + test["required_time_tmkpa"], int(prev_result_tmkpa[1]),
                                      int(prev_result_tmkpa[2] + 1))

        if "required_time_mtm_extended" in test:
            prev_result_mtm_extended = results_mtm_extended.get(key, (0, 0, 0))
            if test["required_time_mtm_extended"] >= 3 * 60 or test["required_time_mtm_extended"] < -0.5:
                results_mtm_extended[key] = (prev_result_mtm_extended[0], int(prev_result_mtm_extended[1] + 1),
                                             int(prev_result_mtm_extended[2]))
            else:
                results_mtm_extended[key] = (prev_result_mtm_extended[0] + test["required_time_mtm_extended"],
                                             int(prev_result_mtm_extended[1]),
                                             int(prev_result_mtm_extended[2] + 1))

    for key in results_tmkpa.keys():
        if results_tmkpa[key][2] != 0:
            results_tmkpa[key] = (results_tmkpa[key][0] / results_tmkpa[key][2],
                                  results_tmkpa[key][1], results_tmkpa[key][2])
        else:
            results_tmkpa[key] = (-1,
                                  results_tmkpa[key][1], results_tmkpa[key][2])

    for key in results_mtm_extended.keys():
        if results_mtm_extended[key][2] != 0:
            results_mtm_extended[key] = (results_mtm_extended[key][0] / results_mtm_extended[key][2],
                                         results_mtm_extended[key][1], results_mtm_extended[key][2])
        else:
            results_mtm_extended[key] = (-1,
                                         results_mtm_extended[key][1], results_mtm_extended[key][2])

    return results_tmkpa, results_mtm_extended


def get_dataframes():
    results_tmkpa, results_mtm_extended = get_average_times_for_variables()

    # create index
    index = pd.MultiIndex.from_tuples(results_tmkpa.keys(),
                                      names=("Anzahl Rucks\"acke", "Anzahl Gewichtsklassen", "Anzahl Gegenst\"ande"))

    # create dataframes
    cols = ["Durchschnittliche Laufzeit", "Anzahl Timeouts", "Erfolgreiche Tests"]
    df_tmkpa = pd.DataFrame(results_tmkpa.values(), index=index,
                            columns=cols)
    df_mtm_extended = pd.DataFrame(results_mtm_extended.values(), index=index,
                                   columns=cols)

    return df_tmkpa, df_mtm_extended


def write_df_to_latex(df, filename):
    style = df.style
    style.format('\\num{{{:n}}}', "Anzahl Timeouts")
    style.format('\\num{{{:n}}}', "Erfolgreiche Tests")

    def format_time(x):
        if x == -1:
            return "-"
        return "\\qty{{{:.2f}}}{{\\second}}".format(x).replace(".", ",")

    style.format(format_time, "Durchschnittliche Laufzeit")
    style.format_index(lambda x: '\\num{{{:_}}}'.format(x).replace(".", ",").replace("_", "."))

    with open(filename, "w") as f:
        f.write(style.to_latex(environment="longtable", hrules=True, clines="skip-last;data"))


if __name__ == "__main__":
    df_tmkpa, df_mtm_extended = get_dataframes()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_tmkpa)
        print(df_mtm_extended)

    write_df_to_latex(df_tmkpa, "tmkpa.tex")
    write_df_to_latex(df_mtm_extended, "mtm_extended.tex")
