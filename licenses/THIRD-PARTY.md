# Third-party components

The Windows patcher embeds the unmodified Windows x86-64 `xdelta3.exe` from Xdelta 3.2.1, including its LZMA decoder. Xdelta is by Joshua MacDonald and contributors, distributed under Apache-2.0. The release build is available at https://github.com/jmacd/xdelta/releases/tag/v3.2.1 .

The upstream decoder includes BLAKE3, also distributed under Apache-2.0. License copies are included in this folder and in the Windows download archive.

The upstream build also includes liblzma from XZ Utils, by the XZ Utils authors and contributors. liblzma is distributed under the BSD Zero Clause License (0BSD). See https://github.com/tukaani-project/xz/blob/v5.8.1/COPYING .

The patcher source and build scripts in this repository were created for this Korean translation release. Game content and original artwork belong to their respective copyright holders.
