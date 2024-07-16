import csv
import json
import os
from datetime import datetime


class PM25Processor:
    def __init__(self, device_name, threshold):
        self.device_name = device_name
        self.threshold = threshold
        self.csv_file = f'{device_name}_pm25_threshold_{threshold}.csv'

    def read_csv(self):
        if not os.path.exists(self.csv_file):
            return []

        data = []
        with open(self.csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['pm25'] = float(row['pm25'])
                data.append(row)
        return data

    def write_csv(self, data):
        file_exists = os.path.exists(self.csv_file)

        with open(self.csv_file, mode='a', newline='') as file:
            fieldnames = ['timestamp', 'pm25']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for entry in data:
                writer.writerow(entry)

    @staticmethod
    def parse_data(api_response):
        data = []
        feeds = api_response.get('feeds', [])
        for feed in feeds:
            for app_data_list in feed.values():
                for app_data in app_data_list:
                    for timestamp, entry in app_data.items():
                        pm25 = entry.get('s_d0')
                        if pm25 is not None:
                            data.append({'timestamp': timestamp, 'pm25': pm25})
        return data

    def insert_data(self, new_data):
        existing_data = self.read_csv()
        existing_timestamps = {entry['timestamp'] for entry in existing_data}

        data_to_insert = [entry for entry in new_data if entry['timestamp'] not in existing_timestamps]
        self.write_csv(data_to_insert)

    def analyze_data(self):
        data = self.read_csv()
        periods_above_threshold = []
        daily_stats = {}

        for entry in data:
            timestamp = datetime.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            pm25 = entry['pm25']

            if pm25 > self.threshold:
                periods_above_threshold.append(entry['timestamp'])

            day = timestamp.date()
            if day not in daily_stats:
                daily_stats[day] = {'max': pm25, 'min': pm25, 'total': pm25, 'count': 1}
            else:
                daily_stats[day]['max'] = max(daily_stats[day]['max'], pm25)
                daily_stats[day]['min'] = min(daily_stats[day]['min'], pm25)
                daily_stats[day]['total'] += pm25
                daily_stats[day]['count'] += 1

        for day in daily_stats:
            daily_stats[day]['avg'] = daily_stats[day]['total'] / daily_stats[day]['count']

        return periods_above_threshold, daily_stats

    @staticmethod
    def generate_report(periods_above_threshold, daily_stats):
        str_daily_stats = {str(key): value for key, value in daily_stats.items()}
        report = {
            "periods_above_threshold": periods_above_threshold,
            "daily_stats": str_daily_stats
        }
        return json.dumps(report, indent=4)
