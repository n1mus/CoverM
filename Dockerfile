FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update



# Install coverm
RUN curl --location https://github.com/wwood/CoverM/releases/download/v0.3.0/coverm-x86_64-unknown-linux-musl-0.3.0.tar.gz > coverm.tar.gz
RUN tar xvfz coverm.tar.gz
RUN mv coverm-x86_64-unknown-linux-musl-0.3.0/coverm /usr/local/bin/coverm
RUN rm -r coverm*

# Install minimap2
RUN curl -L https://github.com/lh3/minimap2/releases/download/v2.17/minimap2-2.17_x64-linux.tar.bz2 | tar -jxvf -
RUN mv minimap2-2.17_x64-linux/minimap2 /usr/local/bin/minimap2
RUN rm -rf minimap2-2.17_x64-linux/

# Install samtools
RUN sudo apt-get --yes update
RUN sudo apt-get --yes install gcc
RUN sudo apt-get --yes install make
RUN sudo apt-get --yes install libbz2-dev
RUN sudo apt-get --yes install zlib1g-dev
RUN sudo apt-get --yes install libncurses5-dev 
RUN sudo apt-get --yes install libncursesw5-dev
RUN sudo apt-get --yes install liblzma-dev
RUN curl --location https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2 > samtools-1.9.tar.bz2
RUN tar -vxjf samtools-1.9.tar.bz2 && rm -rf samtools-1.9.tar.bz2
RUN cd samtools-1.9 && make
RUN mv samtools-1.9 /usr/local/bin/samtools-1.9
ENV PATH="${PATH}:/usr/local/bin/samtools-1.9"

# Install pandas & matplotlib
RUN conda install --yes pandas
RUN conda install --yes matplotlib
RUN conda install --yes numpy

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
