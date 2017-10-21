"""
Utility for converting a JyskeBank CSV file to fit
the HomeBank-style CSV format.

For example use see test.py
"""
import csv
import locale
from datetime import date

# To parse comma decimal points:
locale.setlocale(locale.LC_NUMERIC, "en_DK.UTF-8")

JBCSV_ENCODING = "ISO-8859-1"  # Found with chardet3


class Transaction(object):
    """Represents a financial transaction."""
    def __init__(self, date_, text, amount, balance, comment, checked,
                 jb_flag, account, category, subcategory):
        self.date = date_
        self.text = text
        self.amount = amount
        self.balance = balance
        self.comment = comment
        self.checked = checked
        self.jb_flag = jb_flag
        self.account = account
        self.category = category
        self.subcategory = subcategory

    @classmethod
    def from_jb_csv_line(cls, csvline):
        """
        Constructs a Transaction object from a JyskeBank style CSV file.

        Example JyskeBank CSV file:
        "Dato";"";"Tekst";"";"Beløb";"Saldo";"Kommentar";"Afstemt";"Flag";"Konto";"";"Kategori";"Underkategori"
        "19.10.2017";"";"VD CAFE STEDET";"";"-75,00";"3.997,34";"";"nej";"nej";"Jeppe - Visa Electron";"";"Fritid";"Café, restaurant og bar"
        """

        # BEGIN FIELDS
        # Field 1 --- DATO
        raw_date = csvline.pop(0)
        raw_date = raw_date.split(".")
        raw_date = [int(x) for x in raw_date]
        raw_date.reverse()

        date_ = date(*raw_date)

        # Field 2 --- SKIP
        csvline.pop(0)  # Skip empty field

        # Field 3 --- TEKST
        text = csvline.pop(0).strip()

        # Field 4 --- SKIP
        csvline.pop(0)  # Skip empty field

        # Field 5 --- BELØB
        amount = locale.atof(csvline.pop(0))

        # Field 6 --- SALDO
        balance = locale.atof(csvline.pop(0))

        # Field 7 --- KOMMENTAR
        comment = csvline.pop(0).strip()

        # Field 8 --- AFSTEMT
        checked_raw = csvline.pop(0)
        if checked_raw == "nej":
            checked = False
        elif checked_raw == "ja":
            checked = True
        else:
            raise ValueError("CHECKED flag not 'nej' or 'ja'.")

        # Field 9 --- FLAG
        jb_flag_raw = csvline.pop(0)
        if jb_flag_raw == "nej":
            jb_flag = False
        elif jb_flag_raw == "ja":
            jb_flag = True
        else:
            raise ValueError("FLAG flag not 'nej' or 'ja'.")

        # Field 10 --- KONTO
        account = csvline.pop(0)

        # Field 11 --- SKIP
        csvline.pop(0)  # Skip empty field

        # Field 12 --- KATEGORI
        category = csvline.pop(0)

        # Field 13 --- Underkategori
        subcategory = csvline.pop(0)

        # END FIELDS
        if csvline:
            raise IndexError("More fields than expected in csvline")

        # print(date_, text, amount, balance, comment, checked,
        #       jb_flag, account, category, subcategory)
        return cls(date_, text, amount, balance, comment, checked,
                   jb_flag, account, category, subcategory)

    def to_hb_csv_row(self):
        """
        Returns a row for a csv-writer in the HomeBank format.
        """
        row = []

        # BEGIN FIELDS
        # Field 1 - DATE
        date_ = self.date.strftime("%d-%m-%y")
        row.append(date_)

        # Field 2 - PAYMENT (type)
        row.append(0)  # Not relevant/Data not available from JB

        # Field 3 - INFO
        row.append("")  # Not relevant/Data not available from JB

        # Field 4 - PAYEE
        row.append(self.text)

        # Field 5 - MEMO
        row.append(self.comment)

        # Field 6 - AMOUNT
        row.append(self.amount)

        # Field 7 - Category
        category = self.category
        if self.subcategory != "Ingen kategori":
            category = category + ":" + self.subcategory

        row.append(category)

        # Field 8 - Tags
        tags = []
        if self.checked:
            tags.append("Afstemt")
        else:
            tags.append("Uafstemt")

        row.append(" ".join(tags))

        return row


def get_fileobject_jb(path):
    """
    Returns a fileobject from path using the proper encoding.
    """
    return open(path, newline="", encoding=JBCSV_ENCODING)


def get_fileobject_hb(path):
    return open(path, "w", newline="")


def list_of_transactions_from_file(fileobject, header=True):
    """
    Returns a list of Transaction objects from
    JyskeBank-formatted CSV fileobject.

    If 'header' is True the first row is skipped
    """
    transactions = []

    if header:
        next(fileobject)

    with fileobject as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            transactions.append(Transaction.from_jb_csv_line(row))

    return transactions


def list_of_transactions_to_file(fileobject, transactions):
    """
    Writes a list of Transaction objects to fileobject
    as a HomeBank-formatted CSV file.
    """
    with fileobject as f:
        writer = csv.writer(f, delimiter=";")

        for transaction in transactions:
            writer.writerow(transaction.to_hb_csv_row())
