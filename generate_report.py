import argparse

from src.core import StudentId
from src.application.service import ApplicationService
from src.application.loader import DataLoader
from src.application.visualizer import DataVisualizer, ReportType

parser = argparse.ArgumentParser()
parser.add_argument('--student_id', type=str, required=True, help="Student Id to generate report with statistics")
parser.add_argument('--data_dir', type=str, default="./data/", help="Path to directory with applications data files")
parser.add_argument('--type', type=str, default="BRIEF", help="Type of report: 'BRIEF' or 'FULL'")
parser.add_argument('--output_dir', type=str, default="./", help="Directory to save generated report")

args = parser.parse_args()

print("Preparing system for report generation...")
service = ApplicationService()
visualizer = DataVisualizer(service)

print(f"Loading data from '{args.data_dir}'...")
loader = DataLoader(service)
loader.load_data(args.data_dir)

report_type = ReportType[args.type]
print(f"Generating report for student [id={args.student_id}]...")

if visualizer.get_report_for(StudentId(args.student_id), report_type, output_dir=args.output_dir):
    print(f"Report successfully generated for student [id={args.student_id}].")
else:
    print(f"Report was not generated for student [id={args.student_id}].")
