import matplotlib.pyplot as plt
import csv
import argparse
import re
import sys
# from datetime import datetime


def save_to_file(out_list, out_file):
    print(f"Saving to file {out_file}")

    with open(out_file, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        for line in out_list:
            writer.writerow(line)


def find_index(in_list, column_name):
    for index, item in enumerate(in_list):
        if item == column_name:
            return index
    return -1

def plot_graph(in_list):
    print("Plot chart")
    # to save time I relay on the order in the insert_line()
    x = []
    y = []
    num = 0
    range_idx = find_index(in_list[0], "range")
    if (range_idx < 0):
        print("ERROR range column was not found")
        sys.exit(2)

    for line in in_list:
        num+=1
        if num == 1:
            # skip header
            continue
        # TODO fix dates
        # date = line[0]
        # date_format = '%d.%m.%Y %H:%M:%S.%f'
        # date_obj = datetime.strptime(date, date_format)
        # x.append(date_obj)
        x.append(num)
        range_km = float(line[range_idx])/100000
        y.append(range_km)

    plt.plot(x, y)

    plt.xlabel('line number')
    plt.ylabel('range')
    plt.title('range changes!')
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Parse route progress from log file and return table with logger time soc and range on route",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="verbose logs")
    parser.add_argument("-r", "--route", help="only for specific route")
    parser.add_argument("-p", "--plot", action="store_true", help="plot chart")
    parser.add_argument("-o", "--out-file", help="save result to file")
    parser.add_argument("log-file", help="log file to parse")
    args = parser.parse_args()
    config = vars(args)
    return config


def extract_number(re_match):
    if re_match:
        return re.search(r'\d+\.?\d*', re_match.group())
    return None


def string_or_empty(re_match):
    if re_match:
        return re_match.group()
    return ""


def create_list():
    return [["time", "route", "offset", "remaining length",
             "soc", "consumption", "range"]]


def insert_line(out_list, time, route, offset, length, soc, consumption, range):
    out_list.append([string_or_empty(time), string_or_empty(route), string_or_empty(offset), string_or_empty(
        length), string_or_empty(soc), string_or_empty(consumption), string_or_empty(range)])


def main():

    config = parse_args()
    if config['verbose']:
        print(config)
    route_filter = config['route']
    print(f"Parsing {config['log-file']} ...")
    with open(config['log-file'], 'r') as file:
        search_progress = "OnPositionUpdate: progress Progress"
        out_list = create_list()
        for line in file:
            if re.search(search_progress, line):
                if config['verbose']:
                    print(line)
                m_chanel = re.search(r'navigation-trip-onboardservice-Route\(.{8}\)', line)
                m_route = re.search(r'\(.{8}\)', string_or_empty(m_chanel))
                if route_filter and not route_filter in string_or_empty(m_route):
                    continue
                m_time = re.search(r'01.01.1970 \d\d:\d\d:\d\d\.\d\d\d', line)
                m_offset = extract_number(re.search(r'offset:\d+ cm', line))
                m_length = extract_number(
                    re.search(r'remaining length:\d+ cm', line))
                m_soc = extract_number(
                    re.search(r'vehicle state of charge:\d+.?\d*', line))
                m_consumption_and_range = re.search(
                    r'consumption and range:ConsumptionAndRange\{consumption: \d+\.?\d* kWh\, range: \d+ cm\}', line)
                m_consumption = extract_number(
                    re.search(r'consumption: \d+\.?\d* kWh', m_consumption_and_range.group()))
                m_range = extract_number(re.search(r'range: \d+ cm', line))
                insert_line(out_list, m_time, m_route, m_offset, m_length,
                            m_soc, m_consumption, m_range)
        if config["out_file"]:
            save_to_file(out_list, config["out_file"])
        if config['verbose'] or not config["out_file"]:
            print(out_list)
        if config['plot']:
            plot_graph(out_list)

    print("Finished")


if __name__ == "__main__":
    main()