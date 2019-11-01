FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

RUN curl --location https://github.com/wwood/CoverM/releases/download/v0.3.0/coverm-x86_64-unknown-linux-musl-0.3.0.tar.gz > coverm.tar.gz
RUN tar xvfz coverm.tar.gz
RUN mv coverm-x86_64-unknown-linux-musl-0.3.0/coverm /usr/local/bin/coverm
RUN rm -r coverm*


# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
