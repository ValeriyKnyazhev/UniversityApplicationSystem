# UniversityApplicationSystem
System that helps enrollees to understand the current rating in all universities

Instructions:
1. To install `dataclasses-json` use ```pip install dataclasses-json```
2. To install `pdfkit` use ```pip install pdfkit```
3. To install `wkhtmltopdf` find all instructions on the following website https://wkhtmltopdf.org/downloads.html

# Python script to generate report
```
python generate_report.py \
    --student_id '185-597-938 50' \
    --data_dir ./data/ \
    --type FULL \
    --output_dir ./reports/
```
