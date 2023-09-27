from pandas import DataFrame
from runtime_tester.Testrecord import Testrecord
from runtime_tester.evaluator import get_tests

weightclasses = set()
knapsacks = set()

time_timeout_replace = 300


def generate_data():
    for test in get_tests():
        test: Testrecord

        kp = test["number_of_knapsacks"]
        wk = test["number_of_weightclasses"]
        it = test["number_of_items"]

        weightclasses.add(wk)
        knapsacks.add(kp)

        if "required_time_MMKAI" in test:
            if test["required_time_MMKAI"] >= 3 * 60 or test["required_time_MMKAI"] < -0.5:

                yield kp, wk, it, time_timeout_replace, "MMKAI", "Ja"
            else:
                yield kp, wk, it, test["required_time_MMKAI"], "MMKAI", "Nein"

        if "required_time_mtm_extended" in test:
            if test["required_time_mtm_extended"] >= 3 * 60 or test["required_time_mtm_extended"] < -0.5:
                yield kp, wk, it, time_timeout_replace, "MTM EXTENDED", "Ja"
            else:
                yield kp, wk, it, test["required_time_mtm_extended"], "MTM EXTENDED", "Nein"


def generate_main_df():
    df = DataFrame(generate_data(),
                   columns=["number_of_knapsacks", "number_of_weightclasses", "number_of_items",
                            "required_time",
                            "algorithm", "Timeout"])
    return df


def generate_timeout_df(main_df):
    main_df = main_df.replace({"Ja": 1, "Nein": 0})
    # replace all "Ja" with 1 and all "Nein" with 0

    # for each algorithm, knapsack, weightclass, item count, get the number of timeouts and the number of runs
    df = main_df.groupby(["algorithm", "number_of_knapsacks", "number_of_weightclasses", "number_of_items"]).agg(
        {"Timeout": ["sum", "count"]})
    df = df.reset_index()
    df.columns = ["algorithm", "number_of_knapsacks", "number_of_weightclasses", "number_of_items", "sum", "count"]
    df.rename(columns={"sum": "Anzahl Timeouts", "count": "Anzahl Läufe"}, inplace=True)

    # add a column for the percentage of timeouts
    df["Prozentuale Timeouts"] = df["Anzahl Timeouts"] / df["Anzahl Läufe"] * 100
    return df


data = generate_main_df()
weightclasses = sorted(weightclasses)
knapsacks = sorted(knapsacks)
timeout_df = generate_timeout_df(data)
