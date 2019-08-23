from avito import Avito
from avito.storage import SimpleStorage


if __name__ == '__main__':
    st = SimpleStorage()
    Avito('balakovo', 'kvartiry', pages=1, storage=st).run()
    print(st)