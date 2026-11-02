"""Tools of github/github-mcp-server: eight read tools and ten write tools, with names, descriptions, input schemas
and annotations copied from the live server.

Result shapes follow the live server: Minimal* types for get_me, list_pull_requests, pull_request_read and
search_repositories/search_users, raw GitHub search JSON for search_pull_requests, the GraphQL-derived maps for
list_label/get_label, and MinimalResponse ({id, url}) or a status message for writes. Fields the seed has no data
for (diffs, files, commits, SHAs, check runs) are omitted rather than invented.

Writes change only the calling conversation's copy of the seed (see store.StateStore). Links in results point at
that copy's viewer pages (/v/<token>/...) so the change is visible in the browser too.
"""

from __future__ import annotations

import hashlib
import json
import re
import shlex
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from mockmcp import CallContext, Tool, ToolError, ToolOutput

from .store import COPILOT_REVIEWER, StateStore, Store, base_url

SCHEMAS_PATH = Path(__file__).resolve().parent.parent / "seed_files" / "tool_schemas.json"
HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")
API = "https://api.github.com"
UNSEEDED_METHODS = ("get_diff", "get_status", "get_files", "get_commits", "get_check_runs")
REACTIONS = ("+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes")
REVIEW_STATES = {"APPROVE": "APPROVED", "REQUEST_CHANGES": "CHANGES_REQUESTED", "COMMENT": "COMMENTED"}
NOT_COLLABORATOR = ("Reviews may only be requested from collaborators. One or more of the users or teams you "
                    "specified is not a collaborator of the {repo} repository.")
PENDING_COMMENT_FAILED = """Failed to add comment to pending review. Possible reasons:
	- The line number doesn't exist in the pull request diff
	- The file path is incorrect
	- The side (LEFT/RIGHT) is invalid for the specified line
"""

# "/v/<token>" while serving a conversation that has its own copy of the data, else "".
LINK_SCOPE: ContextVar[str] = ContextVar("github_link_scope", default="")


def load_schemas() -> dict[str, dict]:
    return {t["name"]: t for t in json.loads(SCHEMAS_PATH.read_text(encoding="utf-8"))}


class GitHubError(ToolError):
    """Rendered as the plain error text the live server returns."""


def api_error(action: str, verb: str, path: str, status: int = 404, text: str = "Not Found") -> GitHubError:
    return GitHubError(f"{action}: {verb} {API}{path}: {status} {text} []")


def not_found(action: str, path: str) -> GitHubError:
    return api_error(action, "GET", path)


# --- shaping -------------------------------------------------------------------------------------------------------

def site() -> str:
    return base_url() + LINK_SCOPE.get()


def repo_url(repo: dict) -> str:
    return f"{site()}/{repo['owner']}/{repo['name']}"


def pull_url(repo: dict, pr: dict) -> str:
    return f"{repo_url(repo)}/pull/{pr['number']}"


def avatar(login: str) -> str:
    return f"{base_url()}/avatars/{login}.svg"


def issue_id(repo: dict, pr: dict) -> int:
    return repo["id"] * 1000 + pr["number"]


def minimal_user(store: Store, login: str) -> dict:
    u = store.user(login) or {"login": login, "id": 0}
    return {"login": u["login"], "id": u["id"], "profile_url": f"{site()}/{u['login']}",
            "avatar_url": avatar(u["login"])}


def raw_user(store: Store, login: str) -> dict:
    u = store.user(login) or {"login": login, "id": 0}
    return {"login": u["login"], "id": u["id"], "avatar_url": avatar(u["login"]),
            "html_url": f"{site()}/{u['login']}", "type": "User", "site_admin": False}


def label_obj(repo: dict, name: str) -> dict:
    return next((x for x in repo["labels"] if x["name"] == name),
                {"id": "", "name": name, "color": "ededed", "description": ""})


def repo_open_count(repo: dict) -> int:
    return sum(1 for p in repo["pulls"] if p["state"] == "open")


def repo_updated(repo: dict) -> str:
    return max(p["updated_at"] for p in repo["pulls"])


def minimal_repo(repo: dict) -> dict:
    return {"id": repo["id"], "name": repo["name"], "full_name": f"{repo['owner']}/{repo['name']}",
            "description": repo["description"], "html_url": repo_url(repo), "stargazers_count": 0,
            "forks_count": 0, "open_issues_count": repo_open_count(repo), "updated_at": repo_updated(repo),
            "private": repo["private"], "fork": False, "archived": False, "default_branch": repo["default_branch"]}


def minimal_pr(store: Store, repo: dict, pr: dict) -> dict:
    """MinimalPullRequest, in the live server's field order; empty omitempty fields are left out."""
    out: dict[str, Any] = {
        "number": pr["number"], "title": pr["title"], "body": pr["body"], "state": pr["state"],
        "draft": pr["draft"], "merged": pr["merged"], "html_url": pull_url(repo, pr),
        "user": minimal_user(store, pr["user"]),
    }
    for key in ("labels", "assignees", "requested_reviewers"):
        if pr.get(key):
            out[key] = list(pr[key])
    if pr.get("merged_by"):
        out["merged_by"] = pr["merged_by"]
    if pr.get("base") and pr["base"] != repo["default_branch"]:
        out["base"] = pr["base"]
    if pr["comments"]:
        out["comments"] = len(pr["comments"])
    out["created_at"] = pr["created_at"]
    out["updated_at"] = pr["updated_at"]
    for key in ("closed_at", "merged_at", "milestone"):
        if pr.get(key):
            out[key] = pr[key]
    return out


def search_item(store: Store, repo: dict, pr: dict) -> dict:
    """An issue-shaped item, as returned by GitHub's /search/issues for a pull request."""
    url = pull_url(repo, pr)
    milestone = {"title": pr["milestone"], "state": "open"} if pr.get("milestone") else None
    return {
        "id": issue_id(repo, pr), "number": pr["number"], "title": pr["title"], "body": pr["body"],
        "state": pr["state"], "locked": False, "draft": pr["draft"], "html_url": url,
        "repository_url": repo_url(repo), "user": raw_user(store, pr["user"]),
        "labels": [{k: label_obj(repo, n)[k] for k in ("id", "name", "color", "description")}
                   | {"default": n in ("bug", "enhancement")} for n in pr["labels"]],
        "assignee": raw_user(store, pr["assignees"][0]) if pr["assignees"] else None,
        "assignees": [raw_user(store, a) for a in pr["assignees"]], "milestone": milestone,
        "comments": len(pr["comments"]), "created_at": pr["created_at"], "updated_at": pr["updated_at"],
        "closed_at": pr.get("closed_at"), "author_association": "MEMBER",
        "pull_request": {"url": url, "html_url": url, "merged_at": pr.get("merged_at")},
    }


def reactions_obj(items: list[dict]) -> dict | None:
    if not items:
        return None
    out: dict[str, int] = {"total_count": len(items)}
    for content in REACTIONS:
        n = sum(1 for r in items if r["content"] == content)
        if n:
            out[content] = n
    return out


def visible_reviews(store: Store, pr: dict) -> list[dict]:
    """Pending reviews are visible only to their author, as on GitHub."""
    me = store.me["login"]
    return [r for r in pr["reviews"] if r["state"] != "PENDING" or r["user"] == me]


def review_obj(store: Store, repo: dict, pr: dict, r: dict) -> dict:
    out = {"id": r["id"], "state": r["state"], "body": r["body"],
           "html_url": f"{pull_url(repo, pr)}#pullrequestreview-{r['id']}", "user": minimal_user(store, r["user"])}
    if r.get("submitted_at"):
        out["submitted_at"] = r["submitted_at"]
    out["author_association"] = "MEMBER"
    return out


def issue_comment_obj(store: Store, repo: dict, pr: dict, c: dict) -> dict:
    out = {"id": c["id"], "body": c["body"], "html_url": f"{pull_url(repo, pr)}#issuecomment-{c['id']}",
           "user": minimal_user(store, c["user"]), "author_association": "MEMBER"}
    reactions = reactions_obj(c["reactions"])
    if reactions:
        out["reactions"] = reactions
    out["created_at"] = c["created_at"]
    out["updated_at"] = c["updated_at"]
    return out


def comment_visible(store: Store, pr: dict, c: dict) -> bool:
    review = next((r for r in pr["reviews"] if r["id"] == c.get("review_id")), None)
    return review is None or review["state"] != "PENDING" or review["user"] == store.me["login"]


def thread_obj(store: Store, repo: dict, pr: dict, t: dict) -> dict | None:
    comments = []
    for c in t["comments"]:
        if not comment_visible(store, pr, c):
            continue
        item: dict[str, Any] = {"body": c["body"], "path": c["path"]}
        if c.get("line"):
            item["line"] = c["line"]
            item["original_line"] = c["line"]
        if c.get("start_line"):
            item["start_line"] = c["start_line"]
            item["original_start_line"] = c["start_line"]
        item |= {"author": c["user"], "created_at": c["created_at"], "updated_at": c["updated_at"],
                 "html_url": f"{pull_url(repo, pr)}#discussion_r{c['id']}"}
        comments.append(item)
    if not comments:
        return None
    return {"id": t["id"], "is_resolved": t["is_resolved"], "is_outdated": False, "is_collapsed": t["is_resolved"],
            "comments": comments, "total_count": len(comments)}


def pick(obj: dict, fields: list[str] | None) -> dict:
    return {k: obj[k] for k in fields if k in obj} if fields else obj


def paginate(items: list, args: dict, default: int = 30) -> list:
    page = max(int(args.get("page") or 1), 1)
    per = min(max(int(args.get("perPage") or default), 1), 100)
    return items[(page - 1) * per: page * per]


def cursor_page(items: list, args: dict, default: int) -> tuple[list, dict]:
    per = min(max(int(args.get("perPage") or default), 1), 100)
    start = int(args["after"]) if str(args.get("after") or "").isdigit() else 0
    page = items[start:start + per]
    info: dict[str, Any] = {"hasNextPage": start + per < len(items), "hasPreviousPage": start > 0}
    if page:
        info |= {"startCursor": str(start), "endCursor": str(start + len(page))}
    return page, info


def sort_desc(items: list[dict], key: str, order: str | None) -> list[dict]:
    return sorted(items, key=lambda x: (x.get(key) or ""), reverse=(order or "desc") != "asc")


def find_pr(repo: dict | None, number: Any) -> dict | None:
    if repo is None:
        return None
    return next((p for p in repo["pulls"] if p["number"] == number), None)


def latest_review_states(pr: dict) -> dict[str, str]:
    """Each reviewer's latest deciding review (comment-only reviews don't change it)."""
    latest: dict[str, str] = {}
    for r in sorted((r for r in pr["reviews"] if r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")),
                    key=lambda r: r.get("submitted_at") or ""):
        latest[r["user"]] = r["state"]
    return latest


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
    reviews = [r for r in visible_reviews(store, pr) if r["state"] != "PENDING"]
    reviewers = [r["user"] for r in reviews]
    review_comments = [c for t in pr["threads"] for c in t["comments"]
                       if comment_visible(store, pr, c) and _submitted(pr, c)]
    commenters = [c["user"] for c in pr["comments"]] + [c["user"] for c in review_comments] + reviewers
    people = {pr["user"], *pr["assignees"], *commenters}

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
        if key == "reviewed-by":
            return any(_has_user(store, val, r) for r in reviewers)
        if key == "review-requested":
            return any(_has_user(store, val, r) for r in pr["requested_reviewers"])
        if key == "commenter":
            return any(_has_user(store, val, c) for c in commenters)
        if key in ("involves", "mentions"):
            return any(_has_user(store, val, p) for p in people)
        if key == "label":
            have = {x.lower() for x in pr["labels"]}
            return any(part.strip().lower() in have for part in val.split(","))
        if key == "milestone":
            return (pr.get("milestone") or "").lower() == v
        if key == "base":
            return (pr.get("base") or repo["default_branch"]).lower() == v
        if key == "review":
            states = list(latest_review_states(pr).values())
            return {"approved": "APPROVED" in states and "CHANGES_REQUESTED" not in states,
                    "changes_requested": "CHANGES_REQUESTED" in states,
                    "none": not states, "required": not states}.get(v, True)
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
            hay += [r["body"] for r in reviews]
            hay += [c["body"] for c in pr["comments"]] + [c["body"] for c in review_comments]
        text = "\n".join(hay).lower()
        if not all(w.lower() in text for w in words):
            return False
    return True


def _submitted(pr: dict, c: dict) -> bool:
    """Search indexes only published review comments, never a pending draft."""
    review = next((r for r in pr["reviews"] if r["id"] == c.get("review_id")), None)
    return review is None or review["state"] != "PENDING"


# --- tool base -----------------------------------------------------------------------------------------------------

class GitHubTool(Tool):
    """Reads run against the conversation's copy (or the seed); writes (``writes = True``) run against a scratch
    copy that is kept for the conversation only if the handler succeeds."""

    writes = False

    def __init__(self, state: StateStore, schemas: dict[str, dict]) -> None:
        self.state = state
        spec = schemas[self.name]
        self.description = spec["description"]
        self.input_schema = spec["inputSchema"]
        hints = spec.get("annotations") or {}
        self.annotations = {k: hints[k] for k in HINTS if k in hints}
        if hints.get("title"):
            self.title = hints["title"]

    def run(self, args: dict, ctx: CallContext) -> Any:
        conv = ctx.conversation_id
        scope = f"/v/{self.state.view_token(conv)}" if conv and (self.writes or self.state.has_overlay(conv)) else ""
        token = LINK_SCOPE.set(scope)
        try:
            if not self.writes:
                return self.handle(self.state.read(conv), args, ctx)
            with self.state.write(conv) as store:
                return self.handle(store, args, ctx)
        finally:
            LINK_SCOPE.reset(token)

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        raise NotImplementedError

    @staticmethod
    def repo(store: Store, args: dict, action: str, suffix: str = "", verb: str = "GET") -> dict:
        repo = store.repo(args.get("owner"), args.get("repo"))
        if repo is None:
            raise api_error(action, verb, f"/repos/{args.get('owner')}/{args.get('repo')}{suffix}")
        return repo

    @staticmethod
    def now(ctx: CallContext) -> str:
        return ctx.clock.iso(millis=False)


# --- read tools ----------------------------------------------------------------------------------------------------

class GetMe(GitHubTool):
    name = "get_me"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        me = store.me
        owned = sum(1 for r in store.repos if r["owner"] == me["login"])
        details = {"name": me["name"], "company": me["company"], "bio": me["bio"], "public_repos": owned,
                   "public_gists": 0, "followers": 0, "following": 0, "created_at": me["created_at"],
                   "updated_at": me["updated_at"]}
        return minimal_user(store, me["login"]) | {"details": details}


class SearchUsers(GitHubTool):
    name = "search_users"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        quals, words = parse(args["query"])
        users = list(store.users.values())
        if "type" in quals and all(v.lower() != "user" for v in quals["type"]):
            users = []
        if "org" in quals:
            users = users if any(v.lower() == store.org["login"] for v in quals["org"]) else []
        for w in words:
            users = [u for u in users if w.lower() in u["login"].lower() or w.lower() in u["name"].lower()]
        users = sorted(users, key=lambda u: u["login"])
        if args.get("sort") == "joined":
            users = sort_desc(users, "created_at", args.get("order"))
        return {"total_count": len(users), "incomplete_results": False,
                "items": [minimal_user(store, u["login"]) for u in paginate(users, args)]}


class SearchRepositories(GitHubTool):
    name = "search_repositories"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        quals, words = parse(args["query"])
        hits = []
        for repo in store.repos:
            full = f"{repo['owner']}/{repo['name']}".lower()
            ok = all(v.lower() == full for v in quals.get("repo", []))
            ok &= all(v.lower() == repo["owner"].lower() for k in ("org", "user") for v in quals.get(k, []))
            ok &= all({"private": repo["private"], "public": not repo["private"]}.get(v.lower(), True)
                      for v in quals.get("is", []))
            text = f"{repo['name']} {repo['description']}".lower()
            ok &= all(w.lower() in text for w in words)
            if ok:
                hits.append(repo)
        page = paginate(hits, args)
        items = [minimal_repo(r) for r in page]
        if args.get("minimal_output") is False:
            items = [i | {"owner": {"login": r["owner"], "id": store.org["id"], "type": "Organization",
                                    "html_url": f"{site()}/{r['owner']}"}, "visibility": "private"}
                     for i, r in zip(items, page)]
        return {"total_count": len(hits), "incomplete_results": False, "items": items}


class ListPullRequests(GitHubTool):
    name = "list_pull_requests"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        repo = self.repo(store, args, "failed to list pull requests", "/pulls")
        state = args.get("state") or "open"
        pulls = [p for p in repo["pulls"] if state == "all" or p["state"] == state]
        if args.get("base"):
            pulls = [p for p in pulls if p["base"] == args["base"]]
        if args.get("head"):
            pulls = []  # The seed records no head branches.
        key = {"created": "created_at", "updated": "updated_at"}.get(args.get("sort") or "created", "created_at")
        pulls = sort_desc(pulls, key, args.get("direction"))
        return [pick(minimal_pr(store, repo, p), args.get("fields")) for p in paginate(pulls, args)]


class SearchPullRequests(GitHubTool):
    name = "search_pull_requests"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        query = args["query"]
        quals, _ = parse(query)
        if "is:pr" not in query:
            query = f"is:pr {query}"
        if args.get("owner") and args.get("repo") and "repo" not in quals:
            query = f"repo:{args['owner']}/{args['repo']} {query}"
        quals, words = parse(query)
        hits = [(r, p) for r in store.repos for p in r["pulls"] if pr_matches(store, r, p, quals, words)]
        key = {"created": "created_at", "updated": "updated_at"}.get(args.get("sort") or "updated", "updated_at")
        hits = sorted(hits, key=lambda rp: rp[1][key], reverse=(args.get("order") or "desc") != "asc")
        items = [search_item(store, r, p) for r, p in paginate(hits, args)]
        if args.get("fields"):
            items = [pick(i, args["fields"]) for i in items]
        return {"total_count": len(hits), "incomplete_results": False, "items": items}


class PullRequestRead(GitHubTool):
    name = "pull_request_read"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        method = args["method"]
        n = args["pullNumber"]
        owner, name = args["owner"], args["repo"]
        path = f"/repos/{owner}/{name}/pulls/{n}"
        repo = store.repo(owner, name)
        pr = find_pr(repo, n)
        if method not in ("get", "get_reviews", "get_comments", "get_review_comments", *UNSEEDED_METHODS):
            raise GitHubError(f"unknown method: {method}")
        if method == "get_review_comments":
            if pr is None:
                what = f"Could not resolve to a Repository with the name '{owner}/{name}'." if repo is None \
                    else f"Could not resolve to a PullRequest with the number of {n}."
                raise GitHubError(f"failed to get pull request review threads: {what}")
            threads = [t for t in (thread_obj(store, repo, pr, t) for t in pr["threads"]) if t]
            page, info = cursor_page(threads, args, 30)
            return {"review_threads": page, "totalCount": len(threads), "pageInfo": info}
        if pr is None:
            if method == "get_reviews":
                raise not_found("failed to get pull request reviews", path + "/reviews")
            if method == "get_comments":
                raise not_found("failed to get pull request comments", f"/repos/{owner}/{name}/issues/{n}/comments")
            raise not_found("failed to get pull request", path)
        if method == "get":
            return minimal_pr(store, repo, pr)
        if method == "get_reviews":
            return [review_obj(store, repo, pr, r) for r in paginate(visible_reviews(store, pr), args)]
        if method == "get_comments":
            return [issue_comment_obj(store, repo, pr, c) for c in paginate(pr["comments"], args)]
        raise GitHubError(f"{method} is not available in this mock: the lab data has no diffs, files, commits, "
                          "statuses or check runs. Use method get, get_reviews, get_comments or get_review_comments.")


class ListLabel(GitHubTool):
    name = "list_label"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        repo = store.repo(args["owner"], args["repo"])
        if repo is None:
            raise GitHubError(f"Failed to list labels: Could not resolve to a Repository with the name "
                              f"'{args['owner']}/{args['repo']}'.")
        usage = {x["name"]: sum(x["name"] in p["labels"] for p in repo["pulls"]) for x in repo["labels"]}
        labels = sorted(repo["labels"], key=lambda x: -usage[x["name"]])
        page, info = cursor_page(labels, args, 100)
        return {"labels": [{k: x[k] for k in ("id", "name", "color", "description")} for x in page],
                "totalCount": len(labels), "pageInfo": info}


class GetLabel(GitHubTool):
    name = "get_label"

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name, label = args["owner"], args["repo"], args["name"]
        repo = store.repo(owner, name)
        if repo is None:
            raise GitHubError(f"Failed to find label: Could not resolve to a Repository with the name "
                              f"'{owner}/{name}'.")
        found = next((x for x in repo["labels"] if x["name"].lower() == label.lower()), None)
        if found is None:
            raise GitHubError(f"label '{label}' not found in {owner}/{name}")
        return {k: found[k] for k in ("id", "name", "color", "description")}


# --- write helpers -------------------------------------------------------------------------------------------------

def minimal_response(id_: Any, url: str) -> dict:
    return {"id": str(id_), "url": url}


def add_reaction(store: Store, target: list[dict], content: str) -> dict:
    """GitHub returns the existing reaction when the same user reacts the same way twice."""
    me = store.me["login"]
    existing = next((r for r in target if r["user"] == me and r["content"] == content), None)
    if existing:
        return existing
    reaction = {"id": store.next_id("reaction"), "user": me, "content": content}
    target.append(reaction)
    return reaction


def check_body_and_reaction(args: dict) -> tuple[str | None, str | None]:
    has_body, has_reaction = "body" in args, "reaction" in args
    if not has_body and not has_reaction:
        raise GitHubError("at least one of body or reaction is required")
    if has_body and args["body"] == "":
        raise GitHubError("body cannot be empty when provided")
    if has_reaction and args["reaction"] == "":
        raise GitHubError("reaction cannot be empty when provided")
    if has_reaction and args["reaction"] not in REACTIONS:
        raise GitHubError("reaction must be one of " + ", ".join(REACTIONS))
    return (args["body"] if has_body else None), (args["reaction"] if has_reaction else None)


def find_issue_comment(repo: dict, comment_id: int) -> tuple[dict, dict] | None:
    return next(((p, c) for p in repo["pulls"] for c in p["comments"] if c["id"] == comment_id), None)


def find_review_comment(store: Store, repo: dict, comment_id: int) -> tuple[dict, dict, dict] | None:
    for p in repo["pulls"]:
        for t in p["threads"]:
            for c in t["comments"]:
                if c["id"] == comment_id and comment_visible(store, p, c):
                    return p, t, c
    return None


def find_thread(store: Store, thread_id: str) -> tuple[dict, dict] | None:
    for r in store.repos:
        for p in r["pulls"]:
            for t in p["threads"]:
                if t["id"] == thread_id and any(comment_visible(store, p, c) for c in t["comments"]):
                    return p, t
    return None


def pending_review(store: Store, pr: dict) -> dict | None:
    me = store.me["login"]
    return next((r for r in pr["reviews"] if r["state"] == "PENDING" and r["user"] == me), None)


def graphql_pr(store: Store, args: dict, action: str) -> tuple[dict, dict]:
    repo = store.repo(args.get("owner"), args.get("repo"))
    if repo is None:
        raise GitHubError(f"{action}: Could not resolve to a Repository with the name "
                          f"'{args.get('owner')}/{args.get('repo')}'.")
    pr = find_pr(repo, args["pullNumber"])
    if pr is None:
        raise GitHubError(f"{action}: Could not resolve to a PullRequest with the number of {args['pullNumber']}.")
    return repo, pr


def int_arg(args: dict, key: str) -> int | None:
    value = args.get(key)
    if value is None:
        return None
    if isinstance(value, float) and not value.is_integer():
        raise GitHubError(f"parameter {key} is not a valid number")
    return int(value)


def own_review_error(event: str) -> str:
    return f"Can not {'approve' if event == 'APPROVE' else 'request changes on'} your own pull request"


# --- write tools ---------------------------------------------------------------------------------------------------

class AddIssueComment(GitHubTool):
    name = "add_issue_comment"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name, number = args["owner"], args["repo"], int_arg(args, "issue_number")
        comment_id = int_arg(args, "comment_id")
        if comment_id is not None:
            if comment_id < 1:
                raise GitHubError("comment_id must be greater than 0")
            if "body" in args:
                raise GitHubError("comment_id cannot be combined with body")
            if "reaction" not in args:
                raise GitHubError("comment_id can only be provided when reaction is provided")
        body, reaction = check_body_and_reaction(args)
        repo = store.repo(owner, name)
        pr = find_pr(repo, number)
        base = f"/repos/{owner}/{name}"
        out: dict[str, Any] = {}
        if reaction is not None:
            if comment_id is not None:
                found = find_issue_comment(repo, comment_id) if repo else None
                if found is None:
                    raise not_found("failed to get issue comment", f"{base}/issues/comments/{comment_id}")
                if found[0]["number"] != number:
                    raise GitHubError(f"comment_id does not belong to issue_number {number}")
                r = add_reaction(store, found[1]["reactions"], reaction)
                out["reaction"] = minimal_response(
                    r["id"], f"{API}{base}/issues/comments/{comment_id}/reactions/{r['id']}")
            else:
                if pr is None:
                    raise api_error("failed to add reaction to issue", "POST", f"{base}/issues/{number}/reactions")
                r = add_reaction(store, pr["reactions"], reaction)
                out["reaction"] = minimal_response(r["id"], f"{API}{base}/issues/{number}/reactions/{r['id']}")
        if body is not None:
            if pr is None:
                raise api_error("failed to create comment", "POST", f"{base}/issues/{number}/comments")
            now = self.now(ctx)
            c = {"id": store.next_id("issue_comment"), "user": store.me["login"], "body": body,
                 "created_at": now, "updated_at": now, "reactions": []}
            pr["comments"].append(c)
            pr["updated_at"] = now
            out["comment"] = minimal_response(c["id"], f"{pull_url(repo, pr)}#issuecomment-{c['id']}")
        return out if len(out) == 2 else next(iter(out.values()))


class UpdateIssueComment(GitHubTool):
    name = "update_issue_comment"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name = args["owner"], args["repo"]
        comment_id = int_arg(args, "comment_id")
        if comment_id < 1:
            raise GitHubError("comment_id must be greater than 0")
        if args["body"] == "":
            raise GitHubError("body cannot be empty when provided")
        repo = store.repo(owner, name)
        found = find_issue_comment(repo, comment_id) if repo else None
        if found is None:
            raise api_error("failed to update issue comment", "PATCH",
                            f"/repos/{owner}/{name}/issues/comments/{comment_id}")
        pr, c = found
        c["body"] = args["body"]
        c["updated_at"] = self.now(ctx)
        return minimal_response(c["id"], f"{pull_url(repo, pr)}#issuecomment-{c['id']}")


class IssueWrite(GitHubTool):
    name = "issue_write"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        method, owner, name = args["method"], args["owner"], args["repo"]
        if method not in ("create", "update"):
            raise GitHubError("invalid method, must be either 'create' or 'update'")
        number = int_arg(args, "issue_number")
        if method == "update" and not number:
            raise GitHubError("issue_number is required for update method")
        if args.get("duplicate_of") and args.get("state_reason") != "duplicate":
            raise GitHubError("duplicate_of can only be used when state_reason is 'duplicate'")
        if method == "update" and args.get("parent_issue_number"):
            raise GitHubError("parent_issue_number can only be used with the create method")
        repo = store.repo(owner, name)
        base = f"/repos/{owner}/{name}"
        if method == "create":
            # The lab repository tracks its work in Jira, so GitHub Issues are turned off for it.
            if repo is None:
                raise api_error("failed to create issue", "POST", f"{base}/issues")
            raise api_error("failed to create issue", "POST", f"{base}/issues", 410,
                            "Issues are disabled for this repo")
        for key in ("milestone", "type", "issue_fields"):
            if args.get(key) is not None:
                raise GitHubError(f"{key} is not available in this mock: the lab repository has no numbered "
                                  "milestones, issue types or issue fields. Leave it out and try again.")
        pr = find_pr(repo, number)
        path = f"{base}/issues/{number}"
        if pr is None:
            raise api_error("failed to update issue", "PATCH", path)
        if "assignees" in args and any(store.user(a) is None for a in args["assignees"]):
            raise api_error("failed to update issue", "PATCH", path, 422, "Validation Failed")
        state = args.get("state")
        if state and state != pr["state"] and pr["merged"]:
            raise api_error("failed to update issue", "PATCH", path, 422, "Validation Failed")
        now = self.now(ctx)
        if "assignees" in args:
            pr["assignees"] = list(dict.fromkeys(store.user(a)["login"] for a in args["assignees"]))
        if "labels" in args:
            for label in args["labels"]:
                if not any(x["name"].lower() == label.lower() for x in repo["labels"]):
                    repo["labels"].append({"id": f"LA_aurora_{store.next_id('label')}", "name": label,
                                           "color": "ededed", "description": ""})
            pr["labels"] = list(dict.fromkeys(
                next(x["name"] for x in repo["labels"] if x["name"].lower() == label.lower())
                for label in args["labels"]))
        if args.get("title") is not None:
            pr["title"] = args["title"]
        if args.get("body") is not None:
            pr["body"] = args["body"]
        if state and state != pr["state"]:
            pr["state"] = state
            pr["closed_at"] = now if state == "closed" else None
        pr["updated_at"] = now
        return minimal_response(issue_id(repo, pr), pull_url(repo, pr))


class LabelWrite(GitHubTool):
    name = "label_write"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        method, owner, name, label = args["method"], args["owner"], args["repo"], args["name"]
        if method not in ("create", "update", "delete"):
            raise GitHubError(f"unknown method: {method}. Supported methods are: create, update, delete")
        if method == "create" and not args.get("color"):
            raise GitHubError("color is required for create")
        if method == "update" and not any(args.get(k) for k in ("new_name", "color", "description")):
            raise GitHubError("at least one of new_name, color, or description must be provided for update")
        repo = store.repo(owner, name)
        if repo is None:
            raise GitHubError(f"Failed to find repository: Could not resolve to a Repository with the name "
                              f"'{owner}/{name}'.")
        color = (args.get("color") or "").lstrip("#").lower()
        if color and not re.fullmatch(r"[0-9a-f]{6}", color):
            raise GitHubError(f"Failed to {method} label: Color is invalid")
        found = next((x for x in repo["labels"] if x["name"].lower() == label.lower()), None)
        if method == "create":
            if found:
                raise GitHubError("Failed to create label: Name has already been taken")
            repo["labels"].append({"id": f"LA_aurora_{store.next_id('label')}", "name": label, "color": color,
                                   "description": args.get("description") or ""})
            return f"label '{label}' created successfully"
        if found is None:
            raise GitHubError(f"label '{label}' not found in {owner}/{name}")
        if method == "delete":
            repo["labels"].remove(found)
            for p in repo["pulls"]:
                p["labels"] = [x for x in p["labels"] if x != found["name"]]
            return f"label '{label}' deleted successfully"
        new_name = args.get("new_name") or found["name"]
        if new_name.lower() != found["name"].lower() and any(
                x["name"].lower() == new_name.lower() for x in repo["labels"]):
            raise GitHubError("Failed to update label: Name has already been taken")
        for p in repo["pulls"]:
            p["labels"] = [new_name if x == found["name"] else x for x in p["labels"]]
        found["name"] = new_name
        if color:
            found["color"] = color
        if args.get("description") is not None:
            found["description"] = args["description"]
        return f"label '{new_name}' updated successfully"


class PullRequestReviewWrite(GitHubTool):
    name = "pull_request_review_write"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        method = args["method"]
        me = store.me["login"]
        now = self.now(ctx)
        if method in ("resolve_thread", "unresolve_thread"):
            thread_id = args.get("threadId")
            if not thread_id:
                raise GitHubError("threadId is required for resolve_thread and unresolve_thread methods")
            found = find_thread(store, thread_id)
            verb = method.split("_")[0]
            if found is None:
                raise GitHubError(f"failed to {verb} review thread: Could not resolve to a node with the global id "
                                  f"of '{thread_id}'")
            pr, thread = found
            thread["is_resolved"] = method == "resolve_thread"
            thread["resolved_by"] = me if thread["is_resolved"] else None
            pr["updated_at"] = now
            return f"review thread {verb}d successfully"
        if method not in ("create", "submit_pending", "delete_pending"):
            raise GitHubError(f"unknown method: {method}")
        event = args.get("event")
        _, pr = graphql_pr(store, args, "failed to get pull request")
        if method == "create":
            if pending_review(store, pr):
                raise GitHubError("failed to create pull request review: User can only have one pending review "
                                  "per pull request")
            if event and pr["user"] == me and event != "COMMENT":
                raise GitHubError(f"failed to create pull request review: {own_review_error(event)}")
            review = {"id": store.next_id("review"), "user": me, "state": "PENDING", "body": args.get("body") or "",
                      "submitted_at": None}
            pr["reviews"].append(review)
            if not event:
                return "pending pull request created"
            self.submit(pr, review, event, args.get("body"), now)
            return "pull request review submitted successfully"
        review = pending_review(store, pr)
        if review is None:
            raise GitHubError("No pending review found for the viewer")
        if method == "delete_pending":
            pr["reviews"].remove(review)
            for t in pr["threads"]:
                t["comments"] = [c for c in t["comments"] if c.get("review_id") != review["id"]]
            pr["threads"] = [t for t in pr["threads"] if t["comments"]]
            return "pending pull request review successfully deleted"
        if not event:
            raise GitHubError("failed to submit pull request review: event is required to submit a pending review "
                              "(APPROVE, REQUEST_CHANGES or COMMENT)")
        if pr["user"] == me and event != "COMMENT":
            raise GitHubError(f"failed to submit pull request review: {own_review_error(event)}")
        self.submit(pr, review, event, args.get("body"), now)
        return "pending pull request review successfully submitted"

    @staticmethod
    def submit(pr: dict, review: dict, event: str, body: str | None, now: str) -> None:
        review["state"] = REVIEW_STATES[event]
        if body is not None:
            review["body"] = body
        review["submitted_at"] = now
        for t in pr["threads"]:
            for c in t["comments"]:
                if c.get("review_id") == review["id"]:
                    c["created_at"] = c["updated_at"] = now
        pr["requested_reviewers"] = [r for r in pr["requested_reviewers"] if r != review["user"]]
        pr["updated_at"] = now


class AddCommentToPendingReview(GitHubTool):
    name = "add_comment_to_pending_review"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        _, pr = graphql_pr(store, args, "failed to get pull request")
        review = pending_review(store, pr)
        if review is None:
            raise GitHubError("No pending review found for the viewer")
        line, start = int_arg(args, "line"), int_arg(args, "startLine")
        if not args["path"].strip() or (args["subjectType"] == "LINE" and not line) or \
                (start is not None and (line is None or start > line)):
            raise GitHubError(PENDING_COMMENT_FAILED)
        now = self.now(ctx)
        is_line = args["subjectType"] == "LINE"
        comment = {"id": store.next_id("review_comment"), "user": store.me["login"], "body": args["body"],
                   "path": args["path"], "subject_type": args["subjectType"], "line": line if is_line else None,
                   "side": (args.get("side") or "RIGHT") if is_line else None,
                   "start_line": start if is_line else None, "start_side": args.get("startSide") if is_line else None,
                   "review_id": review["id"], "created_at": now, "updated_at": now, "reactions": []}
        pr["threads"].append({"id": f"PRRT_kwDOLabMock{comment['id']}", "is_resolved": False, "resolved_by": None,
                              "comments": [comment]})
        return "pull request review comment successfully added to pending review"


class AddReplyToPullRequestComment(GitHubTool):
    name = "add_reply_to_pull_request_comment"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name = args["owner"], args["repo"]
        comment_id = int_arg(args, "commentId")
        if comment_id < 1:
            raise GitHubError("commentId must be greater than 0")
        body, reaction = check_body_and_reaction(args)
        number = None
        if body is not None:
            number = int_arg(args, "pullNumber")
            if number is None:
                raise GitHubError("missing required parameter: pullNumber")
        repo = store.repo(owner, name)
        found = find_review_comment(store, repo, comment_id) if repo else None
        base = f"/repos/{owner}/{name}"
        out: dict[str, Any] = {}
        if reaction is not None:
            if found is None:
                raise api_error("failed to add reaction to pull request review comment", "POST",
                                f"{base}/pulls/comments/{comment_id}/reactions")
            r = add_reaction(store, found[2]["reactions"], reaction)
            out["reaction"] = minimal_response(
                r["id"], f"{API}{base}/pulls/comments/{comment_id}/reactions/{r['id']}")
        if body is not None:
            if found is None or found[0]["number"] != number:
                raise api_error("failed to add reply to pull request comment", "POST",
                                f"{base}/pulls/{number}/comments/{comment_id}/replies")
            pr, thread, parent = found
            now = self.now(ctx)
            reply = {k: parent.get(k) for k in ("path", "subject_type", "line", "side", "start_line", "start_side")}
            reply |= {"id": store.next_id("review_comment"), "user": store.me["login"], "body": body,
                      "review_id": None, "in_reply_to": comment_id, "created_at": now, "updated_at": now,
                      "reactions": []}
            thread["comments"].append(reply)
            pr["updated_at"] = now
            out["comment"] = minimal_response(reply["id"], f"{pull_url(repo, pr)}#discussion_r{reply['id']}")
        return out if len(out) == 2 else next(iter(out.values()))


def request_reviewers(store: Store, repo: dict, pr: dict, reviewers: list[str], path: str, action: str) -> None:
    logins = []
    for login in reviewers:
        if login.lower() == COPILOT_REVIEWER or login.lower() == "copilot":
            logins.append(COPILOT_REVIEWER)
            continue
        user = store.user(login)
        if user is None:
            raise api_error(action, "POST", path, 422,
                            NOT_COLLABORATOR.format(repo=f"{repo['owner']}/{repo['name']}"))
        if user["login"] == pr["user"]:
            raise api_error(action, "POST", path, 422, "Review cannot be requested from pull request author.")
        logins.append(user["login"])
    if pr["state"] != "open":
        raise api_error(action, "POST", path, 422, "Unprocessable Entity")
    for login in logins:
        if login not in pr["requested_reviewers"]:
            pr["requested_reviewers"].append(login)


class UpdatePullRequest(GitHubTool):
    name = "update_pull_request"
    writes = True
    REST_KEYS = ("title", "body", "state", "base", "maintainer_can_modify")

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name, number = args["owner"], args["repo"], int_arg(args, "pullNumber")
        rest = {k: args[k] for k in self.REST_KEYS if args.get(k) is not None}
        draft = args.get("draft")
        reviewers = args.get("reviewers") or []
        if not rest and draft is None and not reviewers:
            raise GitHubError("No update parameters provided.")
        repo = store.repo(owner, name)
        pr = find_pr(repo, number)
        path = f"/repos/{owner}/{name}/pulls/{number}"
        now = self.now(ctx)
        if rest:
            if pr is None:
                raise api_error("failed to update pull request", "PATCH", path)
            if rest.get("base") and rest["base"] != repo["default_branch"]:
                raise api_error("failed to update pull request", "PATCH", path, 422, "Validation Failed")
            if rest.get("state") and rest["state"] != pr["state"]:
                if pr["merged"]:
                    raise api_error("failed to update pull request", "PATCH", path, 422, "Validation Failed")
                pr["state"] = rest["state"]
                pr["closed_at"] = now if rest["state"] == "closed" else None
            for key in ("title", "body", "base", "maintainer_can_modify"):
                if key in rest:
                    pr[key] = rest[key]
        if draft is not None:
            if pr is None:
                what = f"Could not resolve to a PullRequest with the number of {number}." if repo else \
                    f"Could not resolve to a Repository with the name '{owner}/{name}'."
                raise GitHubError(f"Failed to find pull request: {what}")
            if draft != pr["draft"]:
                if pr["state"] != "open":
                    action = "Failed to convert pull request to draft" if draft else \
                        "Failed to mark pull request ready for review"
                    raise GitHubError(f"{action}: Pull request is closed")
                pr["draft"] = draft
        if reviewers:
            if pr is None:
                raise api_error("failed to request reviewers", "POST", f"{path}/requested_reviewers")
            request_reviewers(store, repo, pr, reviewers, f"{path}/requested_reviewers",
                              "failed to request reviewers")
        pr["updated_at"] = now
        return minimal_response(issue_id(repo, pr), pull_url(repo, pr))


class MergePullRequest(GitHubTool):
    name = "merge_pull_request"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name, number = args["owner"], args["repo"], int_arg(args, "pullNumber")
        method = args.get("merge_method") or "merge"
        repo = store.repo(owner, name)
        pr = find_pr(repo, number)
        path = f"/repos/{owner}/{name}/pulls/{number}/merge"
        if pr is None:
            raise api_error("failed to merge pull request", "PUT", path)
        if pr["merged"] or pr["state"] != "open" or pr["draft"]:
            raise api_error("failed to merge pull request", "PUT", path, 405, "Pull Request is not mergeable")
        # main is protected: it needs an approving review and no outstanding request for changes.
        states = latest_review_states(pr).values()
        if "CHANGES_REQUESTED" in states or "APPROVED" not in states:
            raise api_error("failed to merge pull request", "PUT", path, 405,
                            "At least 1 approving review is required by reviewers with write access.")
        now = self.now(ctx)
        sha = hashlib.sha1(f"{owner}/{name}#{number}:{method}:{now}".encode()).hexdigest()
        pr |= {"merged": True, "state": "closed", "merged_at": now, "closed_at": now,
               "merged_by": store.me["login"], "updated_at": now, "requested_reviewers": []}
        return {"sha": sha, "merged": True, "message": "Pull Request successfully merged"}


class RequestCopilotReview(GitHubTool):
    name = "request_copilot_review"
    writes = True

    def handle(self, store: Store, args: dict, ctx: CallContext) -> Any:
        owner, name, number = args["owner"], args["repo"], int_arg(args, "pullNumber")
        repo = store.repo(owner, name)
        pr = find_pr(repo, number)
        path = f"/repos/{owner}/{name}/pulls/{number}/requested_reviewers"
        if pr is None:
            raise api_error("failed to request copilot review", "POST", path)
        request_reviewers(store, repo, pr, [COPILOT_REVIEWER], path, "failed to request copilot review")
        pr["updated_at"] = self.now(ctx)
        return ToolOutput("", {"status": "requested"})


READ_TOOLS = [GetMe, SearchUsers, SearchRepositories, ListPullRequests, SearchPullRequests, PullRequestRead,
              ListLabel, GetLabel]
WRITE_TOOLS = [AddIssueComment, UpdateIssueComment, IssueWrite, LabelWrite, PullRequestReviewWrite,
               AddCommentToPendingReview, AddReplyToPullRequestComment, UpdatePullRequest, MergePullRequest,
               RequestCopilotReview]
TOOLS = READ_TOOLS + WRITE_TOOLS
