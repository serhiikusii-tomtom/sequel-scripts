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
        num += 1
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
    parser.add_argument("-pr", "--preferred-route", action="store_true", help="Filter only by preferred route if any")
    parser.add_argument("-o", "--out-file", help="save result to file")
    parser.add_argument("-d", "--devapp", action="store_true",
                        help="Since devapp logs are different this options help to parse devapp logs correctly")
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


def search_chanel(line, is_devapp):
    if is_devapp:
        return re.search(r'navigation-trip-onboardservice.RouteProgressUpdater\(.{8}\)', line)
    return re.search(r'navigation-trip-onboardservice-RouteProgressUpdater\(.{8}\)', line)


def search_time(line, is_devapp):
    #for devapp simply take symbol by symbol and convert it to eso trace time
    # 2023-08-11T04:03:58.538 -> 11.08.1970 04:03:58.538
    # TODO replace with datetime formater
    if is_devapp and len(line) >= 50:
        time_m = re.search(r'\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d', line[0:50])
        if time_m:
            datetime_str = string_or_empty(time_m)
            line = datetime_str[8:10]+"."+datetime_str[5:7]+".1970 " + datetime_str[11:23]
    
    return re.search(r'\d\d\.\d\d\.1970 \d\d:\d\d:\d\d\.\d\d\d', line)

def find_prefered_route_if_any(line, preferred_route):
    if re.search(r'Setting preferred route to invalid route', line):
        return None

    m_preferred_route = re.search(r'Setting preferred route to .{8}', line)
    if m_preferred_route:
        return m_preferred_route.group()[-8:]

    return preferred_route


def main():
    config = parse_args()
    if config['verbose']:
        print(config)
    route_filter = config['route']
    print(f"Parsing {config['log-file']} ...")
    # Progress splited into 2 lines: 1. Progress 2. Consumption and range
    # Consumption and range is calculating always but route progress can be not calculated
    # so merging 2 lines 
    with open(config['log-file'], 'r') as file:
        search_progress = "progress Progress\(offset"
        search_range = "CalculateConsumptionAndRange: consumption and range"
        prev_line = None
        preferred_route = None
        out_list = create_list()
        for line in file:
            if config['preferred_route']:
                preferred_route = find_prefered_route_if_any(line, preferred_route)
            if re.search(search_range, line):
                if config['verbose']:
                    print(line)
                m_chanel = search_chanel(line, config['devapp'])
                m_route = re.search(r'\(.{8}\)', string_or_empty(m_chanel))
                if route_filter and not route_filter in string_or_empty(m_route):
                    continue
                if preferred_route and not preferred_route in string_or_empty(m_route):
                    continue
                m_time = search_time(line, config['devapp'])
                m_offset = extract_number(re.search(r'offset: \d+ cm', line))
                m_consumption_and_range = re.search(
                    r'consumption and range: ConsumptionAndRange\{consumption: \d+\.?\d* kWh\, range: \d+ cm\}', line)
                m_consumption = extract_number(
                    re.search(r'consumption: \d+\.?\d* kWh', m_consumption_and_range.group()))
                m_range = extract_number(re.search(r'range: \d+ cm', line))
                # data from route progress
                if prev_line and re.search(search_progress, prev_line):
                    m_length = extract_number(
                        re.search(r'remaining length:\d+ cm', prev_line))
                    m_soc = extract_number(
                        re.search(r'vehicle state of charge:\d+.?\d*', prev_line))
                else:
                    m_length = None
                    m_soc = None
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
