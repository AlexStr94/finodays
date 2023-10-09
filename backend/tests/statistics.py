import pandas as pd


class Statistics:
    def __init__(self):
        self.__statistics = pd.DataFrame(columns=['endpoint_name', 'frequency', 'response_code', 'response_time'])

    def add(self, endpoint_name: str, frequency: int, response_code: int, response_time: float) -> None:
        self.__statistics.loc[len(self.__statistics)] = [endpoint_name, frequency, response_code, response_time]

    def __get_mean_response_time_for_endpoint_name_and_frequency(self, endpoint_name: str, frequency: int) -> float:
        return self.__statistics.loc[(self.__statistics['endpoint_name'] == endpoint_name) &
                                     (self.__statistics['frequency'] == frequency), 'response_time'].mean()

    def __get_codes_count_for_endpoint_name_and_frequency(self, endpoint_name: str, frequency: int) -> pd.DataFrame:
        return self.__statistics.loc[(self.__statistics['endpoint_name'] == endpoint_name) &
                                     (self.__statistics['frequency'] == frequency), 'response_code'].value_counts()

    def __get_mean_response_time_for_each_frequency_for_exact_endpoint_name(self, endpoint_name: str) -> pd.DataFrame:
        res = pd.DataFrame(columns=['frequency', 'response_time'])
        for f in self.__statistics['frequency'].unique():
            res.loc[len(res)] = [f, self.__get_mean_response_time_for_endpoint_name_and_frequency(endpoint_name, f)]
        return res.sort_values(by='frequency', ascending=True).reset_index(drop=True)

    def __get_codes_count_for_each_frequency_for_exact_endpoint_name(self, name: str) -> pd.DataFrame:
        res = pd.DataFrame(columns=['frequency', 'code', 'code_count'])
        for f in self.__statistics['frequency'].unique():
            current_codes_count = self.__get_codes_count_for_endpoint_name_and_frequency(name, f)
            for i in zip(current_codes_count.index, current_codes_count.values):
                res.loc[len(res)] = [f, i[0], i[1]]
        return res

    def get_mean_response_time_for_each_frequency_for_each_endpoint_name(self) -> pd.DataFrame:
        res = pd.DataFrame(columns=['endpoint', 'frequency', 'mean_response_time'])
        for name in self.__statistics['endpoint_name'].unique():
            current_mean_response_time = self.__get_mean_response_time_for_each_frequency_for_exact_endpoint_name(name)
            for value in current_mean_response_time.values:
                res.loc[len(res)] = [name, value[0], value[1]]
        return res

    def get_codes_count_for_each_frequency_for_each_endpoint_name(self) -> pd.DataFrame:
        res = pd.DataFrame(columns=['endpoint', 'frequency', 'code', 'code_count'])
        for name in self.__statistics['endpoint_name'].unique():
            current_codes_count = self.__get_codes_count_for_each_frequency_for_exact_endpoint_name(name)
            for value in current_codes_count.values:
                res.loc[len(res)] = [name, value[0], value[1], value[2]]
        return res

    def __save_codes_count_for_each_frequency_for_each_endpoint_name_to_csv(self, path: str) -> None:
        res = self.get_codes_count_for_each_frequency_for_each_endpoint_name()
        res.to_csv(path)

    def __save_mean_response_time_for_each_frequency_for_each_endpoint_name_to_csv(self, path: str) -> None:
        res = self.get_mean_response_time_for_each_frequency_for_each_endpoint_name()
        res.to_csv(path)

    def save_all_to_csv(self, path: str) -> None:
        self.__save_mean_response_time_for_each_frequency_for_each_endpoint_name_to_csv(
            f'{path}/mean_response_time_for_each_frequency_for_each_endpoint_name.csv'
        )
        self.__save_codes_count_for_each_frequency_for_each_endpoint_name_to_csv(
            f'{path}/codes_count_for_each_frequency_for_each_endpoint_name.csv'
        )
