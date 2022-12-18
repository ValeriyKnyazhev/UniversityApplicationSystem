# UniversityApplicationSystem
System that helps enrollees to understand the current rating in all universities

Instructions:
1. To install `dataclasses-json` use ```pip install dataclasses-json```
2. To install `pdfkit` use ```pip install pdfkit```
3. To install `wkhtmltopdf` find all instructions on the following website https://wkhtmltopdf.org/downloads.html

### Python script to generate report
``` commandline
python generate_report.py \
    --student_id '185-597-938 50' \
    --data_dir ./data/ \
    --type FULL \
    --output_dir ./reports/
```

### Docker to generate report
#### Build docker image
``` commandline
docker image build -t generate_report:0.1 ./
```
#### Run docker container
``` commandline
docker run \
    --mount src="$(pwd)/data",target=/app/data/applications,type=bind \
    --mount src="$(pwd)",target=/app/data/reports,type=bind \
    -e STUDENT_ID="185-597-938 50" \
    -e TYPE=FULL \
    generate_report:0.1
```