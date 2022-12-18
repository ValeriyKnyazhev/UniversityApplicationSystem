FROM python:3.11.1-slim
WORKDIR /app

# Prepare env
RUN apt-get update && apt-get install -y wkhtmltopdf
RUN pip install bs4
RUN pip install colorama
RUN pip install dataclasses-json
RUN pip install IPython
RUN pip install jinja2
RUN pip install lxml
RUN pip install pandas
RUN pip install pdfkit

# Copy executable files
COPY ./generate_report.py /app/generate_report.py
COPY src/ /app/src

ENV STUDENT_ID=NOT_DEFINED
ENV TYPE=BRIEF
ENV INPUT_DIR=/app/data/applications
ENV OUTPUT_DIR=/app/data/reports

CMD ["sh", "-c", "python ./generate_report.py \
                         --student_id \"${STUDENT_ID}\" \
                         --type ${TYPE} \
                         --data_dir ${INPUT_DIR} \
                         --output_dir ${OUTPUT_DIR}"]
