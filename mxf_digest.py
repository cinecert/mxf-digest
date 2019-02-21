#!/usr/bin/env python
#
# This program calculates a sha512 message digest over the set of
# sha512 digests created by digesting each KLV packet in an MXF file.
# The resulting digest is encoded as a URN value.
#
# Contact John Hurst jhurst@cinecert.com
#

import sys
import struct
import hashlib

MXF_MAX_RUNIN = 65536
MXF_RUNIN_END_MARKER = "\x06\x0e\x2b\x34\x02\x05\x01\x01\x0d\x01\x02"
MXF_DIGEST_LEN = 88
B58_RADIX = 58
B58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

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
def read_mxf_run_in(handle):
    """
    Read any run-in from the front of an MXF file and leave the file
    pointer at the first byte of the first partition. Returns the
    collected run-in or None if the header starts at offset zero.
    """
    count = 0
    runin_buffer = ""
    marker_buffer = ""

    while count < MXF_MAX_RUNIN:
        byte = handle.read(1)
        count += 1
        runin_buffer += byte
        if byte == MXF_RUNIN_END_MARKER[0]:
            marker_buffer = byte
        else:
            if marker_buffer:
                marker_buffer += byte
                l = len(marker_buffer)
                if marker_buffer[:l] != MXF_RUNIN_END_MARKER[:l]:
                    marker_buffer = ""
                elif l == len(MXF_RUNIN_END_MARKER):
                    # remove marker bytes from the end of the run-in buffer
                    if len(runin_buffer) > l:
                        runin_buffer = runin_buffer[:-l]
                    else:
                        runin_buffer = None
                    # seek to the start of the header
                    handle.seek(handle.tell()-l)
                    return runin_buffer

    raise ValueError("No MXF partiton found in allowable run-in.")


#
def mxf_digest_file(filename):
    """
    Return the sha512 message digest over the set of sha512 digests
    created by digesting each KLV packet read from the named file.
    """
    with open(filename) as reader:
        read_mxf_run_in(reader) # ignore run-in
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

        return md.digest()


#
def format_mxf_digest_urn(raw_digest):
    """
    Format a digest value as an MXF-DIGEST URN.
    """
    n = int(raw_digest.encode("hex"), 16)
    mxfid = ""

    while n:
        n, y = divmod(n, B58_RADIX)
        mxfid = B58_CHARS[y] + mxfid

    return "urn:smpte:mxf-digest:" + ("1"*(MXF_DIGEST_LEN - len(mxfid))) + mxfid


#
#
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("USAGE: mxf_digest.py <mxf-filename>+")
    for item in sys.argv[1:]:
        print ("({0}) {1}".format(
            item,
            format_mxf_digest_urn(mxf_digest_file(item))
        ))

#
# end mxf_digest.py
#
