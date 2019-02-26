#!/usr/bin/env python

import sys
sys.path.append("..")
import mxf_digest

template = "urn:smpte:mxf-digest:64pMA4dgr8iLqAEkiMpfJv2JHLubLY9wpDUeAcr3pto3gKGsszyCqr9ofBk668EJrVNagTW7WujyYZV9YEUqCRGE"
result = mxf_digest.format_mxf_digest_urn(mxf_digest.mxf_digest_file("oneframe.pcm.mxf"))

if result != template:
    raise RuntimeError("Result mismatch.")

print "PASS"

#
#
#
