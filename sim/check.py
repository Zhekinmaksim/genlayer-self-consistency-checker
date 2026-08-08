import importlib.util
import hashlib
import pathlib
import sys
import types


class UserError(Exception):
    pass


class Address(str):
    def __new__(cls, value):
        return str.__new__(cls, value)


Address.ZERO = Address("0x0000000000000000000000000000000000000000")


class TreeMap(dict):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


class DynArray(list):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


class Keccak256:
    def __init__(self):
        self._h = hashlib.sha3_256()

    def update(self, data):
        self._h.update(data)

    def hexdigest(self):
        return self._h.hexdigest()


class Event:
    def emit(self):
        return None


def allow_storage(cls):
    return cls


class Public:
    def write(self, fn):
        return fn

    def view(self, fn):
        return fn


class Nondet:
    responses = []
    fail_next = False

    @classmethod
    def exec_prompt(cls, _prompt, **_kwargs):
        if cls.fail_next:
            cls.fail_next = False
            raise RuntimeError("provider down")
        if not cls.responses:
            raise RuntimeError("no response")
        return cls.responses.pop(0)


class EqPrinciple:
    @staticmethod
    def prompt_comparative(fn, _principle):
        return fn()


message = types.SimpleNamespace(sender_address=Address("0xaaa"))
gl = types.SimpleNamespace(
    Contract=object,
    Event=Event,
    public=Public(),
    vm=types.SimpleNamespace(UserError=UserError),
    message=message,
    nondet=Nondet,
    eq_principle=EqPrinciple(),
)

genlayer = types.ModuleType("genlayer")
for name, value in {
    "Address": Address,
    "TreeMap": TreeMap,
    "DynArray": DynArray,
    "Keccak256": Keccak256,
    "allow_storage": allow_storage,
    "u32": int,
    "gl": gl,
}.items():
    setattr(genlayer, name, value)
sys.modules["genlayer"] = genlayer

root = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contract", root / "contract.py")
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


def fresh():
    checker = contract.SelfConsistencyChecker()
    checker.checks = TreeMap()
    checker.ids = DynArray()
    Nondet.responses = []
    Nondet.fail_next = False
    message.sender_address = Address("0xaaa")
    return checker


def must_raise(fn, code):
    try:
        fn()
    except UserError as exc:
        assert str(exc) == code, f"expected {code}, got {exc}"
        return
    raise AssertionError(f"expected {code}")


def pin(checker, cid="case", axes="payment timing\ntermination rights", doc="ok"):
    axes_hash = checker.open_check(cid, axes)
    digest = contract._digest(doc)
    checker.submit_document(cid, doc, digest)
    return axes_hash, digest


def case_1_contradiction_found():
    checker = fresh()
    pin(checker, doc="Payment is due in 30 days.\nPayment is due immediately.")
    Nondet.responses.append(
        {"axes": [{"i": 1, "conflict": True, "a": "30 days", "b": "immediately"}, {"i": 2, "conflict": False, "a": "", "b": ""}]}
    )
    assert checker.evaluate("case") == "INCONSISTENT"
    assert checker.conflict_mask("case") == 1
    assert checker.conflicting_axes("case") == ["payment timing"]


def case_2_clean_document():
    checker = fresh()
    pin(checker, axes="scope\nbudget", doc="Scope is fixed. Budget is capped.")
    Nondet.responses.append(
        {"axes": [{"i": 1, "conflict": False, "a": "", "b": ""}, {"i": 2, "conflict": False, "a": "", "b": ""}]}
    )
    assert checker.evaluate("case") == "CONSISTENT"
    assert checker.conflict_mask("case") == 0


def case_3_malformed_judgment():
    checker = fresh()
    pin(checker)
    Nondet.responses.append({"axes": [{"i": 1, "conflict": False, "a": "", "b": ""}]})
    assert checker.evaluate("case") == "UNDETERMINED"
    assert checker.reason_of("case") == "MALFORMED_JUDGMENT"


def case_4_provider_failure():
    checker = fresh()
    pin(checker)
    Nondet.fail_next = True
    assert checker.evaluate("case") == "UNDETERMINED"
    assert checker.reason_of("case") == "JUDGMENT_UNAVAILABLE"


def case_5_input_guards():
    checker = fresh()
    must_raise(lambda: checker.open_check("blank", " \n\t "), "EMPTY_AXIS_SET")
    must_raise(lambda: checker.open_check("dup", "scope\nSCOPE"), "DUPLICATE_AXIS")
    must_raise(lambda: checker.open_check("many", "\n".join(str(i) for i in range(13))), "TOO_MANY_AXES")
    checker.open_check("same", "scope")
    must_raise(lambda: checker.open_check("same", "scope"), "ID_ALREADY_USED")
    must_raise(lambda: checker.submit_document("same", "doc", "0x00"), "HASH_MISMATCH")
    must_raise(lambda: checker.status_of("missing"), "UNKNOWN_CHECK")


def case_6_one_shot_and_terminal():
    checker = fresh()
    pin(checker, axes="scope", doc="Scope is fixed.")
    must_raise(lambda: checker.submit_document("case", "new", contract._digest("new")), "DOCUMENT_ALREADY_PINNED")
    Nondet.responses.append({"axes": [{"i": 1, "conflict": False, "a": "", "b": ""}]})
    assert checker.evaluate("case") == "CONSISTENT"
    must_raise(lambda: checker.evaluate("case"), "NOT_PINNED_OR_ALREADY_EVALUATED")


def case_7_author_only_submission():
    checker = fresh()
    checker.open_check("case", "scope")
    message.sender_address = Address("0xbbb")
    must_raise(lambda: checker.submit_document("case", "doc", contract._digest("doc")), "NOT_AUTHOR")


cases = [
    case_1_contradiction_found,
    case_2_clean_document,
    case_3_malformed_judgment,
    case_4_provider_failure,
    case_5_input_guards,
    case_6_one_shot_and_terminal,
    case_7_author_only_submission,
]

for case in cases:
    case()
    print(f"PASS {case.__name__}")

print(f"{len(cases)}/{len(cases)} pass")
