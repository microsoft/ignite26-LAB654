"""The eight read-only tools, with names, descriptions and input schemas copied from github/github-mcp-server.

Result shapes follow the live server: Minimal* types for get_me, list_pull_requests, pull_request_read and
search_repositories/search_users, raw GitHub search JSON for search_pull_requests, and the GraphQL-derived maps
for list_label/get_label. Fields the seed has no data for (diffs, files, commits, SHAs, check runs) are omitted
rather than invented, the way the live server omits empty omitempty fields.
"""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any

from mockmcp import CallContext, Tool, ToolError

from .store import Store, base_url

SCHEMAS_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "tool_schemas.json"
HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")
API = "https://api.github.com"
UNSEEDED_METHODS = ("get_diff", "get_status", "get_files", "get_commits", "get_check_runs")


def load_schemas() -> dict[str, dict]:
    return {t["name"]: t for t in json.loads(SCHEMAS_PATH.read_text(encoding="utf-8"))}


class GitHubError(ToolError):
    """Rendered as the plain error text the live server returns."""


def not_found(action: str, path: str) -> GitHubError:
    return GitHubError(f"{action}: GET {API}{path}: 404 Not Found []")


# --- shaping -------------------------------------------------------------------------------------------------------

def repo_url(repo: dict) -> str:
    return f"{base_url()}/{repo['owner']}/{repo['name']}"


def pull_url(repo: dict, pr: dict) -> str:
    return f"{repo_url(repo)}/pull/{pr['number']}"


def avatar(login: str) -> str:
    return f"{base_url()}/avatars/{login}.svg"


def minimal_user(store: Store, login: str) -> dict:
    u = store.user(login) or {"login": login, "id": 0}
    return {"login": u["login"], "id": u["id"], "profile_url": f"{base_url()}/{u['login']}",
            "avatar_url": avatar(u["login"])}


def raw_user(store: Store, login: str) -> dict:
    u = store.user(login) or {"login": login, "id": 0}
    return {"login": u["login"], "id": u["id"], "avatar_url": avatar(u["login"]),
            "html_url": f"{base_url()}/{u['login']}", "type": "User", "site_admin": False}


def label_obj(repo: dict, name: str) -> dict:
    return next((x for x in repo["labels"] if x["name"] == name), {"id": "", "name": name, "color": "ededed",
                                                                    "description": ""})


def repo_open_count(repo: dict) -> int:
    return sum(1 for p in repo["pulls"] if p["state"] == "open")


def repo_updated(repo: dict) -> str:
    return max(p["updated_at"] for p in repo["pulls"])


def minimal_repo(repo: dict) -> dict:
    out = {"id": repo["id"], "name": repo["name"], "full_name": f"{repo['owner']}/{repo['name']}",
           "description": repo["description"], "html_url": repo_url(repo), "stargazers_count": 0,
           "forks_count": 0, "open_issues_count": repo_open_count(repo), "updated_at": repo_updated(repo),
           "private": repo["private"], "fork": False, "archived": False, "default_branch": repo["default_branch"]}
    return out


def minimal_pr(store: Store, repo: dict, pr: dict) -> dict:
    out: dict[str, Any] = {
        "number": pr["number"], "title": pr["title"], "body": pr["body"], "state": pr["state"],
        "draft": pr["draft"], "merged": pr["merged"], "html_url": pull_url(repo, pr),
        "user": minimal_user(store, pr["user"]), "labels": list(pr["labels"]), "assignees": list(pr["assignees"]),
        "created_at": pr["created_at"], "updated_at": pr["updated_at"],
    }
    if pr.get("closed_at"):
        out["closed_at"] = pr["closed_at"]
    if pr.get("merged_at"):
        out["merged_at"] = pr["merged_at"]
    if pr.get("merged_by"):
        out["merged_by"] = pr["merged_by"]
    if pr.get("milestone"):
        out["milestone"] = pr["milestone"]
    return out


def search_item(store: Store, repo: dict, pr: dict) -> dict:
    """An issue-shaped item, as returned by GitHub's /search/issues for a pull request."""
    url = pull_url(repo, pr)
    milestone = None
    if pr.get("milestone"):
        milestone = {"title": pr["milestone"], "state": "open"}
    return {
        "id": repo["id"] * 1000 + pr["number"], "number": pr["number"], "title": pr["title"], "body": pr["body"],
        "state": pr["state"], "locked": False, "draft": pr["draft"], "html_url": url,
        "repository_url": repo_url(repo), "user": raw_user(store, pr["user"]),
        "labels": [{k: label_obj(repo, n)[k] for k in ("id", "name", "color", "description")} | {
            "default": n in ("bug", "enhancement")} for n in pr["labels"]],
        "assignee": raw_user(store, pr["assignees"][0]) if pr["assignees"] else None,
        "assignees": [raw_user(store, a) for a in pr["assignees"]], "milestone": milestone, "comments": 0,
        "created_at": pr["created_at"], "updated_at": pr["updated_at"], "closed_at": pr.get("closed_at"),
        "author_association": "MEMBER",
        "pull_request": {"url": url, "html_url": url, "merged_at": pr.get("merged_at")},
    }


def review_obj(store: Store, repo: dict, pr: dict, r: dict) -> dict:
    return {"id": r["id"], "state": r["state"], "body": r["body"],
            "html_url": f"{pull_url(repo, pr)}#pullrequestreview-{r['id']}", "user": minimal_user(store, r["user"]),
            "submitted_at": r["submitted_at"], "author_association": "MEMBER"}


def pick(obj: dict, fields: list[str] | None) -> dict:
    return {k: obj[k] for k in fields if k in obj} if fields else obj


def paginate(items: list, args: dict, default: int = 30) -> list:
    page = max(int(args.get("page") or 1), 1)
    per = min(max(int(args.get("perPage") or default), 1), 100)
    return items[(page - 1) * per: page * per]


def sort_desc(items: list[dict], key: str, order: str | None) -> list[dict]:
    return sorted(items, key=lambda x: (x.get(key) or ""), reverse=(order or "desc") != "asc")


# --- search parsing ------------------------------------------------------------------------------------------------

def tokens(query: str) -> list[str]:
    try:
        return shlex.split(query)
    except ValueError:
        return query.split()


def parse(query: str) -> tuple[dict[str, list[str]], list[str]]:
    quals: dict[str, list[str]] = {}
    words: list[str] = []
    for tok in tokens(query):
        neg = tok.startswith("-")
        key, sep, val = tok.lstrip("-").partition(":")
        if sep and val and (key.isalpha() or key in ("reviewed-by", "review-requested")):
            quals.setdefault(("-" if neg else "") + key.lower(), []).append(val.strip('"'))
        else:
            words.append(tok.strip('"'))
    return quals, [w for w in words if w and w.upper() not in ("AND", "OR")]


def _has_user(store: Store, value: str, login: str) -> bool:
    if value == "@me":
        value = store.me["login"]
    return value.lower() == login.lower()


def pr_matches(store: Store, repo: dict, pr: dict, quals: dict[str, list[str]], words: list[str]) -> bool:
    full = f"{repo['owner']}/{repo['name']}".lower()
    reviewers = [r["user"] for r in pr["reviews"]]
    people = {pr["user"], *pr["assignees"], *reviewers}

    def test(key: str, val: str) -> bool:
        v = val.lower()
        if key == "is":
            return {"pr": True, "pull-request": True, "issue": False, "open": pr["state"] == "open",
                    "closed": pr["state"] == "closed", "merged": pr["merged"],
                    "unmerged": not pr["merged"], "draft": pr["draft"], "public": not repo["private"],
                    "private": repo["private"]}.get(v, True)
        if key == "type":
            return v in ("pr", "pull-request")
        if key == "state":
            return pr["state"] == v
        if key == "repo":
            return v == full
        if key in ("org", "user", "owner"):
            return v == repo["owner"].lower()
        if key == "author":
            return _has_user(store, val, pr["user"])
        if key == "assignee":
            return any(_has_user(store, val, a) for a in pr["assignees"])
        if key in ("reviewed-by", "commenter"):
            return any(_has_user(store, val, r) for r in reviewers)
        if key in ("involves", "mentions"):
            return any(_has_user(store, val, p) for p in people)
        if key == "label":
            have = {x.lower() for x in pr["labels"]}
            return any(part.strip().lower() in have for part in val.split(","))
        if key == "milestone":
            return (pr.get("milestone") or "").lower() == v
        if key == "review":
            states = [r["state"] for r in pr["reviews"]]
            return {"approved": "APPROVED" in states, "changes_requested": "CHANGES_REQUESTED" in states,
                    "none": not states, "required": False}.get(v, True)
        if key == "no":
            return {"label": not pr["labels"], "milestone": not pr.get("milestone"),
                    "assignee": not pr["assignees"]}.get(v, True)
        return True  # Unsupported qualifiers don't narrow the mock's results.

    for key, vals in quals.items():
        neg = key.startswith("-")
        name = key.lstrip("-")
        if name == "in":
            continue
        for val in vals:
            if test(name, val) == neg:
                return False

    if words:
        scopes = {s.lower() for v in quals.get("in", []) for s in v.split(",")} or {"title", "body", "comments"}
        hay = []
        if "title" in scopes:
            hay.append(pr["title"])
        if "body" in scopes:
            hay.append(pr["body"] or "")
        if "comments" in scopes:
            hay += [r["body"] for r in pr["reviews"]]
        text = "\n".join(hay).lower()
        if not all(w.lower() in text for w in words):
            return False
    return True


# --- tool base -----------------------------------------------------------------------------------------------------

class GitHubTool(Tool):
    def __init__(self, store: Store, schemas: dict[str, dict]) -> None:
        self.store = store
        spec = schemas[self.name]
        self.description = spec["description"]
        self.input_schema = spec["inputSchema"]
        hints = spec.get("annotations") or {}
        self.annotations = {k: hints[k] for k in HINTS if k in hints}
        if hints.get("title"):
            self.title = hints["title"]

    def repo(self, args: dict, action: str, suffix: str = "") -> dict:
        repo = self.store.repo(args.get("owner"), args.get("repo"))
        if repo is None:
            raise not_found(action, f"/repos/{args.get('owner')}/{args.get('repo')}{suffix}")
        return repo


class GetMe(GitHubTool):
    name = "get_me"

    def run(self, args: dict, ctx: CallContext) -> Any:
        me = self.store.me
        owned = sum(1 for r in self.store.repos if r["owner"] == me["login"])
        details = {"name": me["name"], "company": me["company"], "bio": me["bio"], "public_repos": owned,
                   "public_gists": 0, "followers": 0, "following": 0, "created_at": me["created_at"],
                   "updated_at": me["updated_at"]}
        return minimal_user(self.store, me["login"]) | {"details": details}


class SearchUsers(GitHubTool):
    name = "search_users"

    def run(self, args: dict, ctx: CallContext) -> Any:
        quals, words = parse(args["query"])
        users = list(self.store.users.values())
        if "type" in quals and all(v.lower() != "user" for v in quals["type"]):
            users = []
        if "org" in quals:
            users = users if any(v.lower() == self.store.org["login"] for v in quals["org"]) else []
        for w in words:
            users = [u for u in users if w.lower() in u["login"].lower() or w.lower() in u["name"].lower()]
        users = sorted(users, key=lambda u: u["login"])
        if args.get("sort") == "joined":
            users = sort_desc(users, "created_at", args.get("order"))
        return {"total_count": len(users), "incomplete_results": False,
                "items": [minimal_user(self.store, u["login"]) for u in paginate(users, args)]}


class SearchRepositories(GitHubTool):
    name = "search_repositories"

    def run(self, args: dict, ctx: CallContext) -> Any:
        quals, words = parse(args["query"])
        hits = []
        for repo in self.store.repos:
            full = f"{repo['owner']}/{repo['name']}".lower()
            ok = all(v.lower() == full for v in quals.get("repo", []))
            ok &= all(v.lower() == repo["owner"].lower() for k in ("org", "user") for v in quals.get(k, []))
            ok &= all({"private": repo["private"], "public": not repo["private"]}.get(v.lower(), True)
                      for v in quals.get("is", []))
            text = f"{repo['name']} {repo['description']}".lower()
            ok &= all(w.lower() in text for w in words)
            if ok:
                hits.append(repo)
        items = [minimal_repo(r) for r in paginate(hits, args)]
        if args.get("minimal_output") is False:
            items = [i | {"owner": {"login": r["owner"], "id": self.store.org["id"], "type": "Organization",
                                    "html_url": f"{base_url()}/{r['owner']}"}, "visibility": "private"}
                     for i, r in zip(items, hits)]
        return {"total_count": len(hits), "incomplete_results": False, "items": items}


class ListPullRequests(GitHubTool):
    name = "list_pull_requests"

    def run(self, args: dict, ctx: CallContext) -> Any:
        repo = self.repo(args, "failed to list pull requests", "/pulls")
        state = args.get("state") or "open"
        pulls = [p for p in repo["pulls"] if state == "all" or p["state"] == state]
        if args.get("base") and args["base"] != repo["default_branch"]:
            pulls = []
        if args.get("head"):
            pulls = []  # The seed records no head branches.
        sort = args.get("sort") or "created"
        key = {"created": "created_at", "updated": "updated_at"}.get(sort, "created_at")
        pulls = sort_desc(pulls, key, args.get("direction"))
        return [pick(minimal_pr(self.store, repo, p), args.get("fields")) for p in paginate(pulls, args)]


class SearchPullRequests(GitHubTool):
    name = "search_pull_requests"

    def run(self, args: dict, ctx: CallContext) -> Any:
        query = args["query"]
        quals, _ = parse(query)
        if "is:pr" not in query:
            query = f"is:pr {query}"
        if args.get("owner") and args.get("repo") and "repo" not in quals:
            query = f"repo:{args['owner']}/{args['repo']} {query}"
        quals, words = parse(query)
        hits = [(r, p) for r in self.store.repos for p in r["pulls"] if pr_matches(self.store, r, p, quals, words)]
        key = {"created": "created_at", "updated": "updated_at"}.get(args.get("sort") or "updated", "updated_at")
        hits = sorted(hits, key=lambda rp: rp[1][key], reverse=(args.get("order") or "desc") != "asc")
        items = [search_item(self.store, r, p) for r, p in paginate(hits, args)]
        if args.get("fields"):
            items = [pick(i, args["fields"]) for i in items]
        return {"total_count": len(hits), "incomplete_results": False, "items": items}


class PullRequestRead(GitHubTool):
    name = "pull_request_read"

    def run(self, args: dict, ctx: CallContext) -> Any:
        method = args["method"]
        n = args["pullNumber"]
        path = f"/repos/{args['owner']}/{args['repo']}/pulls/{n}"
        repo = self.store.repo(args["owner"], args["repo"])
        pr = next((p for p in repo["pulls"] if p["number"] == n), None) if repo else None
        what = {"get": "failed to get pull request", "get_reviews": "failed to get pull request reviews",
                "get_comments": "failed to get pull request comments",
                "get_review_comments": "failed to get pull request review comments"}.get(method,
                                                                                         "failed to get pull request")
        if method not in ("get", "get_reviews", "get_comments", "get_review_comments", *UNSEEDED_METHODS):
            raise GitHubError(f"unknown method: {method}")
        if pr is None:
            raise not_found(what, path)
        if method == "get":
            return minimal_pr(self.store, repo, pr)
        if method == "get_reviews":
            return [review_obj(self.store, repo, pr, r) for r in paginate(pr["reviews"], args)]
        if method == "get_comments":
            return []
        if method == "get_review_comments":
            return {"review_threads": [], "totalCount": 0,
                    "pageInfo": {"hasNextPage": False, "hasPreviousPage": False}}
        raise GitHubError(f"{method} is not available in this mock: the lab data has no diffs, files, commits, "
                          "statuses or check runs. Use method get, get_reviews, get_comments or get_review_comments.")


class ListLabel(GitHubTool):
    name = "list_label"

    def run(self, args: dict, ctx: CallContext) -> Any:
        repo = self.store.repo(args["owner"], args["repo"])
        if repo is None:
            raise GitHubError(f"Failed to list labels: Could not resolve to a Repository with the name "
                              f"'{args['owner']}/{args['repo']}'.")
        usage = {x["name"]: sum(x["name"] in p["labels"] for p in repo["pulls"]) for x in repo["labels"]}
        labels = sorted(repo["labels"], key=lambda x: -usage[x["name"]])
        per = min(max(int(args.get("perPage") or 100), 1), 100)
        start = int(args["after"]) if str(args.get("after") or "").isdigit() else 0
        page = labels[start:start + per]
        more = start + per < len(labels)
        info: dict[str, Any] = {"hasNextPage": more, "hasPreviousPage": start > 0}
        if page:
            info |= {"startCursor": str(start), "endCursor": str(start + len(page))}
        return {"labels": [{k: x[k] for k in ("id", "name", "color", "description")} for x in page],
                "totalCount": len(labels), "pageInfo": info}


class GetLabel(GitHubTool):
    name = "get_label"

    def run(self, args: dict, ctx: CallContext) -> Any:
        owner, name, label = args["owner"], args["repo"], args["name"]
        repo = self.store.repo(owner, name)
        if repo is None:
            raise GitHubError(f"Failed to find label: Could not resolve to a Repository with the name "
                              f"'{owner}/{name}'.")
        found = next((x for x in repo["labels"] if x["name"].lower() == label.lower()), None)
        if found is None:
            raise GitHubError(f"label '{label}' not found in {owner}/{name}")
        return {k: found[k] for k in ("id", "name", "color", "description")}


TOOLS = [GetMe, SearchUsers, SearchRepositories, ListPullRequests, SearchPullRequests, PullRequestRead, ListLabel,
         GetLabel]
