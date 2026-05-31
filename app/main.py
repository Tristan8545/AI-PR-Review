from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.analyzer.context_builder import build_review_context
from app.analyzer.rule_analyzer import analyze_rules
from app.ai.reviewer import DeepSeekReviewer
from app.config import get_settings
from app.demo_data.sample import sample_pr
from app.services.review_service import ReviewService


app = FastAPI(title="AI PR Review Assistant")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    settings = get_settings()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "demo_mode": settings.demo_mode or not settings.deepseek_api_key,
            "model": settings.deepseek_model,
        },
    )


@app.post("/review", response_class=HTMLResponse)
async def review(request: Request, pr_url: str = Form(""), use_demo: str | None = Form(None)):
    settings = get_settings()
    try:
        if use_demo or pr_url.strip().lower() in {"demo", ""}:
            pr = sample_pr()
            findings = analyze_rules(pr)
            context = build_review_context(pr, findings, settings.max_patch_chars)
            review_result = await DeepSeekReviewer(settings).review(pr, context, findings)
        else:
            pr, review_result = await ReviewService(settings).analyze_pr(pr_url)

        return templates.TemplateResponse(
            "result.html",
            {"request": request, "pr": pr, "review": review_result, "error": None},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(exc),
                "demo_mode": settings.demo_mode or not settings.deepseek_api_key,
                "model": settings.deepseek_model,
            },
            status_code=400,
        )

