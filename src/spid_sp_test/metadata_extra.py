import datetime
import os

from spid_sp_test import constants
from spid_sp_test.dump_pem import dump_metadata_pem
from spid_sp_test.utils import parse_pem

from . metadata import SpidSpMetadataCheck


class SpidSpMetadataCheckExtra(SpidSpMetadataCheck):

    def __init__(self, *args, **kwargs):

        super(SpidSpMetadataCheckExtra, self).__init__(*args, **kwargs)
        self.category = 'metadata_extra'

    def test_Signature_extra(self):
        '''Test the compliance of AuthnRequest element'''

        sign = self.doc.xpath('//EntityDescriptor/Signature')

        desc = [ent.attrib for ent in sign if sign]
        error_kwargs = dict(description = desc) if desc else {}

        for si in sign:
            certs = si.xpath('./KeyInfo/X509Data/X509Certificate')

            for i in range(len(certs)):
                cert = certs[i]
                fname = dump_metadata_pem(cert, 'sp', 'signature', '/tmp')

                r = parse_pem(fname)
                self._assertFalse(
                    r[0].lower().startswith('sha1'),
                    ((f'The certificate #{i} must not use '
                      f'weak signature algorithm: {r[0].lower()}')),
                      **error_kwargs
                )

                exp = ['rsaEncryption', 'id-ecPublicKey']
                self._assertIn(
                    r[2],
                    exp,
                    ((f'The key type of certificate #{i} must be one of [%s] - TR pag. 19') %
                     (', '.join(exp))),
                     **error_kwargs
                )

                if r[2] == 'rsaEncryption':
                    exp = constants.MINIMUM_CERTIFICATE_LENGHT
                elif r[2] == 'id-ecPublicKey':
                    exp = 256
                else:
                    pass

                self._assertTrue(
                    (int(r[1]) >= exp),
                    f'The key length of certificate #{i} must be >= {exp}. Instead it is {r[1]}',
                     **error_kwargs
                )

                self._assertTrue(
                    (datetime.datetime.strptime(
                        r[3], "%b %d %H:%M:%S %Y") >= datetime.datetime.now()
                    ),
                    f'The certificate #{i} is expired. It was valid till {r[3]}',
                    **error_kwargs
                )
                os.remove(fname)
        return self.is_ok(
            f'{self.__class__.__name__}.test_Signature_extra'
        )

    def test_SPSSODescriptor_extra(self):
        spsso = self.doc.xpath('//EntityDescriptor/SPSSODescriptor')

        desc = [ent.attrib for ent in spsso if spsso]
        error_kwargs = dict(description = desc) if desc else {}

        for attr in ['protocolSupportEnumeration', 'WantAssertionsSigned']:
            self._assertTrue(
                (attr in spsso[0].attrib),
                f'The {attr} attribute must be present'
            )

            if attr == 'protocolSupportEnumeration':
                a = spsso[0].get(attr)
                self._assertIsNotNone(
                    a,
                    f'The {attr} attribute must have a value',
                    **error_kwargs
                )

                self._assertEqual(
                    a,
                    'urn:oasis:names:tc:SAML:2.0:protocol',
                    f'The {attr} attribute must be '
                    'urn:oasis:names:tc:SAML:2.0:protocol',
                    **error_kwargs
                )

            if attr == 'WantAssertionsSigned':
                a = spsso[0].get(attr)
                self._assertIsNotNone(
                    a,
                    f'The {attr} attribute must have a value',
                    **error_kwargs
                )

                if a:
                    self._assertEqual(
                        a.lower(),
                        'true',
                        f'The {attr} attribute must be true',
                        **error_kwargs
                    )
        return self.is_ok(
            f'{self.__class__.__name__}.test_SPSSODescriptor_extra'
        )

    def test_AttributeConsumingService_extra(self):
        acss = self.doc.xpath('//EntityDescriptor/SPSSODescriptor'
                              '/AssertionConsumerService')

        desc = [ent.attrib for ent in acss if acss]
        error_kwargs = dict(description = desc) if desc else {}

        for acs in acss:
            ras = acs.xpath('./RequestedAttribute')
            for ra in ras:
                a = ra.get('NameFormat')
                if a is not None:
                    self._assertIn(
                        a,
                        constants.ALLOWED_FORMATS,
                        (('The NameFormat attribute '
                          'in RequestedAttribute element '
                          'must be one of [%s]') %
                         (', '.join(constants.ALLOWED_FORMATS))),
                         **error_kwargs
                    )
        return self.is_ok(
            f'{self.__class__.__name__}.test_AttributeConsumingService_extra'
        )

    def test_Organization_extra(self):
        orgs = self.doc.xpath('//EntityDescriptor/Organization')
        self._assertTrue((len(orgs) == 1), 'An Organization must be present')

        desc = [ent.attrib for ent in orgs if orgs]
        error_kwargs = dict(description = desc) if desc else {}

        if orgs:
            org = orgs[0]
            for elem in ['Name', 'URL', 'DisplayName']:
                e = org.xpath(
                    './Organization%s[@xml:lang="it"]' % elem,
                    namespaces={
                        'xml': 'http://www.w3.org/XML/1998/namespace',
                    }
                )
                self._assertTrue(
                    (len(e) == 1),
                    f'An IT localised Organization {elem} must be present',
                    **error_kwargs
                )
            return self.is_ok(
                f'{self.__class__.__name__}.test_Organization'
            )

    def test_all(self):
        self.test_Signature_extra()
        self.test_AttributeConsumingService_extra()
        self.test_SPSSODescriptor_extra()
        self.test_Organization_extra()
