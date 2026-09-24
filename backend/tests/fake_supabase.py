"""
테스트용 가짜 Supabase 클라이언트.

실제 DB 없이 API 로직(분기, 상태 전이, 동시성 처리)을 검증하기 위해
supabase-py 의 쿼리 빌더 중 이 프로젝트가 쓰는 메서드만 메모리 위에서 흉내 낸다.
"""
import copy
from types import SimpleNamespace


class FakeQuery:
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.filters = []
        self.op = "select"
        self.payload = None
        self._limit = None
        self._order = None
        self.not_ = self  # .not_.is_(col, "null") 지원

    # ---- 동작 지정 ----
    def select(self, *_args, **_kwargs):
        self.op = "select"
        return self

    def insert(self, payload):
        self.op, self.payload = "insert", payload
        return self

    def update(self, payload):
        self.op, self.payload = "update", payload
        return self

    def delete(self):
        self.op = "delete"
        return self

    # ---- 필터 ----
    def eq(self, col, val):
        self.filters.append(lambda r: str(r.get(col)) == str(val))
        return self

    def neq(self, col, val):
        self.filters.append(lambda r: str(r.get(col)) != str(val))
        return self

    def in_(self, col, vals):
        vals = {str(v) for v in vals}
        self.filters.append(lambda r: str(r.get(col)) in vals)
        return self

    def is_(self, col, _null):
        self.filters.append(lambda r: r.get(col) is not None)  # not_.is_(col, null) 용도로만 사용
        return self

    def or_(self, expr):
        conds = [c.split(".eq.") for c in expr.split(",")]
        self.filters.append(lambda r: any(str(r.get(c)) == v for c, v in conds))
        return self

    def order(self, col, desc=False):
        self._order = (col, desc)
        return self

    def limit(self, n):
        self._limit = n
        return self

    def single(self):
        return self

    # ---- 실행 ----
    def _match(self):
        return [r for r in self.db.tables.setdefault(self.table, []) if all(f(r) for f in self.filters)]

    def execute(self):
        rows = self.db.tables.setdefault(self.table, [])
        self.db.calls.append((self.table, self.op))

        if self.op == "insert":
            hook = self.db.insert_hooks.get(self.table)
            if hook:
                hook(self.payload)
            new = copy.deepcopy(self.payload)
            rows.append(new)
            return SimpleNamespace(data=[new], count=None)

        matched = self._match()
        if self.op == "update":
            for r in matched:
                r.update(self.payload)
            return SimpleNamespace(data=copy.deepcopy(matched), count=None)
        if self.op == "delete":
            self.db.tables[self.table] = [r for r in rows if r not in matched]
            return SimpleNamespace(data=matched, count=None)

        if self._order:
            col, desc = self._order
            matched = sorted(matched, key=lambda r: r.get(col) or "", reverse=desc)
        if self._limit is not None:
            matched = matched[: self._limit]
        return SimpleNamespace(data=copy.deepcopy(matched), count=len(matched))


class FakeSupabase:
    def __init__(self, tables=None, rpc_results=None):
        self.tables = tables or {}
        self.rpc_results = rpc_results or {}
        self.rpc_calls = []
        self.calls = []
        self.insert_hooks = {}

    def table(self, name):
        return FakeQuery(self, name)

    def rpc(self, name, params):
        self.rpc_calls.append((name, params))
        result = self.rpc_results.get(name, [])
        data = result(params) if callable(result) else result
        return SimpleNamespace(execute=lambda: SimpleNamespace(data=copy.deepcopy(data)))


def wkt_point(lon, lat):
    return f"POINT({lon} {lat})"


def vec_str(values):
    return "[" + ",".join(str(v) for v in values) + "]"


