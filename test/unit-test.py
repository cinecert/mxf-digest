#!/usr/bin/env python

import sys
import os
import hashlib
sys.path.append("..")
import mxf_digest


test_target = "oneframe.pcm.mxf"

## first, this program is designed to run from "test/"
if not os.path.exists(test_target):
    raise RuntimeError("The source file is missing or your $CWD is not the \"test/\" directory.")

## next, make sure that the input file is the one we're expecting
with open(test_target) as stream:
    md = hashlib.sha512()

    block = stream.read(8192)
    while block:
        md.update(block)
        block = stream.read(8192)

template = "f36392fcdb6af584b5c65f290399ca679eb37061e8dc2d5fe53dccd4750e39501d850ebcf9e25e34c84c0736b0ad53a32dc3dfe826a8e7b21a04df1f9c4b6821"
if template != md.hexdigest():
    raise RuntimeError("The source file is not appropriate for use with this version of the test.")

## calculate the mxf-digest and compare to the expected value
result = mxf_digest.format_mxf_digest_urn(mxf_digest.mxf_digest_file(test_target))
template = "urn:smpte:mxf-digest:64pMA4dgr8iLqAEkiMpfJv2JHLubLY9wpDUeAcr3pto3gKGsszyCqr9ofBk668EJrVNagTW7WujyYZV9YEUqCRGE"

if template != result:
    raise RuntimeError("Result mismatch.")

print "PASS"

#
#
#
