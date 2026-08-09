FROM docker.io/library/python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
WORKDIR /opt/scdesignguard
COPY artifacts/scdesignguard_nm03-0.1.0-py3-none-any.whl /tmp/scdesignguard_nm03-0.1.0-py3-none-any.whl
RUN python -m pip install --no-cache-dir --no-index --no-deps /tmp/scdesignguard_nm03-0.1.0-py3-none-any.whl && \
    rm /tmp/scdesignguard_nm03-0.1.0-py3-none-any.whl && \
    useradd --system --uid 65532 --no-create-home scdesignguard
USER 65532:65532
ENTRYPOINT ["scdesignguard"]
CMD ["--help"]
