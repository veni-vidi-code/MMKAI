# Copyright (c) 2023 Tom Mucke

import json
import os

from runtime_tester.Testrecord import Testrecord

import pandas as pd


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

    for key in results_mtm_extended.keys():
        if results_mtm_extended[key][2] != 0:
            results_mtm_extended[key] = (results_mtm_extended[key][0] / results_mtm_extended[key][2],
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
    style.format(lambda x: '\\qty{{{:.2E}}}{{\\second}}'.format(x).replace(".", ","), "Durchschnittliche Laufzeit")
    style.format_index(lambda x: '\\num{{{:_}}}'.format(x).replace(".", ",").replace("_", "."))


    with open(filename, "w") as f:
        f.write(style.to_latex(environment="longtable"))


if __name__ == "__main__":
    df_tmkpa, df_mtm_extended = get_dataframes()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_tmkpa)
        print(df_mtm_extended)

    write_df_to_latex(df_tmkpa, "tmkpa.tex")
    write_df_to_latex(df_mtm_extended, "mtm_extended.tex")
