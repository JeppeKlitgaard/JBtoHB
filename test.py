from jbtohb import (get_fileobject_jb, get_fileobject_hb,
                    list_of_transactions_from_file,
                    list_of_transactions_to_file)
import sys

if __name__ == '__main__':
    with get_fileobject_jb(sys.argv[1]) as f:
        transactions = list_of_transactions_from_file(f)

    for t in transactions:
        print(t.to_hb_csv_row())

    out_name = "processed_" + sys.argv[1]
    with get_fileobject_hb(out_name) as f:
        list_of_transactions_to_file(f, transactions)
