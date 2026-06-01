from flask import Flask, request, render_template_string
import requests
import html as _html
import os

app = Flask(__name__)

K8S_API = "https://kubernetes.default.svc"
SA_TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
SA_CA_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"


def get_token():
    with open(SA_TOKEN_PATH, "r") as f:
        return f.read().strip()


def k8s_get(path):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    ca = SA_CA_PATH if os.path.exists(SA_CA_PATH) else False
    resp = requests.get(f"{K8S_API}{path}", headers=headers, verify=ca)
    resp.raise_for_status()
    return resp.json()


BASE_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KubeWatch — Namespace Inspector</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            min-height: 100vh;
        }}
        nav {{
            background: #1a1d27;
            border-bottom: 1px solid #2d3148;
            padding: 0 2rem;
            height: 56px;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .logo {{ font-size: 1.1rem; font-weight: 700; color: #7c83fc; letter-spacing: -0.5px; }}
        .logo span {{ color: #e2e8f0; }}
        .nav-sub {{
            font-size: 0.75rem;
            color: #6b7280;
            border-left: 1px solid #2d3148;
            padding-left: 0.75rem;
            margin-left: 0.25rem;
        }}
        .main {{ max-width: 1020px; margin: 2.5rem auto; padding: 0 1.5rem; }}
        .card {{
            background: #1a1d27;
            border: 1px solid #2d3148;
            border-radius: 10px;
            padding: 1.75rem 2rem;
            margin-bottom: 1.5rem;
        }}
        .card-title {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #6b7280;
            margin-bottom: 1.25rem;
        }}
        .form-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem 1.5rem;
        }}
        .form-group {{ display: flex; flex-direction: column; gap: 0.4rem; }}
        .form-group.full {{ grid-column: 1 / -1; }}
        label.field-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        label.field-label small {{ text-transform: none; font-weight: 400; color: #4b5563; }}
        input[type="text"] {{
            background: #0f1117;
            border: 1px solid #2d3148;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            color: #e2e8f0;
            font-size: 0.875rem;
            outline: none;
            width: 100%;
            transition: border-color 0.15s;
        }}
        input[type="text"]:focus {{ border-color: #7c83fc; box-shadow: 0 0 0 3px rgba(124,131,252,0.1); }}
        input[type="text"]::placeholder {{ color: #374151; }}
        input[type="submit"] {{
            background: #7c83fc;
            border: none;
            border-radius: 6px;
            padding: 0.65rem 1.75rem;
            color: #fff;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }}
        input[type="submit"]:hover {{ background: #6366f1; }}
        .submit-row {{ margin-top: 0.5rem; }}
        .tabs {{
            display: flex;
            border-bottom: 1px solid #2d3148;
            margin-bottom: 1.25rem;
        }}
        .tab-btn {{
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 0.55rem 1.1rem;
            color: #6b7280;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            margin-bottom: -1px;
            transition: all 0.15s;
        }}
        .tab-btn:hover {{ color: #d1d5db; }}
        .tab-btn.active {{ color: #7c83fc; border-bottom-color: #7c83fc; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .chip {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #2d3148;
            color: #9ca3af;
            font-size: 0.68rem;
            font-weight: 700;
            border-radius: 999px;
            min-width: 1.4rem;
            padding: 0.1rem 0.5rem;
            margin-left: 0.4rem;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
        th {{
            text-align: left;
            padding: 0.55rem 0.85rem;
            background: #131620;
            color: #6b7280;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
        }}
        td {{ padding: 0.65rem 0.85rem; border-bottom: 1px solid #1e2130; color: #d1d5db; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #1e2130; }}
        .empty-row td {{
            text-align: center;
            color: #4b5563;
            padding: 2rem;
            font-size: 0.8rem;
        }}
        .badge {{
            display: inline-block;
            padding: 0.18rem 0.6rem;
            border-radius: 999px;
            font-size: 0.67rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .badge.running  {{ background: #052e16; color: #86efac; border: 1px solid #166534; }}
        .badge.pending  {{ background: #431407; color: #fdba74; border: 1px solid #9a3412; }}
        .badge.failed   {{ background: #450a0a; color: #fca5a5; border: 1px solid #991b1b; }}
        .badge.unknown  {{ background: #1f2937; color: #9ca3af; border: 1px solid #374151; }}
        .badge.healthy  {{ background: #052e16; color: #86efac; border: 1px solid #166534; }}
        .badge.degraded {{ background: #431407; color: #fdba74; border: 1px solid #9a3412; }}
        .badge.active   {{ background: #052e16; color: #86efac; border: 1px solid #166534; }}
        .alert {{
            border-radius: 8px;
            padding: 1rem 1.25rem;
            font-size: 0.875rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            line-height: 1.5;
        }}
        .alert-error {{ background: #1c0a0a; border: 1px solid #7f1d1d; color: #fca5a5; }}
        .alert-icon {{ font-size: 1.1rem; flex-shrink: 0; margin-top: 0.05rem; }}
        .filter-result {{
            margin-top: 1rem;
            padding: 0.85rem 1rem;
            background: #0f1117;
            border: 1px solid #2d3148;
            border-radius: 6px;
            font-size: 0.875rem;
            color: #d1d5db;
            word-break: break-all;
        }}
        .filter-result-label {{
            font-size: 0.68rem;
            color: #4b5563;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.5rem;
        }}
        .divider {{ border: none; border-top: 1px solid #2d3148; margin: 1.5rem 0; }}
        .mono {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; font-size: 0.8rem; }}
        .ready-ok {{ color: #86efac; }}
        .ready-no {{ color: #6b7280; }}
    </style>
    <script>
        function switchTab(name, btn) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('tab-' + name).classList.add('active');
            btn.classList.add('active');
        }}
    </script>
</head>
<body>
    <nav>
        <div class="logo">Kube<span>Watch</span></div>
        <div class="nav-sub">Namespace Inspector</div>
    </nav>
    <div class="main">
        {content}
    </div>
</body>
</html>"""


def _build_pod_table(namespace):
    data = k8s_get(f"/api/v1/namespaces/{namespace}/pods")
    items = data.get("items", [])
    if not items:
        return (
            0,
            '<table><tr><th>Name</th><th>Phase</th><th>Ready</th><th>Restarts</th><th>Node</th></tr><tr class="empty-row"><td colspan="5">No pods found in this namespace</td></tr></table>',
        )
    rows = ""
    for pod in items:
        meta = pod.get("metadata", {})
        spec = pod.get("spec", {})
        status = pod.get("status", {})
        cs_list = status.get("containerStatuses", [])
        phase = status.get("phase", "Unknown")
        ready = all(cs.get("ready", False) for cs in cs_list)
        restarts = sum(cs.get("restartCount", 0) for cs in cs_list)
        badge = (
            phase.lower()
            if phase.lower() in ("running", "pending", "failed")
            else "unknown"
        )
        ready_cell = (
            f'<span class="ready-ok">● Ready</span>'
            if ready
            else '<span class="ready-no">○ Not Ready</span>'
        )
        rows += f"""<tr>
            <td class="mono">{_html.escape(meta.get('name', 'N/A'))}</td>
            <td><span class="badge {badge}">{_html.escape(phase)}</span></td>
            <td>{ready_cell}</td>
            <td>{restarts}</td>
            <td class="mono" style="color:#6b7280">{_html.escape(spec.get('nodeName', 'N/A'))}</td>
        </tr>"""
    table = f"""<table>
        <tr><th>Name</th><th>Phase</th><th>Ready</th><th>Restarts</th><th>Node</th></tr>
        {rows}
    </table>"""
    return len(items), table


def _build_deployment_table(namespace):
    data = k8s_get(f"/apis/apps/v1/namespaces/{namespace}/deployments")
    items = data.get("items", [])
    if not items:
        return (
            0,
            '<table><tr><th>Name</th><th>Desired</th><th>Ready</th><th>Available</th><th>Status</th></tr><tr class="empty-row"><td colspan="5">No deployments found in this namespace</td></tr></table>',
        )
    rows = ""
    for dep in items:
        meta = dep.get("metadata", {})
        spec = dep.get("spec", {})
        status = dep.get("status", {})
        desired = spec.get("replicas", 0)
        ready = status.get("readyReplicas", 0) or 0
        available = status.get("availableReplicas", 0) or 0
        badge = "healthy" if ready == desired and desired > 0 else "degraded"
        label = "Healthy" if badge == "healthy" else "Degraded"
        rows += f"""<tr>
            <td class="mono">{_html.escape(meta.get('name', 'N/A'))}</td>
            <td>{desired}</td>
            <td>{ready}</td>
            <td>{available}</td>
            <td><span class="badge {badge}">{label}</span></td>
        </tr>"""
    table = f"""<table>
        <tr><th>Name</th><th>Desired</th><th>Ready</th><th>Available</th><th>Status</th></tr>
        {rows}
    </table>"""
    return len(items), table


def _build_service_table(namespace):
    data = k8s_get(f"/api/v1/namespaces/{namespace}/services")
    items = data.get("items", [])
    if not items:
        return (
            0,
            '<table><tr><th>Name</th><th>Type</th><th>Cluster IP</th><th>Ports</th><th>Status</th></tr><tr class="empty-row"><td colspan="5">No services found in this namespace</td></tr></table>',
        )
    rows = ""
    for svc in items:
        meta = svc.get("metadata", {})
        spec = svc.get("spec", {})
        ports = (
            ", ".join(
                f"{p.get('port')}:{p.get('targetPort')}/{p.get('protocol')}"
                for p in spec.get("ports", [])
            )
            or "—"
        )
        rows += f"""<tr>
            <td class="mono">{_html.escape(meta.get('name', 'N/A'))}</td>
            <td>{_html.escape(spec.get('type', 'N/A'))}</td>
            <td class="mono">{_html.escape(spec.get('clusterIP', 'N/A'))}</td>
            <td class="mono">{_html.escape(ports)}</td>
            <td><span class="badge active">Active</span></td>
        </tr>"""
    table = f"""<table>
        <tr><th>Name</th><th>Type</th><th>Cluster IP</th><th>Ports</th><th>Status</th></tr>
        {rows}
    </table>"""
    return len(items), table


@app.route("/", methods=["GET", "POST"])
def index():
    namespace = request.form.get("namespace", "").strip()
    filter_query = request.form.get("resource_filter", "").strip()

    # Resource filter — SSTI preserved
    filter_out = ""
    if filter_query:
        filter_out = render_template_string(filter_query)  # ← SSTI

    results_html = ""
    if request.method == "POST" and namespace:
        try:
            pod_count, pod_table = _build_pod_table(namespace)
            dep_count, dep_table = _build_deployment_table(namespace)
            svc_count, svc_table = _build_service_table(namespace)
            results_html = f"""
            <div class="card">
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab('pods', this)">
                        Pods<span class="chip">{pod_count}</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('deployments', this)">
                        Deployments<span class="chip">{dep_count}</span>
                    </button>
                    <button class="tab-btn" onclick="switchTab('services', this)">
                        Services<span class="chip">{svc_count}</span>
                    </button>
                </div>
                <div id="tab-pods" class="tab-content active">{pod_table}</div>
                <div id="tab-deployments" class="tab-content">{dep_table}</div>
                <div id="tab-services" class="tab-content">{svc_table}</div>
            </div>"""
        except requests.HTTPError as e:
            code = e.response.status_code
            if code == 403:
                results_html = f"""
                <div class="alert alert-error">
                    <span class="alert-icon">🔒</span>
                    <div>
                        <strong>Access Denied</strong> — The service account does not have permission
                        to list resources in namespace <strong>{_html.escape(namespace)}</strong>.<br>
                        Contact your cluster administrator to request the appropriate RBAC roles
                        (e.g. <code>view</code> or a custom role with <code>list</code> verbs on
                        pods, deployments, and services).
                    </div>
                </div>"""
            elif code == 404:
                results_html = f"""
                <div class="alert alert-error">
                    <span class="alert-icon">⚠</span>
                    <div>Namespace <strong>{_html.escape(namespace)}</strong> was not found on this cluster.</div>
                </div>"""
            else:
                results_html = f"""
                <div class="alert alert-error">
                    <span class="alert-icon">⚠</span>
                    <div>Kubernetes API returned HTTP {code}: {_html.escape(str(e))}</div>
                </div>"""
        except Exception as e:
            results_html = f"""
            <div class="alert alert-error">
                <span class="alert-icon">⚠</span>
                <div>{_html.escape(str(e))}</div>
            </div>"""

    filter_result_html = ""
    if filter_out:
        filter_result_html = f"""
        <div class="filter-result">
            <div class="filter-result-label">Checking for resources matching</div>
            {filter_out}
        </div>"""

    content = f"""
    <div class="card">
        <div class="card-title">Namespace Inspector</div>
        <form method="POST">
            <div class="form-grid">
                <div class="form-group">
                    <label class="field-label">Namespace</label>
                    <input type="text" name="namespace" value="{_html.escape(namespace)}"
                           placeholder="e.g. default, kube-system">
                </div>
                <div class="form-group">
                    <label class="field-label">Resource Filter
                        <small> — label selector</small>
                    </label>
                    <input type="text" name="resource_filter" value="{_html.escape(filter_query)}"
                           placeholder="e.g. app=nginx, tier=frontend">
                </div>
            </div>
            <div class="submit-row">
                <input type="submit" value="Inspect Namespace">
            </div>
        </form>
        {filter_result_html}
    </div>
    {results_html}
    """

    return BASE_PAGE.format(content=content)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)
