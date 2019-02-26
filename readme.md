# MXF-DIGEST

   * [Status](#status)
   * [Introduction](#introduction)
   * [Normative References](#normative-references)
   * [MXF-DIGEST calculation](#mxf-digest-calculation)
      * [MXF Run-In](#mxf-run-in)
      * [KLV Packet Digests](#klv-packet-digests)
      * [Sequence Digest](#sequence-digest)
      * [Canonical Encoding](#canonical-encoding)
      * [Example](#example)
   * [Equivalence](#equivalence)
   * [MXF-DIGEST URN](#mxf-digest-urn)
      * [MXF-DIGEST URN NID](#mxf-digest-urn-nid)
      * [MXF-DIGEST URN NSS](#mxf-digest-urn-nss)
   * [Bibliography](#bibliography)

## Status

This DRAFT memo describes a proposed method for use by MXF applications. At this time the memo is open for comment. If the proposal is adopted by a sufficiently large subset of the MXF community it will then be submitted to [SMPTE](https://www.smpte.org) for publication as standard (ST) engineering document. Substantial changes to this memo may occur during this process, and implementors are cautioned against making permanent implementation or deployment decisions based on its current contents.

This document and associated reference implementation are hosted at https://github.com/cinecert/mxf-digest

## Introduction

SMPTE ST 377-1 Material Exchange Format (MXF) files are often very large (comprising tens or even hundreds of *gigabytes*), and transferring such files or even transiting them over a system bus to a CPU requires non-trivial resources. In addition, many file-based applications use message digest algorithms to uniquely identify files. The intersection of these two properties is a source of friction in many workflows, both because digesting files after writing them is resource intensive, and because the input to digest algorithms commonly utilized by these systems is inherently serial in nature while parallel processing of file contents is increasingly common. What is needed is a method of digesting large MXF files that supports both parallel calculation and out-of-order calculation.

The proposed algorithm works with any serial-input digest by using the KLV sub-structure of an MXF file as a natural segmentation layer upon which to calculate an ordered set of digests. The digest values in this ordered set can then be the subject of another digest, finally producing an identifier that is appropriately unique within the scope of the chosen digest algorithm. For maximum interoperability a single digest algorithm should be chosen for use by this process, and so this proposal selects SHA-512.

The resulting digest value must have a canonical encoding to promote interoperable use across applications. This proposal defines a URN encoding which employs a Base58 alphabet chosen for brevity and lack of ambiguity when used with common path separators.


## Normative References

[SMPTE ST 336:2007 — Data Encoding Protocol Using Key-Length-Value](https://doi.org/10.5594/SMPTE.ST336.2007)

[SMPTE ST 377-1:2011 — Material Exchange Format (MXF) — File Format Specification](https://doi.org/10.5594/SMPTE.ST377-1.2011)

[SMPTE ST 2029:2009 — Uniform Resource Names for SMPTE Resources](https://doi.org/10.5594/SMPTE.ST2029.2009)

[SMPTE ST 2114:2017 — Unique Digital Media Identifier (C4 ID)](https://doi.org/10.5594/SMPTE.ST2114.2017)

[ISO/IEC 10118-3:2004 Information technology — Security techniques — Hash-functions — Part 3: Dedicated hash-functions](https://www.iso.org/standard/39876.html)

[IETF RFC 4234 — Augmented BNF for Syntax Specifications: ABNF](https://www.ietf.org/rfc/rfc4234.txt)


## MXF-DIGEST calculation


### Primitive Digest Algorithm

The primitive message digest algorithm shall be SHA512 as defined in [ISO/IEC 10118-3](https://www.iso.org/standard/39876.html).


### MXF Run-In

Run-in, as defined in [ST 377-1](https://doi.org/10.5594/SMPTE.ST377-1.2011), Sec. 6.5, "Run-In Sequence", shall not be contributed to the digest. If present, run-in bytes shall be skipped before digest calculation begins.

Note to IMF implementors: <b>There is no run-in in IMF.</b> MXF run-in is disallowed for use by the [IMF Essence Component](https://doi.org/10.5594/SMPTE.ST2067-5.2013). This provision of the MXF-DIGEST process exists for maximum compatibility with other MXF applications.


### KLV Packet Digests

The algorithm shall operate on complete KLV packets, as defined in [SMPTE ST 336](https://doi.org/10.5594/SMPTE.ST336.2007), which shall be digested in their original form. Expansion or translation of BER-encoded Key or Value Length fields shall not be performed.

* Establish an empty list of digest values
* For each KLV packet in the file:
  * Instantiate a fresh Primitive Digest context (a *packet digest*)
  * Update the packet digest context with all of the bytes comprising the KLV packet
  * Finalize the packet digest context and append its value to the list of digest values


### Sequence Digest

* Instantiate a fresh Primitive Digest context (the *sequence digest*)
* For each packet digest in the list of digest values:
  * update the sequence digest context with the binary value of the packet digest
* Finalize the sequence digest


### Canonical Encoding

The MXF-DIGEST value is created by encoding the sequence digest value as URN item of the form `urn:smpte:mxf-digest:<b58-digits>`, where `mxf-digest` is a registered NSS as defined in this document, and `<b58-digits>` is the Base58 encoding of the sequence digest value octets. The Base58 encoding shall be interpreted as defined in [SMPTE ST 2114](https://doi.org/10.5594/SMPTE.ST2114.2017), Sec. 5.1 "C4 Base58".


#### Example

`urn:smpte:mxf-digest:64pMA4dgr8iLqAEkiMpfJv2JHLubLY9wpDUeAcr3pto3gKGsszyCqr9ofBk668EJrVNagTW7WujyYZV9YEUqCRGE`


## Equivalence

While the normative algorithm processes the KLV packets in order, it should be noted that the packet digest values may be calculated in any order, at any time, so long as they are contributed to the sequence digest completely and in the same order in which the respective KLV packets appear in the MXF file. For a given list of KLV packets, any out-of-order calculation of MXF Digest that produces a value equal to the normative algorithm presented above in [MXF-DIGEST calculation](#mxf-digest-calculation) is in compliance with this memo.


## MXF-DIGEST URN

### MXF-DIGEST URN NID

The NID of an MXF-DIGEST URN shall be `smpte`, as defined in [SMPTE ST 2029](https://doi.org/10.5594/SMPTE.ST2029.2009).

### MXF-DIGEST URN NSS

The NSS of an MXF-DIGEST URN shall begin with `mxf-digest:`. The identifier structure for the MXF-DIGEST subnamespace (MXF-DIGEST-NSS), described using [IETF RFC 4234 (EBNF)](https://www.ietf.org/rfc/rfc4234.txt), shall be:

```BNF
MXF-DIGEST-NSS  = "smpte:mxf-digest:" MXF-DIGEST
MXF-DIGEST      = 88*B58-DIGIT
B58-DIGIT       = %x31-39 / ; 1-9
                  %x41-48 / ; A-H
                  %x4a-4e / ; J-N
                  %x50-5a / ; P-Z
                  %x61-6b / ; a-k
                  %x6d-7a / ; m-z
```

The Base58 digits in the URN representation of an MXF-DIGEST shall be the Base58 representation of the [Sequence Digest](#sequence-digest). Lexical equivalence of MXF-DIGEST URN values shall be determined by an exact string match that is case-sensitive for B58-DIGIT characters.


## Bibliography

[SMPTE ST 2067-5:2013 — Interoperable Master Format — Essence Component](https://doi.org/10.5594/SMPTE.ST2067-5.2013)

