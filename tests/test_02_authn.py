import os

BASE_CMD = "python3 src/spid_sp_test/spid_sp_test"
BASE_METADATA = "spid-django-other.xml"
CMD = BASE_CMD + " --extra --metadata-url file://tests/metadata/{} --authn-url file://tests/authn/{}"


def run_cmd(mfname, metadata = BASE_METADATA) -> int:
    cmd = CMD.format(metadata, mfname)
    return os.system(cmd)


def test_django_post_html():
    es = run_cmd('spid_django_post.html')
    assert es == 0


def test_django_post():
    es = run_cmd('spid_django.xml')
    assert es == 0


def test_django_redirect():
    """
        ERROR:spid_sp_test.authn_request:The ProtocolBinding attribute must be urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST - TR pag. 8  : FAILED
    """
    es = run_cmd('spid_django_redirect.url')
    assert es != 0

def test_spid_express_no_relaystate():
    es = run_cmd("spid_express_no_relaystate_redirect.url",
                 metadata = "spid_express_no_relaystate_metadata.xml")
    assert es == 0
