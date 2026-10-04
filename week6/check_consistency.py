"""Model-code consistency check (Stage 3 Part H; reused in Stage 4).

Compares the Python module against the machine-readable UML and prints a
UML-element -> Python-element trace.  Exit status 1 if anything is missing.
Usage:  python check_consistency.py            (checks skeletons.py)
"""
import importlib
import inspect
import sys
from datetime import date, datetime


def _sample_objects(mod):
    p = mod.Patient("P001", "Aisha Rahman", date(1990, 4, 12), "0412 345 678")
    d = mod.Practitioner("D01", "Dr Mei Tanaka", "General Practice")
    a = mod.Appointment("A0001", p, d, datetime(2026, 10, 5, 9, 0))
    return {"Patient": p, "Practitioner": d, "Appointment": a, "Clinic": mod.Clinic()}


def check(mod, uml) -> list[tuple[str, str, bool]]:
    rows = []
    objs = _sample_objects(mod)
    for cls_name, spec in uml.items():
        cls = getattr(mod, cls_name, None)
        rows.append((f"class {cls_name}", cls_name, cls is not None))
        if cls is None:
            continue
        for m in spec.get("members", []):
            rows.append((f"{cls_name}.{m}", f"{cls_name}.{m}", hasattr(cls, m)))
        if spec.get("exception"):
            rows.append((f"{cls_name} is an Exception", cls_name,
                         issubclass(cls, Exception)))
        obj = objs.get(cls_name)
        for attr in spec.get("attributes", []):
            rows.append((f"{cls_name}.{attr} (attribute)", f"{cls_name}.{attr}",
                         obj is not None and (hasattr(type(obj), attr) or attr in vars(obj))))
        for op, params in spec.get("operations", {}).items():
            fn = getattr(cls, op, None)
            ok = callable(fn) and list(inspect.signature(fn).parameters)[1:] == params
            rows.append((f"{cls_name}.{op}({', '.join(params)})", f"def {op}", ok))
    return rows


def report(rows) -> bool:
    width = max(len(r[0]) for r in rows)
    for uml, py, ok in rows:
        print(f"{uml:<{width}}  ->  {py:<34} {'OK' if ok else 'MISSING'}")
    passed = sum(ok for *_, ok in rows)
    print(f"\n{passed}/{len(rows)} UML elements present in code")
    return passed == len(rows)


if __name__ == "__main__":
    import skeletons
    from uml_spec import UML_V03
    sys.exit(0 if report(check(skeletons, UML_V03)) else 1)
