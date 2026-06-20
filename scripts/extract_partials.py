from pathlib import Path

root = Path(__file__).resolve().parents[1] / "src" / "company_lookup" / "templates"
lines = (root / "dashboard.html").read_text(encoding="utf-8").splitlines()
(root / "partials" / "dashboard_tabs.html").write_text("\n".join(lines[29:267]), encoding="utf-8")

alines = (root / "analysis.html").read_text(encoding="utf-8").splitlines()
(root / "partials" / "analysis_result.html").write_text("\n".join(alines[10:130]), encoding="utf-8")

rlines = (root / "result.html").read_text(encoding="utf-8").splitlines()
company_partial = "\n".join(rlines[5:246])
company_partial = company_partial.replace("url_for('dashboard'", "url_for('company.dashboard'")
company_partial = company_partial.replace("url_for('index')", "url_for('main.index')")
(root / "partials" / "company_result.html").write_text(company_partial, encoding="utf-8")

print("extracted partials")
