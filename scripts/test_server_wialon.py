import binascii
import argparse
import asyncio


async def tcp_client(host, port, package):
    reader, writer = await asyncio.open_connection(host, port)

    writer.write(package)

    data = await reader.read(1024)
    confirm_byte = int.from_bytes(data, byteorder='little')
    response_txt = "Is OK" if confirm_byte == 17 else "Is bad response"
    print(f'Received: {hex(confirm_byte)}. {response_txt}')

    print('Close the connection')
    writer.close()
    # await writer.wait_closed()


if __name__ == '__main__':
    packages = [
        '74000000333533393736303133343435343835004B0BFB70000000030BBB000000270102706F73696E666F00A027AFDF5D9848403AC7253383DD4B400000000000805A40003601460B0BBB0000001200047077725F657874002B8716D9CE973B400BBB00000011010361766C5F696E707574730000000001',
        '7e00000073686d6900552d3f49000000070bbb000000270102706f73696e666f001f090e42538d3b40af8c20a82dfc4a400000000000000000006c0109ff0bbb0000000f000461646331000000000000ca21400bbb00000011010361766c5f696e7075747300000000240bbb00000012010361766c5f6f7574707574730000000037'
    ]

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-t', '--host', default='127.0.0.1', help='IP address wialon parser')
    args_parser.add_argument('-p', '--port', required=True, help='Port wialon parser')

    args = args_parser.parse_args()

    loop = asyncio.get_event_loop()

    tasks = []
    for package in packages:
        print(f"Send to {args.host}:{args.port} Wialon dataframe: {package}")
        tasks.append(loop.create_task(tcp_client(args.host, args.port, binascii.unhexlify(package))))

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
