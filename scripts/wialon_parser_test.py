import binascii
from translator.parser.wialon import Wialon


if __name__ == '__main__':
    parser = Wialon()

    # test data
    data = [
        '333533393736303133343435343835004B0BFB70000000030BBB000000270102706F73696E666F00A027AFDF5D9848403AC7253383DD4B400000000000805A40003601460B0BBB0000001200047077725F657874002B8716D9CE973B400BBB00000011010361766C5F696E707574730000000001',
        '73686d6900552d3f49000000070bbb000000270102706f73696e666f001f090e42538d3b40af8c20a82dfc4a400000000000000000006c0109ff0bbb0000000f000461646331000000000000ca21400bbb00000011010361766c5f696e7075747300000000240bbb00000012010361766c5f6f7574707574730000000037',
        '74000000333533393736303133343435343835004B0BFB70000000030BBB000000270102706F73696E666F00A027AFDF5D9848403AC7253383DD4B400000000000805A40003601460B0BBB0000001200047077725F657874002B8716D9CE973B400BBB00000011010361766C5F696E707574730000000001',
    ]

    for i in range(len(data)):
        print('\nParse packet: %s\n' % data[i])
        print(parser.parse_packet(binascii.unhexlify(data[i])))
