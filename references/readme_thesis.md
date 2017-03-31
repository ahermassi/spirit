# A UAV Teleoperation System Using Subimposed Past Image Records

### 過去画像を用いた飛行ロボットの遠隔操作手法

This document was typeset using the XeTeX typesetting system created by the Non-Roman Script Initiative and the memoir class created by Peter Wilson.
The text is set in 10pt in Linux Libertine O.
The other fonts used include Linux Biolinum O, `Deja Vu Sans Mono`, and IPA Mincho (明朝).

All the files for the thesis are contained in the [`reports/thesis`](../reports/thesis) directory.

## Table of Contents

* [Structure](#structure)
* [Building](#building)
* [Licensing](#licensing)

## Structure
The following files are available:

* [`Makefile`](../reports/thesis/Makefile), which allows you to build the file. See the [Building](#building) section for more details.
* [`masastyle.sty`](../reports/thesis/masastyle.sty), which defines the entire preamble, including PDF metadata, glossary and bibliogrpahy settings, and formatting for `tikz` and XeLaTeX.
* [`glossary.tex`](../reports/thesis/glossary.tex), which contains the glossary and appendix, as well as the symbol list.
Entries appear upon first use in the text.
The symbol list is used in the thesis instead of hardcoding any variables.
This allows for flexibility, and also happens to hyperlink every instance of a variable to its corresponding symbol in the back.
* [`mshtsy_thesis.bib`](../reports/thesis/mshtsy_thesis.bib), which contains the bibliography.
References are added to that section when they are cited.
* [`mshtsy_thesis.tex`](../reports/thesis/mshtsy_thesis.tex), the main body of the thesis.
In its current implementation, it just includes the necessary files in the right order, and adds labels for them.
All other `.tex` files are part of the thesis and can thus be [included individually](../reports/thesis/mshtsy_thesis.tex#L9).

Images are in the [`img`](../reports/thesis/img) directory, and plots are in the [`plots`](../reports/thesis/img/plots) subdirectory.
Graphviz is used for the flowcharts.
Currently, the only flowchart is in [`img/flowchart.dot`](../reports/thesis/img/flowchart.dot`).

## Building
Before building, please run the analysis suite in order to generate the PGF plots to be included.

On first build, you need to use `make full` to generate the necessary files.
For changes in the glossary to be reflected, `make refs` needs to be run.
Otherwise, `make` is usually enough.

For a full listing of `Makefile` targets, run `make help`.

Result text and table data is currently hardcoded, but `pandas` can generate LaTeX tables and Python can fill in the blanks with a templating engine such as Jinja2 or Mako.
It is recommended that future users implement such a system to automate the entire pipeline and keep the PDF up-to-date as more experiments are run.
A prototype of this was tested, but was not included in the final version.

## Licensing
![CC-BY-SA](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)
Copyright © 2017 by Jean Nassar.

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit:
http://creativecommons.org/licenses/by-sa/4.0/
