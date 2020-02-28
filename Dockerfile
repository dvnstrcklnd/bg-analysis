FROM jupyter/scipy-notebook as notebook-base

RUN pip install plotly \
    && pip install ipywidgets
