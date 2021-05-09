# docker build -t package-lambda .
# docker run --rm -it -v /tmp:/tmp package-lambda
FROM amazonlinux
ENV lambdaName getVaultItems
ENV lambdaDirectory ./vault/getVaultItems
WORKDIR /package
COPY . .
RUN yum install -y amazon-linux-extras && \
    amazon-linux-extras enable python3.8 && \
    yum install -y python3.8 zip && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
CMD ./package-lambda.sh ${lambdaName} ${lambdaDirectory}
