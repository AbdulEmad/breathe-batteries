from pm25_client import PM25Client
from pm25_processor import PM25Processor

device_id = "FT2_0176"
threshold = 30

client = PM25Client(device_id)
api_response = client.fetch_device_history()

pm25_processor = PM25Processor(device_id, threshold)
parsed_data = PM25Processor.parse_data(api_response)
pm25_processor.insert_data(parsed_data)

periods_above_threshold, daily_stats = pm25_processor.analyze_data()
report = PM25Processor.generate_report(periods_above_threshold, daily_stats)
print(report)
