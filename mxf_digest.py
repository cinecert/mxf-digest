#!/usr/bin/env python
#
# This program calculates a sha512 message digest over the set of
# sha512 digests created by digesting each KLV packet in an MXF file.
#
# Contact John Hurst jhurst@cinecert.com
#



import sys
import struct
import hashlib

# ST 336 for Individual Data Items and Top-Level Sets
KEY_LENGTH = 16

#
def decode_BER_int_from_stream(reader):
    """
    Decode a BER-encoded integer from a stream and return the decoded value.
    Reads only enough bytes to complete the value.
    """
    value = struct.unpack("B", reader.read(1))[0] # Decode the first byte

    if value > 127:
        # Decode the extended value
        value = int(reader.read(value - 128).encode("hex"), 16)

    return value

#
def decode_BER_oid_from_stream(reader):
    """
    Decode a BER-encoded object id from a stream and return the decoded value.
    Respects only SMPTE ST 336 ULs corresponding to Individual Data Items and
    Top-Level Sets
    """
    preamble = reader.read(4)
    if len(preamble) == 0:
        return None

    if struct.unpack("BBBB", preamble) != (0x06, 0x0e, 0x2b, 0x34):
        raise ValueError("Unexpected OID encoding: 0x{0}.".format(
                preamble.encode("hex")))

    remainder = reader.read(12)
    return preamble+remainder

#
def parse_klv_stream(reader):
    """
    Yields (key, length) for each KLV packet decoded from the input stream.
    """
    while True:
        key = decode_BER_oid_from_stream(reader)
        if key is None:
            raise StopIteration()

        length = decode_BER_int_from_stream(reader)
        yield key, length

#
def mxf_digest_file(filename):
    """
    Return an un-finalized sha512 message digest over the set
    of sha512 digests created by digesting each KLV packet read
    from the named file.
    """
    with open(filename) as reader:
        digest_list = []
        start_position = reader.tell()

        # collect the KLV packet digests
        for k, l in parse_klv_stream(reader):
            v_position = reader.tell()
            reader.seek(start_position)

            md = hashlib.sha512()
            md.update(reader.read(v_position-start_position+l))
            digest_list.append(md.digest())
            start_position = reader.tell()

        # produce the sequence digest
        md = hashlib.sha512()

        for item in digest_list:
            md.update(item)

        return md

#
def format_mxf_digest_urn(md):
    """
    Finalize a sequence digest and format it as an MXF-DIGEST URN
    """
    return "urn:smpte:mxf-digest:{0}".format(md.hexdigest())

#
#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise UsageError("What")
    for item in sys.argv[1:]:
        print ("({0}) {1}".format(
            item,
            format_mxf_digest_urn(mxf_digest_file(item))
        ))

#
# end mxf_digest.py
#
