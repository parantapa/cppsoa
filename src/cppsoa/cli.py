"""Command line interface."""

from dataclasses import dataclass

import click
import json5
from pydantic import BaseModel

from .templates import render

DataColumns = dict[str, str]


class DataStructures(BaseModel):
    namespace: str
    headers: list[str]
    vector: dict[str, DataColumns]

    def add_header(self, header: str):
        if header not in self.headers:
            self.headers.append(header)


@dataclass
class Column:
    name: str
    type: str


@click.command()
@click.option(
    "-i",
    "--input",
    "input_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    help="Input file",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    required=True,
    help="Output file",
)
def cli(input_file: str, output_file: str):
    """Struct of array generator."""
    input: DataStructures
    with open(input_file, "rt") as fobj:
        input = DataStructures.model_validate(json5.load(fobj))

    with open(output_file, "wt") as fobj:
        fobj.write("#pragma once\n")
        fobj.write("// This code is auto generated.\n")
        fobj.write("// Do not edit manually.\n\n")

        if input.vector:
            input.add_header("vector")

        for header in input.headers:
            fobj.write(f"#include <{header}>\n")
        fobj.write("\n")

        namespace = input.namespace
        fobj.write(f"namespace {namespace} {{\n\n")

        for itype, icols in input.vector.items():
            otype = itype
            ocols = []
            for name, type in icols.items():
                ocols.append(Column(type=type, name=name))

            struct_str = render("vector:vector", type=otype, cols=ocols)
            fobj.write(struct_str)
            fobj.write("\n\n")

        fobj.write(f"}} // namespace {namespace}")
