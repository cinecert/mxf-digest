# MXF-DIGEST

## Status

This DRAFT memo describes a proposed method for use by MXF applications. At this time the memo is open for comment. If the proposal is adopted by a sufficiently large subset of the MXF community it will then be submitted to [SMPTE](https://www.smpte.org) for publication as standard (ST) engineering document. Substantial changes to this memo may occur during this process, and implementors are cautioned against making permanent implementation or deployment decisions based on its current contents.

This document and associated reference implementation are hosted at https://github.com/cinecert/mxf-digest

## Introduction

SMPTE ST 377-1 Material Exchange Format (MXF) files are often very large (comprising tens or even hundreds of *gigabytes*), and transferring such files or even transiting them over a system bus to a CPU requires non-trivial resources. In addition, many file-based applications use message digest algorithms to uniquely identify files. The intersection of these two properties is a source of friction in many workflows, both because digesting files after writing them is resource intensive, and because the input to digest algorithms commonly utilized by these systems is inherently serial in nature while parallel processing of file contents is increasingly common. What is needed is a method of digesting large MXF files that supports both parallel calculation and out-of-order calculation.

The proposed algorithm works with any serial-input digest by using the KLV sub-structure of an MXF file as a natural segmentation layer upon which to calculate an ordered set of digests. The digest values in this ordered set can then be the subject of another digest, finally producing an identifier that is appropriately unique within the scope of the chosen digest algorithm. For maximum interoperability a single digest algorithm should be chosen for use by this process.

## Normative References

(TODO: decide on a linking style)

[1]: SMPTE ST 377-1:2011 — Material Exchange Format (MXF) — File Format Specification

[2]: SMPTE ST 2029:2009 — Uniform Resource Names for SMPTE Resources

[3]: ISO/IEC 10118-3:2004 Information technology — Security techniques — Hash-functions — Part 3: Dedicated hash-functions

[4]: IETF RFC 4234 — Augmented BNF for Syntax Specifications: ABNF

## MXF-DIGEST calculation

### Primitive Digest Algorithm

The primitive message digest algorithm shall be SHA512 as defined in ISO/IEC 10118-3.

### MXF Run-In

Skip run-in as described in ST 377-1, Sec. 6.5, Run-In Sequence.

TODO: complete and implement prototype.

### KLV Packet Digests

* Establish an empty list of digest values
* For each KLV packet (Individual data items and top-level Sets) in the file:
  * instantiate a fresh Primitive Digest context (a *packet digest*)
  * Update the digest context with all of the bytes comprising the KLV packet (the packet shall be digested in its original form:  expansion or translation of BER items shall not be performed)
  * finalize the digest context and append it to the list of digest values

### Sequence Digest

* instantiate a fresh Primitive Digest context (the *sequence digest*)
* For each packet digest in the list of digest values:
  * update the sequence digest context with the binary value of the packet digest
* Finalize the sequence digest

### Canonical Encoding

The MXF-DIGEST value is created by encoding the sequence digest value as URN item of the form "urn:smpte:mxf-digest:&lt;hex-digits&gt;", where "mxf-digest" is a registered NSS as defined in this document, and &lt;hex-digits&gt; is the hexadecimal encoding of the sequence digest.

### Equivalence

While the normative  algorithm processes the KLV packets in order, it should be noted that the packet digest values may be calculated in any order, at any time, so long as they are contributed to the sequence digest completely and in the same order in which the respective KLV packets appear in the MXF file. Any out-of-order calculation of MXF Digest that produces a value equal to the normative algorithm presented above is in compliance with this standard.

## MXF-DIGEST URN NSS

The NSS of URNs for an MXF-DIGEST value shall begin with "mxf-digest:". The identifier structure for the MXF-DIGEST subnamespace (MXF-DIGEST-NSS), described using IETF RFC 4234 (EBNF) shall be:

```EBNF
MXF-DIGEST-NSS = "smpte:mxf-digest:" MXF-DIGEST
MXF-DIGEST = 128BYTE
BYTE = 2HEXDIG
```

The hexadecimal digits in the URN representation of an MXF-DIGEST shall be the hexadecimal representation of the MXF-DIGEST octets. The values of MXF-DIGEST shall be produced as defined in "Sequence Digest" in this document. Lexical equivalence of MXF-DIGEST URNs shall be determined by an exact string match that is case-insensitive for alphabetical characters.

TODO: What do we want here to correctly anchor the NSS definition to ST 2029?

### A note regarding SMPTE ST 2114  "C4 ID"

The astute reader may notice that there is already a digest-based SMPTE standard for file identification (ST 2114:2017), and that a process for identifying a set of items is included in that standard. The algorithm for C4 ID for Non-contiguous Blocks of Data however sorts and de-duplicates the constituent block digests, resulting in a process that would produce the same identifier for two MXF files that differ only in the order of their respective KLV packets, or in the repetition of certain identical packets. For this reason ST 2114 is considered unsuitable for this application.

## Bibliography

[5]: SMPTE ST 2114:2017 — Unique Digital Media Identifier (C4 ID)
