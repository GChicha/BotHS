import datetime
import glob
import logging
import os
from typing import Dict, Generic, List, Literal, NewType, Optional, Tuple, TypeVar, TypedDict, Union

import requests
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater
from telegram.files.location import Location
from telegram.files.venue import Venue
from telegram.parsemode import ParseMode

logger = logging.getLogger()

TOKEN = os.environ["TOKEN"]
URL_HLEDGER = os.environ["URL_HLEDGER"]

HLedgerCommoditySymbol = NewType("HLedgerCommoditySymbol", str)
HLedgerAccountName = NewType("HLedgerAccountName", str)
HLedgerTag = NewType("HLedgerTag", Tuple[str, str])
HLedgerFormatedDate = NewType("HLedgerFormatedDate", str)


def to_hledger_date(date: datetime.datetime) -> HLedgerFormatedDate:
    return HLedgerFormatedDate(date.strftime("%Y-%m-%d"))


BRL = HLedgerCommoditySymbol("BRL")
KaristonAccount = HLedgerAccountName("KaristonAccount")


class AmountPrecision(TypedDict):
    tag: Union[Literal["NaturalPrecision"]]
    contents: Tuple


def build_amount_precision() -> AmountPrecision:
    return AmountPrecision(
        contents=(),
        tag="NaturalPrecision"
    )


class HLedgerAmountStyle(TypedDict):
    ascommodityside: Union[Literal["L", "R"]]
    ascommodityspaced: bool
    asprecision: AmountPrecision
    asdecimalpoint: None
    asdigitgroups: Tuple[str, List[int]]


def build_amount_style() -> HLedgerAmountStyle:
    return HLedgerAmountStyle(
        ascommodityside="L",
        ascommodityspaced=True,
        asprecision=build_amount_precision(),
        asdecimalpoint=None,
        asdigitgroups=(",", [3])
    )


class HLedgerQuantity(TypedDict):
    floatingPoint: float
    decimalPlaces: int
    decimalMantissa: int


def to_hledger_quantity(value: float) -> HLedgerQuantity:
    return HLedgerQuantity(
        floatingPoint=value,
        decimalMantissa=int(value * 100),
        decimalPlaces=2
    )


class HLedgerAmount(TypedDict):
    acommodity: HLedgerCommoditySymbol
    aquantity: HLedgerQuantity
    aismultiplier: bool
    astyle: HLedgerAmountStyle
    aprice: None


def build_amount(quantity: float) -> HLedgerAmount:
    return HLedgerAmount(
        acommodity=BRL,
        aquantity=to_hledger_quantity(quantity),
        aismultiplier=False,
        astyle=build_amount_style(),
        aprice=None,
    )


class HLedgerTPosting(TypedDict):
    pdate: Optional[HLedgerFormatedDate]
    pdate2: Optional[HLedgerFormatedDate]
    pstatus: Union[
        Literal[
            "Unmarked",
            "Pending",
            "Cleared"
        ]
    ]
    paccount: HLedgerAccountName
    pamount: List[HLedgerAmount]
    pcomment: str
    ptype: Union[
        Literal[
            "RegularPosting",
            "VirtualPosting",
            "BalancedVirtualPosting"
        ]
    ]
    ptags: List[HLedgerTag]
    pbalanceassertion: None
    ptransaction: None
    poriginal: None


def build_posting(account: HLedgerAccountName, quantity: float) -> HLedgerTPosting:
    return HLedgerTPosting(
        pdate=None,
        pdate2=None,
        pstatus="Unmarked",
        paccount=account,
        pamount=[build_amount(quantity)],
        pcomment="",
        ptype="RegularPosting",
        ptags=[],
        pbalanceassertion=None,
        ptransaction=None,
        poriginal=None,
    )


class HLedgerJournalSourcePos(TypedDict):
    contents: Tuple[str, Tuple[int, int]]
    tag: Literal["JournalSourcePos"]


def build_source_pos() -> HLedgerJournalSourcePos:
    return HLedgerJournalSourcePos(
        contents=("", (1, 1)),
        tag="JournalSourcePos"
    )


class HLedgerTransaction(TypedDict):
    tindex: int
    tprecedingcomment: str
    tsourcepos: HLedgerJournalSourcePos
    tdate: HLedgerFormatedDate
    tdate2: None
    tstatus: Union[
        Literal["Unmarked"],
        Literal["Pending"],
        Literal["Cleared"]
    ]
    tcode: str
    tdescription: str
    tcomment: str
    ttags: List[HLedgerTag]
    tpostings: List[HLedgerTPosting]


def build_transaction(
    description: str,
    tags: Dict[str, str],
    account_a: HLedgerAccountName,
    account_b: HLedgerAccountName,
    value: float
) -> HLedgerTransaction:
    return HLedgerTransaction(
        tindex=0,
        tprecedingcomment="",
        tsourcepos=build_source_pos(),
        tdate=to_hledger_date(datetime.datetime.utcnow()),
        tdate2=None,
        tstatus="Unmarked",
        tcode="",
        tdescription=description,
        tcomment="",
        ttags=[HLedgerTag((tag, value)) for tag, value in tags.items()],
        tpostings=[
            build_posting(account_a, -value),
            build_posting(account_b, value),
        ],
    )


def add_new_donation(update: Update, context: CallbackContext):
    if update.effective_user:
        donation_transaction: HLedgerTransaction = build_transaction(
            account_b=KaristonAccount,
            account_a=HLedgerAccountName(
                f"member::{update.effective_user.first_name}_{update.effective_user.last_name}"
            ),
            tags={
                "type": "donation",
                "member": update.effective_user.full_name
            },
            description=f"Donation from {update.effective_user.full_name}",
            value=10
        )
        response = requests.put(
            f"{URL_HLEDGER}/add", json=donation_transaction
        )
        response.raise_for_status()


# COMANDOS ESTATICOS:
def localizacao(update: Update, context: CallbackContext):
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_venue(
            reply_to_message_id=update.effective_message.message_id,
            venue=Venue(
                title="Hackerspace Maringá",
                address="R. Vitória, 943 - Vila Esperanca, Maringá - PR",
                google_place_id="ChIJr9L4qzLR7JQRWi8Anh8JyCI",
                google_place_type="zoo",
                location=Location(latitude=-23.402309060129333,
                                  longitude=-51.93850697016083)))


def regras(update: Update, context: CallbackContext):
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_message(
            reply_to_message_id=update.effective_message.message_id,
            text=open("static_messages/rules.md").read(),
            parse_mode=ParseMode.MARKDOWN_V2)


def help(update: Update, context: CallbackContext):
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_message(
            reply_to_message_id=update.effective_message.message_id,
            text=open("static_messages/rules.md").read(),
            parse_mode=ParseMode.MARKDOWN_V2)


# COMANDOS DINAMICOS:
def newsletter(update: Update, context: CallbackContext):
    newest_file = max(glob.iglob('./news/*.pdf'), key=os.path.getctime)
    if update.effective_chat and update.effective_message:
        update.effective_chat.send_document(
            open(newest_file, "rb"),
            reply_to_message_id=update.effective_message.message_id,
            filename="newsletter_hs_maringa.pdf",
            caption="Newsletter Hackerspace Maringá")


def finance_summary(update: Update, context: CallbackContext):
    requests.get("http://localhost:5000/accounts/")


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    # COMANDOS ESTATICOS
    dispatcher.add_handler(CommandHandler('address', localizacao))
    dispatcher.add_handler(CommandHandler('rules', regras))
    dispatcher.add_handler(CommandHandler('help', help))

    # COMANDOS DINAMICOS
    dispatcher.add_handler(CommandHandler('news', newsletter))

    # COMANDOS FINANCEIROS
    dispatcher.add_handler(CommandHandler('donation', add_new_donation))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
