FROM python
COPY src/ /usr/src/app
ARG TOKEN
ARG AWS_ACCESS_KEY_ID_ARG
ARG AWS_SECRET_ACCESS_KEY_ARG
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_ARG
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_ARG
ENV AWS_REGION=us-east-2
ENV JAILBOT_TOKEN=$TOKEN
RUN pip install discord
RUN pip install boto3
RUN apt-get update && apt-get install -y unzip curl
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install
CMD ["python", "usr/src/app/bot.py"]
