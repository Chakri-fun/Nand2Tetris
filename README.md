# Nand2Tetris: Building a Modern Computer from First Principles

This repository contains the full suite of projects completed for the **CS2310** course (Semester 3) at **IIT Madras**, under the guidance of **Prof. V. Kamakoti**.

The curriculum follows the renowned [Nand2Tetris](https://www.nand2tetris.org/) syllabus, a journey that begins with a logic gate (NAND) and ends with a fully functional computer system capable of running simple games.

## Project Overview
### Hardware (Projects 1 – 6)

The goal was to build the **Hack Computer**, a 16-bit general-purpose system.

* **Combinational Logic:** Built basic gates (AND, OR, XOR) and a full 16-bit ALU.
* **Sequential Logic:** Developed memory systems, including RAM units and Program Counters.
* **Architecture:** Integrated the CPU and Memory into the final hardware platform.
* **Assembler:** Wrote a tool to translate Hack Assembly into binary machine code.

### Software Stack (Projects 7 – 12)

The goal was to create the hierarchy required to run high-level code on the Hack hardware.

* **Virtual Machine:** Built a VM translator to bridge the gap between high-level code and assembly.
* **Jack Compiler:** Developed a syntax analyzer and code generator for **Jack** (an object-oriented language).
* **Operating System:** Implemented a basic OS in Jack to handle memory management.

---

## Technical Stack

* **Software:** Python is used for the Assembler, VM Translator, and Compiler.
